#!/usr/bin/env python3
"""Build a unified course payload from ingestion output."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build course payload from ingestion JSON")
    parser.add_argument("--ingestion", required=True, help="Path to ingestion JSON")
    parser.add_argument("--output", required=True, help="Output payload JSON path")
    parser.add_argument("--title", default="", help="Optional override title")
    parser.add_argument("--language", default="mixed", help="Primary language")
    return parser.parse_args()


def sentence_snippet(text: str, max_len: int = 200) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    return compact[:max_len].rstrip()


def module_title(bucket: str) -> str:
    if bucket == "root":
        return "Core Concepts"
    title = bucket.replace("_", " ").replace("-", " ").strip()
    return title.title()


def objective_for_unit(source_kind: str, title_hint: str) -> str:
    if source_kind == "code":
        return f"Implement and reason about {title_hint} through working code examples."
    if source_kind == "pdf":
        return f"Understand core concepts from {title_hint} and apply them in practice."
    if source_kind == "data-doc":
        return f"Interpret configuration and structured docs from {title_hint}."
    return f"Explain and apply ideas from {title_hint}."


def exercise_seed(unit: dict) -> str:
    title = unit.get("title_hint", "the source material")
    kind = unit.get("source_kind", "text")
    if kind == "code":
        return f"Write a small program that recreates the main behavior from {title}."
    if kind == "pdf":
        return f"Summarize the key pattern from {title} and implement a minimal example."
    return f"Create a practical exercise based on the concepts from {title}."


def group_bucket(relative_path: str) -> str:
    parts = Path(relative_path).parts
    if len(parts) <= 1:
        return "root"
    return parts[0]


def main() -> int:
    args = parse_args()
    ingestion_path = Path(args.ingestion).resolve()
    output_path = Path(args.output).resolve()

    if not ingestion_path.exists():
        print(f"Ingestion file not found: {ingestion_path}", file=sys.stderr)
        return 2

    payload = json.loads(ingestion_path.read_text(encoding="utf-8"))
    units = payload.get("units", [])
    if not units:
        print("Ingestion payload has no units.", file=sys.stderr)
        return 3

    grouped: dict[str, list[dict]] = defaultdict(list)
    for unit in units:
        grouped[group_bucket(unit["relative_path"])].append(unit)

    modules: list[dict] = []
    for bucket, bucket_units in sorted(grouped.items(), key=lambda x: x[0]):
        objectives = []
        source_files = []
        prompts = []
        content_snippets = []

        for unit in bucket_units:
            objectives.append(objective_for_unit(unit["source_kind"], unit["title_hint"]))
            source_files.append(unit["relative_path"])
            prompts.append(exercise_seed(unit))
            content_snippets.append(sentence_snippet(unit["normalized_text"], max_len=140))

        modules.append(
            {
                "title": module_title(bucket),
                "learning_objectives": sorted(set(objectives))[:6],
                "source_files": source_files,
                "recommended_exercise_prompts": sorted(set(prompts))[:8],
                "context_snippets": content_snippets[:8],
            }
        )

    source_counts = payload.get("summary", {}).get("source_kind_counts", {})
    default_title = f"Unified Course from {Path(payload.get('input_dir', 'Corpus')).name}"
    course_title = args.title or default_title
    summary = (
        f"This course is generated from a mixed local corpus with {len(units)} source files "
        f"across {len(source_counts)} source types."
    )

    course_payload = {
        "title": course_title,
        "language": args.language,
        "summary": summary,
        "modules": modules,
        "source_stats": {
            "total_units": len(units),
            "source_kind_counts": source_counts,
            "total_token_estimate": payload.get("summary", {}).get("total_token_estimate", 0),
            "warnings_count": len(payload.get("warnings", [])),
            "skipped_count": len(payload.get("skipped_files", [])),
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(course_payload, indent=2), encoding="utf-8")
    print(f"Wrote course payload to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
