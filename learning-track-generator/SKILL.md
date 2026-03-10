---
name: learning-track-generator
description: Generate a text-based programming course from a local directory corpus containing mixed files (PDFs, markdown/text transcripts, docs, and source code). Use when a user wants boot.dev-style learning tracks from folder contents, including ingestion, normalization, course payload building, and lesson/exercise planning.
---

# Learning Track Generator

Use this skill to transform a local corpus directory into one unified course payload.

## Workflow

1. Run `scripts/ingest_corpus.py --input-dir <path> --output ./.tmp/ingestion.json`.
2. Review skipped files and warnings in the ingestion output.
3. Run `scripts/build_course_payload.py --ingestion ./.tmp/ingestion.json --output ./.tmp/course_payload.json`.
4. Use the payload as the source of truth for downstream lesson/exercise generation.

See [Ingestion Rules](references/ingestion.md), [Generation Workflow](references/workflow.md), and [Quality Bar](references/quality.md).

## Operating Rules

- Treat input as a local corpus, not as a Git repository workflow.
- Default to one unified course for the full directory.
- Recurse through subdirectories.
- Skip unsupported binaries and record skip reasons.
- Keep extraction failures non-fatal unless no ingestible text remains.

## CLI Quick Start

```bash
mkdir -p .tmp

python3 scripts/ingest_corpus.py \
  --input-dir /path/to/corpus \
  --output ./.tmp/ingestion.json

python3 scripts/build_course_payload.py \
  --ingestion ./.tmp/ingestion.json \
  --title "Practical Course" \
  --language python \
  --output ./.tmp/course_payload.json
```

## Output Contract

`build_course_payload.py` emits JSON with:

- `title`
- `language`
- `summary`
- `modules[]`
- `source_stats`

Each module includes:

- `title`
- `learning_objectives[]`
- `source_files[]`
- `recommended_exercise_prompts[]`

Use this payload to guide the final generated track structure.
