#!/usr/bin/env python3
"""Slice a markdown source file using LLM-decided line-range boundaries.

Input: the original .md path + a JSON file (or stdin) containing
`{"chunks": [{"title", "start_line", "end_line", "rationale"}, ...]}` as
returned by the smart-chunker subagent (see references/chunking-prompt.md).

Output: stdout JSON in the same shape produced by chunk_markdown.py — namely
`{"chunks": [{"index", "title", "content", "token_estimate"}, ...]}` — so that
generate-mode Step 3 (lesson generation) is agnostic to which chunker ran.

Validation rules (kept strict on purpose — a bad chunker output would silently
corrupt the course):

- start_line >= 1, end_line <= total lines.
- start_line <= end_line for every chunk.
- Chunks cover the file with no gaps and no overlaps.
- At least one chunk; first starts at 1, last ends at last line.

If validation fails, exit non-zero with a clear message so the orchestrator can
fall back to chunk_markdown.py.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def estimate_tokens(text: str) -> int:
    return -(-len(text) // 4)  # ceil(len/4)


def load_boundaries(path: Path | None) -> list[dict[str, object]]:
    raw = path.read_text(encoding="utf-8") if path else sys.stdin.read()
    data = json.loads(raw)
    if not isinstance(data, dict) or "chunks" not in data:
        raise ValueError("boundaries JSON must be an object with a 'chunks' key")
    chunks = data["chunks"]
    if not isinstance(chunks, list) or not chunks:
        raise ValueError("boundaries 'chunks' must be a non-empty list")
    return chunks


def validate(chunks: list[dict[str, object]], total_lines: int) -> None:
    prev_end = 0
    for i, c in enumerate(chunks):
        try:
            start = int(c["start_line"])
            end = int(c["end_line"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"chunk {i}: missing/invalid start_line or end_line ({exc})") from exc
        if start < 1 or end > total_lines:
            raise ValueError(f"chunk {i}: range {start}-{end} out of bounds (file has {total_lines} lines)")
        if start > end:
            raise ValueError(f"chunk {i}: start_line {start} > end_line {end}")
        if start != prev_end + 1:
            raise ValueError(
                f"chunk {i}: start_line {start} does not follow previous end_line {prev_end} contiguously"
            )
        prev_end = end
    if prev_end != total_lines:
        raise ValueError(f"last chunk ends at line {prev_end}, expected {total_lines}")


def slice_chunks(lines: list[str], chunks: list[dict[str, object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for i, c in enumerate(chunks):
        start = int(c["start_line"])
        end = int(c["end_line"])
        body = "".join(lines[start - 1 : end])  # inclusive
        title = c.get("title")
        if title is not None and not isinstance(title, str):
            title = str(title)
        out.append({
            "index": i,
            "title": title,
            "content": body,
            "token_estimate": estimate_tokens(body),
        })
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Slice a markdown file using LLM-returned line-range boundaries."
    )
    parser.add_argument("input", type=Path, help="Path to the .md source file")
    parser.add_argument(
        "--boundaries",
        type=Path,
        default=None,
        help="Path to boundaries JSON. If omitted, read from stdin.",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"error: input file not found: {args.input}", file=sys.stderr)
        return 1

    text = args.input.read_text(encoding="utf-8")
    if not text.strip():
        print("error: input file is empty", file=sys.stderr)
        return 1

    # splitlines(keepends=True) preserves trailing newlines so reassembled chunks
    # match the original byte-for-byte (no merging of "Foo\n" + "Bar\n" -> "FooBar").
    lines = text.splitlines(keepends=True)

    try:
        chunks_in = load_boundaries(args.boundaries)
        validate(chunks_in, len(lines))
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"error: invalid boundaries: {exc}", file=sys.stderr)
        return 2  # distinct exit code so orchestrator can detect "fall back to deterministic"

    chunks_out = slice_chunks(lines, chunks_in)
    json.dump({"chunks": chunks_out}, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
