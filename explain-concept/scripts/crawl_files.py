#!/usr/bin/env python3
"""Crawl a directory for source files.

Three modes:
  1. default         → read & return JSON {files: {path: content}, count: N}
  2. --list-only     → print one relative path per line, no content (cheap for triage)
  3. --paths-from=F  → read only the paths listed in F (one per line), return JSON
"""

import argparse
import fnmatch
import json
import os
import sys
from pathlib import Path

DEFAULT_INCLUDE = {
    "*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.go", "*.java", "*.pyi", "*.pyx",
    "*.c", "*.cc", "*.cpp", "*.h", "*.md", "*.rst", "*Dockerfile",
    "*Makefile", "*.yaml", "*.yml", "*.toml", "*.json", "*.rs", "*.rb",
    "*.swift", "*.kt", "*.scala", "*.sh", "*.bash", "*.sql",
}

DEFAULT_EXCLUDE = {
    "assets/*", "data/*", "images/*", "public/*", "static/*", "temp/*",
    "*docs/*", "*venv/*", "*.venv/*", "*test*", "*tests/*", "*examples/*",
    "*dist/*", "*build/*", "*experimental/*", "*deprecated/*", "*misc/*",
    "*legacy/*", ".git/*", ".github/*", ".next/*", ".vscode/*",
    "*obj/*", "*bin/*", "*node_modules/*", "*.log", "*.lock",
    "*.min.js", "*.min.css", "*.map", "*.pyc", "*.pyo",
    "__pycache__/*", "*.egg-info/*", "*.DS_Store",
}

MAX_FILE_SIZE = 100_000


def matches_any(path: str, patterns: set) -> bool:
    return any(
        fnmatch.fnmatch(path, p) or fnmatch.fnmatch(os.path.basename(path), p)
        for p in patterns
    )


def load_gitignore(directory: str) -> list[str]:
    gi = Path(directory) / ".gitignore"
    if not gi.exists():
        return []
    return [
        line.strip()
        for line in gi.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def is_gitignored(rel_path: str, patterns: list[str]) -> bool:
    for p in patterns:
        if fnmatch.fnmatch(rel_path, p) or fnmatch.fnmatch(rel_path, f"*/{p}"):
            return True
        if p.endswith("/") and (rel_path.startswith(p) or f"/{p}" in f"/{rel_path}"):
            return True
    return False


def discover_paths(directory: str) -> list[str]:
    directory = os.path.abspath(directory)
    gitignore = load_gitignore(directory)
    out: list[str] = []

    for root, dirs, filenames in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for filename in filenames:
            filepath = os.path.join(root, filename)
            rel = os.path.relpath(filepath, directory)
            if is_gitignored(rel, gitignore):
                continue
            if matches_any(rel, DEFAULT_EXCLUDE):
                continue
            if not matches_any(rel, DEFAULT_INCLUDE):
                continue
            try:
                if os.path.getsize(filepath) > MAX_FILE_SIZE:
                    continue
            except OSError:
                continue
            out.append(rel)

    out.sort()
    return out


def read_paths(directory: str, rel_paths: list[str]) -> dict[str, str]:
    files: dict[str, str] = {}
    directory = os.path.abspath(directory)
    for rel in rel_paths:
        fp = os.path.join(directory, rel)
        try:
            with open(fp, encoding="utf-8", errors="ignore") as f:
                files[rel] = f.read()
        except (IOError, UnicodeDecodeError):
            continue
    return files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("directory")
    ap.add_argument(
        "--list-only",
        action="store_true",
        help="print relative paths only, one per line; skip reading contents",
    )
    ap.add_argument(
        "--paths-from",
        metavar="FILE",
        help="read only the relative paths listed in FILE (one per line)",
    )
    args = ap.parse_args()

    if args.list_only and args.paths_from:
        print("--list-only and --paths-from are mutually exclusive", file=sys.stderr)
        return 2

    if args.list_only:
        for p in discover_paths(args.directory):
            print(p)
        return 0

    if args.paths_from:
        raw = Path(args.paths_from).read_text().splitlines()
        rel_paths = [line.strip() for line in raw if line.strip()]
        files = read_paths(args.directory, rel_paths)
    else:
        rel_paths = discover_paths(args.directory)
        files = read_paths(args.directory, rel_paths)

    print(json.dumps({"files": files, "count": len(files)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
