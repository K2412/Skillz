#!/usr/bin/env python3
"""Lightweight helper for Markdown knowledge-map domain extraction.

This script prints candidate domain terms from Markdown/source text. It does not
read or write graph artifacts.
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

WORD = re.compile(r"\b[A-Z][A-Za-z0-9_]{2,}\b")


def iter_files(root: Path):
    for path in root.rglob("*"):
        if path.is_file() and ".git" not in path.parts and "node_modules" not in path.parts:
            if path.suffix.lower() in {".md", ".py", ".js", ".ts", ".tsx", ".php", ".rb", ".go", ".rs", ".java"}:
                yield path


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    counts: Counter[str] = Counter()
    for path in iter_files(root):
        try:
            counts.update(WORD.findall(path.read_text(errors="ignore")[:20000]))
        except OSError:
            pass
    for term, count in counts.most_common(100):
        print(f"{term}\t{count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
