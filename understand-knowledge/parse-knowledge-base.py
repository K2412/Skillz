#!/usr/bin/env python3
"""Extract a simple Markdown source index for .knowledge-map workflows."""
from __future__ import annotations

import sys
from pathlib import Path


def first_heading(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("#"):
            return line.lstrip("#").strip() or fallback
    return fallback


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    for path in sorted(root.rglob("*.md")):
        if ".git" in path.parts or ".knowledge-map" in path.parts:
            continue
        text = path.read_text(errors="ignore")
        rel = path.relative_to(root)
        print(f"- [{first_heading(text, path.stem)}]({rel.as_posix()})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
