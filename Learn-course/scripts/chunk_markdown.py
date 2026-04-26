#!/usr/bin/env python3
"""Split a markdown file into chapter-sized chunks for lesson generation.

Port of the Personal-Learning-Platform `ChunkContentAction`. Pure text
processing — no LLM call. Stdout is JSON: {"chunks": [{"index", "title",
"content", "token_estimate"}]}.

Patterns and size constants intentionally mirror the source action so chunks
look the same as on the web platform.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TARGET_CHUNK_SIZE = 16_000
LARGE_CHUNK_RATIO = 1.5  # chunks above TARGET * 1.5 get sub-split

# The source platform's ChunkContentAction merged sub-4KB chapters into the
# previous chunk to save on backend LLM calls. This skill drops that merge:
# preserving chapter structure is more valuable than the call savings, and one
# extra subagent per chapter is a cheap trade.

# Patterns are tried in order. The first that yields >= 2 chapter splits wins.
# H1 is tried before H2 — if a doc has both, H1 chapters are the right grain
# and H2s are subsections. Falling through to H2 only happens for docs that use
# H2 as their top-level heading style.
SPLIT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^(Chapter\s+\d+[.:]\s*.+)$", re.MULTILINE | re.IGNORECASE), "chapter"),
    (re.compile(r"^(#\s+.+)$", re.MULTILINE), "h1"),
    (re.compile(r"^(Part\s+\d+[.:]\s*.+)$", re.MULTILINE | re.IGNORECASE), "part"),
    (re.compile(r"^(Section\s+\d+[.:]\s*.+)$", re.MULTILINE | re.IGNORECASE), "section"),
    (re.compile(r"^(\d+\.\s+[A-Z].+)$", re.MULTILINE), "numbered-section"),
    (re.compile(r"^(##\s+.+)$", re.MULTILINE), "h2"),
]

HEADING_RE = re.compile(
    r"(?:^Chapter\s+\d+)|(?:^#{1,2}\s+)|(?:^\d+\.\s+[A-Z])|(?:^Part\s+\d+)|(?:^Section\s+\d+)",
    re.IGNORECASE,
)


def estimate_tokens(text: str) -> int:
    return -(-len(text) // 4)  # ceil(len/4)


def split_by_chapters(content: str) -> list[dict[str, str | None]]:
    """Try each pattern; return [{title, content}, ...] when one splits the doc."""
    for pattern, _name in SPLIT_PATTERNS:
        # PREG_SPLIT_DELIM_CAPTURE | NO_EMPTY equivalent: split keeping the heading,
        # then walk the parts pairing heading -> body.
        parts = pattern.split(content)
        parts = [p for p in parts if p and p.strip()]
        if len(parts) >= 3:
            return _pair_titles_with_content(parts)
    return [{"title": None, "content": content}]


def _pair_titles_with_content(parts: list[str]) -> list[dict[str, str | None]]:
    chunks: list[dict[str, str | None]] = []
    current_title: str | None = None
    current_body: list[str] = []

    for part in parts:
        stripped = part.strip()
        if HEADING_RE.match(stripped):
            if current_body:
                body = "".join(current_body).strip()
                if body:
                    chunks.append({"title": current_title, "content": body})
            current_title = stripped
            current_body = []
        else:
            current_body.append(part)

    if current_body:
        body = "".join(current_body).strip()
        if body:
            chunks.append({"title": current_title, "content": body})

    return chunks


def split_by_size(content: str, base_title: str | None = None) -> list[dict[str, object]]:
    chunks: list[dict[str, object]] = []
    paragraphs = re.split(r"\n{2,}", content)
    current = ""
    part_num = 1

    for raw in paragraphs:
        para = raw.strip()
        if not para:
            continue
        candidate = para if not current else f"{current}\n\n{para}"
        if len(candidate) > TARGET_CHUNK_SIZE and current:
            title = f"{base_title} (Part {part_num})" if base_title else None
            chunks.append({
                "title": title,
                "content": current,
                "token_estimate": estimate_tokens(current),
            })
            current = para
            part_num += 1
        else:
            current = candidate

    if current:
        title = (
            f"{base_title} (Part {part_num})"
            if base_title is not None and part_num > 1
            else base_title
        )
        chunks.append({
            "title": title,
            "content": current,
            "token_estimate": estimate_tokens(current),
        })

    return chunks


def process_chapter_chunks(raw: list[dict[str, str | None]]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for chunk in raw:
        body = chunk["content"] or ""
        title = chunk["title"]
        size = len(body)

        if size > TARGET_CHUNK_SIZE * LARGE_CHUNK_RATIO:
            # Too big — sub-split. Sub-splits keep the chapter title as a base.
            for sub in split_by_size(body, title):
                result.append(sub)
        else:
            # Keep every detected chapter as its own chunk, even if small —
            # losing chapter structure is worse than spending one cheap subagent.
            result.append({
                "title": title,
                "content": body,
                "token_estimate": estimate_tokens(body),
            })

    return result


def chunk_content(content: str) -> list[dict[str, object]]:
    chapter_chunks = split_by_chapters(content)
    if len(chapter_chunks) > 1:
        chunks = process_chapter_chunks(chapter_chunks)
    else:
        chunks = split_by_size(content)
    # Add stable indexes
    for i, c in enumerate(chunks):
        c["index"] = i
    return chunks


def main() -> int:
    parser = argparse.ArgumentParser(description="Chunk a markdown file by chapter for lesson generation.")
    parser.add_argument("input", type=Path, help="Path to the .md source file")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"error: input file not found: {args.input}", file=sys.stderr)
        return 1

    content = args.input.read_text(encoding="utf-8")
    if not content.strip():
        print("error: input file is empty", file=sys.stderr)
        return 1

    chunks = chunk_content(content)
    json.dump({"chunks": chunks}, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
