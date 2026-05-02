#!/usr/bin/env python3
"""Index a GitHub repo (or local clone) so the matchmaker subagent can decide
which files are relevant to each lesson chunk.

Input is either:
- A GitHub URL (https://github.com/owner/repo, git@github.com:owner/repo.git, or
  the short owner/repo form) — we shell out to `gh repo clone` (preferred) or
  `git clone` into a temp directory under /tmp.
- A local filesystem path to an already-cloned working tree.

Output is JSON to stdout:
{
  "root": "<absolute path on disk>",
  "language": "<the user-chosen target language, lowercased>",
  "tree": "<truncated `find`-style listing>",
  "files": [
    {"path": "src/foo.py", "size_bytes": 1234, "lines": 56, "head": "first ~30 lines"},
    ...
  ],
  "skipped": {"oversize": N, "binary": M, "extension_filter": K}
}

The matchmaker subagent reads this and returns `{chunk_index: [path, ...]}`
mapping each lesson chunk to a small list of files. We do NOT dump every file's
full contents here — that would defeat the point. The `head` preview is enough
for the matchmaker to recognize what each file is about; the per-lesson
subagent then reads the matched files in full.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Per-language file extensions. The matchmaker cares mostly about source files
# in the target language plus a few universal config/doc files. We index
# everything the language pulls in so the subagent has context, but we never
# ship build artifacts or dependency trees.
LANGUAGE_EXTENSIONS: dict[str, set[str]] = {
    "python": {".py", ".pyi", ".pyx"},
    "javascript": {".js", ".mjs", ".cjs", ".jsx"},
    "typescript": {".ts", ".tsx", ".js", ".mjs", ".cjs", ".d.ts"},
    "go": {".go"},
    "rust": {".rs"},
    "ruby": {".rb"},
    "java": {".java"},
    "kotlin": {".kt", ".kts"},
    "swift": {".swift"},
    "c": {".c", ".h"},
    "cpp": {".cc", ".cpp", ".cxx", ".hh", ".hpp", ".h"},
    "csharp": {".cs"},
    "php": {".php"},
    "terraform": {".tf", ".tfvars", ".hcl"},
    "hcl": {".tf", ".tfvars", ".hcl"},
}

# Always include these regardless of language — they describe the project.
ALWAYS_INCLUDE_NAMES = {
    "README.md", "README", "README.rst",
    "LICENSE", "LICENSE.md", "LICENSE.txt",
    "package.json", "pyproject.toml", "setup.py", "setup.cfg",
    "Cargo.toml", "go.mod", "Gemfile", "composer.json",
    "tsconfig.json", "Makefile", "CMakeLists.txt",
}
ALWAYS_INCLUDE_EXTS = {".md"}  # in-repo docs often explain architecture

# Skip these directories outright. Anything under them is dependency code,
# build output, or VCS metadata — not what the lessons should ground on.
SKIP_DIRS = {
    ".git", ".hg", ".svn",
    "node_modules", "bower_components",
    "vendor", "third_party", "deps",
    "build", "dist", "out", "target", "bin", "obj",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".venv", "venv", "env", ".env",
    ".next", ".nuxt", ".svelte-kit", ".turbo", ".cache",
    "coverage", ".nyc_output",
}

MAX_FILE_BYTES = 200_000  # skip anything larger; lesson grounding doesn't need huge files
HEAD_LINES = 30  # how many lines of preview the matchmaker sees per file
MAX_FILES = 500  # hard cap; bigger repos get truncated with a warning
TREE_MAX_LINES = 400  # tree listing budget


GITHUB_URL_RE = re.compile(
    r"^(?:https?://github\.com/|git@github\.com:)([\w.-]+)/([\w.-]+?)(?:\.git)?/?$"
)
SHORT_FORM_RE = re.compile(r"^([\w.-]+)/([\w.-]+)$")


def is_github_url(s: str) -> bool:
    return bool(GITHUB_URL_RE.match(s) or SHORT_FORM_RE.match(s))


def clone_repo(url_or_short: str) -> Path:
    """Clone into a stable /tmp path keyed on owner/repo so re-running the
    indexer reuses the existing checkout. The caller can pass --refresh to
    force a fresh clone."""
    m = GITHUB_URL_RE.match(url_or_short) or SHORT_FORM_RE.match(url_or_short)
    if not m:
        raise ValueError(f"not a recognized GitHub URL or short form: {url_or_short}")
    owner, repo = m.group(1), m.group(2)
    dest = Path(tempfile.gettempdir()) / "learn-course-repos" / f"{owner}__{repo}"
    if dest.exists():
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)

    full_url = (
        url_or_short
        if url_or_short.startswith(("http", "git@"))
        else f"https://github.com/{owner}/{repo}.git"
    )

    # Prefer gh (handles auth, private repos). Fall back to git clone.
    cmd: list[str]
    if shutil.which("gh"):
        cmd = ["gh", "repo", "clone", f"{owner}/{repo}", str(dest), "--", "--depth", "1"]
    elif shutil.which("git"):
        cmd = ["git", "clone", "--depth", "1", full_url, str(dest)]
    else:
        raise RuntimeError("neither `gh` nor `git` is on PATH; cannot clone")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"clone failed (exit {result.returncode}): {result.stderr.strip() or result.stdout.strip()}"
        )
    return dest


def is_binary(path: Path) -> bool:
    try:
        with path.open("rb") as f:
            chunk = f.read(8192)
        if b"\x00" in chunk:
            return True
        # Heuristic: many non-printable bytes => binary.
        if not chunk:
            return False
        printable = sum(c < 128 and (c >= 32 or c in (9, 10, 13)) for c in chunk)
        return (printable / len(chunk)) < 0.85
    except OSError:
        return True


def should_skip_dir(name: str) -> bool:
    return name in SKIP_DIRS or name.startswith(".") and name not in {".github"}


def file_is_relevant(path: Path, allowed_exts: set[str]) -> bool:
    if path.name in ALWAYS_INCLUDE_NAMES:
        return True
    if path.suffix in ALWAYS_INCLUDE_EXTS:
        return True
    return path.suffix in allowed_exts


def read_head(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            lines: list[str] = []
            for i, line in enumerate(f):
                if i >= HEAD_LINES:
                    break
                lines.append(line)
            return "".join(lines)
    except OSError:
        return ""


def walk_repo(root: Path, language: str) -> tuple[list[dict[str, object]], dict[str, int], list[str]]:
    allowed_exts = LANGUAGE_EXTENSIONS.get(language.lower(), set())
    if not allowed_exts:
        # Unknown language — fall back to language-agnostic sweep (configs + .md only).
        # This is intentional: better to ship a thin index than guess wrong extensions.
        allowed_exts = set()

    files: list[dict[str, object]] = []
    skipped = {"oversize": 0, "binary": 0, "extension_filter": 0}
    tree_lines: list[str] = []

    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = Path(dirpath).relative_to(root)
        # Mutate dirnames in place to prune the walk.
        dirnames[:] = sorted(d for d in dirnames if not should_skip_dir(d))
        if str(rel_dir) != ".":
            tree_lines.append(f"{rel_dir}/")

        for fname in sorted(filenames):
            if fname.startswith("."):
                continue
            fpath = Path(dirpath) / fname
            rel = fpath.relative_to(root)

            if not file_is_relevant(fpath, allowed_exts):
                skipped["extension_filter"] += 1
                continue
            try:
                size = fpath.stat().st_size
            except OSError:
                continue
            if size > MAX_FILE_BYTES:
                skipped["oversize"] += 1
                continue
            if is_binary(fpath):
                skipped["binary"] += 1
                continue

            head = read_head(fpath)
            line_count = head.count("\n") + (0 if head.endswith("\n") or not head else 1)
            files.append({
                "path": str(rel),
                "size_bytes": size,
                "lines": line_count,
                "head": head,
            })
            tree_lines.append(f"  {rel}")

            if len(files) >= MAX_FILES:
                tree_lines.append(f"... (file cap {MAX_FILES} reached, remaining files omitted)")
                return files, skipped, tree_lines

    return files, skipped, tree_lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Index a GitHub repo or local checkout for lesson grounding.")
    parser.add_argument(
        "source",
        help="GitHub URL (https or ssh), short form (owner/repo), or local path to a working tree.",
    )
    parser.add_argument(
        "--language",
        required=True,
        help="Target programming language (must match what was chosen in Step 1). "
             "Drives file-extension filtering.",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="If `source` is a URL, delete the cached clone first and re-clone.",
    )
    args = parser.parse_args()

    src = args.source
    if is_github_url(src):
        if args.refresh:
            m = GITHUB_URL_RE.match(src) or SHORT_FORM_RE.match(src)
            if m:
                cached = Path(tempfile.gettempdir()) / "learn-course-repos" / f"{m.group(1)}__{m.group(2)}"
                if cached.exists():
                    shutil.rmtree(cached)
        try:
            root = clone_repo(src)
        except (RuntimeError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
    else:
        root = Path(src).expanduser().resolve()
        if not root.is_dir():
            print(f"error: not a directory: {root}", file=sys.stderr)
            return 1

    files, skipped, tree_lines = walk_repo(root, args.language)

    if not files:
        print(
            f"error: indexed 0 relevant files under {root} for language={args.language!r}. "
            f"skipped={skipped}",
            file=sys.stderr,
        )
        return 1

    if len(tree_lines) > TREE_MAX_LINES:
        tree_lines = tree_lines[:TREE_MAX_LINES] + [f"... (tree truncated at {TREE_MAX_LINES} lines)"]

    out = {
        "root": str(root),
        "language": args.language.lower(),
        "tree": "\n".join(tree_lines),
        "files": files,
        "skipped": skipped,
    }
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
