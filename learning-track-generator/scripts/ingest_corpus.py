#!/usr/bin/env python3
"""Ingest a local directory corpus into normalized learning units."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "vendor",
    "dist",
    "build",
    ".next",
    ".cache",
}

PDF_EXTENSIONS = {".pdf"}
TEXT_EXTENSIONS = {".md", ".txt", ".rst"}
DATA_EXTENSIONS = {".json", ".yaml", ".yml", ".toml", ".ini"}
CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".php",
    ".go",
    ".rs",
    ".java",
    ".c",
    ".cpp",
    ".cs",
    ".rb",
    ".swift",
    ".kt",
    ".sql",
    ".sh",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest a corpus directory")
    parser.add_argument("--input-dir", required=True, help="Corpus root path")
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=2_000_000,
        help="Skip files larger than this size in bytes",
    )
    return parser.parse_args()


def detect_source_kind(path: Path) -> str | None:
    ext = path.suffix.lower()
    if ext in PDF_EXTENSIONS:
        return "pdf"
    if ext in TEXT_EXTENSIONS:
        return "text"
    if ext in DATA_EXTENSIONS:
        return "data-doc"
    if ext in CODE_EXTENSIONS:
        return "code"
    return None


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"^\[?\d{1,2}:\d{2}(?::\d{2})?\]?\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^(Speaker \d+|Host|Guest|Interviewer|Narrator):\s*", "", text, flags=re.MULTILINE)
    return text.strip()


def extract_markdown_code_blocks(text: str) -> list[str]:
    blocks = re.findall(r"```(?:[a-zA-Z0-9_+-]+)?\n(.*?)```", text, flags=re.DOTALL)
    return [block.strip() for block in blocks if block.strip()]


def extract_pdf_text(path: Path) -> tuple[str, str | None]:
    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(str(path))
        text_parts = [(page.extract_text() or "") for page in reader.pages]
        return "\n\n".join(text_parts), None
    except Exception:
        pass

    if not shutil_which("pdftotext"):
        return "", "No PDF extractor available (install pypdf or pdftotext)"

    try:
        result = subprocess.run(
            ["pdftotext", str(path), "-"],
            check=True,
            text=True,
            capture_output=True,
        )
        return result.stdout, None
    except subprocess.CalledProcessError as exc:
        return "", f"pdftotext failed: {exc}"


def shutil_which(command: str) -> str | None:
    result = subprocess.run(["which", command], text=True, capture_output=True)
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def read_text_file(path: Path) -> tuple[str, str | None]:
    try:
        return path.read_text(encoding="utf-8", errors="ignore"), None
    except Exception as exc:  # noqa: BLE001
        return "", f"Read failed: {exc}"


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def main() -> int:
    args = parse_args()

    input_dir = Path(args.input_dir).resolve()
    output_path = Path(args.output).resolve()

    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Input directory does not exist: {input_dir}", file=sys.stderr)
        return 2

    units: list[dict] = []
    skipped_files: list[dict] = []
    warnings: list[str] = []
    source_kind_counts: dict[str, int] = {}

    for path in input_dir.rglob("*"):
        if path.is_dir():
            continue

        rel_parts = path.relative_to(input_dir).parts
        if any(part.startswith(".") for part in rel_parts):
            skipped_files.append({"path": str(path.relative_to(input_dir)), "reason": "Hidden path"})
            continue
        if any(part in SKIP_DIRS for part in rel_parts):
            skipped_files.append({"path": str(path.relative_to(input_dir)), "reason": "Skipped directory"})
            continue

        if path.stat().st_size > args.max_bytes:
            skipped_files.append({"path": str(path.relative_to(input_dir)), "reason": "File too large"})
            continue

        source_kind = detect_source_kind(path)
        if source_kind is None:
            skipped_files.append({"path": str(path.relative_to(input_dir)), "reason": "Unsupported extension"})
            continue

        if source_kind == "pdf":
            raw_text, err = extract_pdf_text(path)
            code_blocks: list[str] = []
        else:
            raw_text, err = read_text_file(path)
            code_blocks = extract_markdown_code_blocks(raw_text) if path.suffix.lower() == ".md" else []

        if err:
            warnings.append(f"{path.relative_to(input_dir)}: {err}")
            if not raw_text:
                skipped_files.append({"path": str(path.relative_to(input_dir)), "reason": err})
                continue

        normalized_text = normalize_text(raw_text)
        if not normalized_text:
            skipped_files.append({"path": str(path.relative_to(input_dir)), "reason": "No extracted text"})
            continue

        unit = {
            "source_path": str(path),
            "relative_path": str(path.relative_to(input_dir)),
            "source_kind": source_kind,
            "title_hint": path.stem.replace("_", " ").replace("-", " ").strip(),
            "language_hint": path.suffix.lower().lstrip("."),
            "normalized_text": normalized_text,
            "code_blocks": code_blocks[:10],
            "metadata": {
                "size_bytes": path.stat().st_size,
                "token_estimate": estimate_tokens(normalized_text),
            },
        }
        units.append(unit)
        source_kind_counts[source_kind] = source_kind_counts.get(source_kind, 0) + 1

    if not units:
        print("No ingestible content found. Check directory and supported types.", file=sys.stderr)
        return 3

    payload = {
        "input_dir": str(input_dir),
        "summary": {
            "total_units": len(units),
            "source_kind_counts": source_kind_counts,
            "total_token_estimate": sum(u["metadata"]["token_estimate"] for u in units),
        },
        "units": units,
        "skipped_files": skipped_files,
        "warnings": warnings,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote ingestion payload to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
