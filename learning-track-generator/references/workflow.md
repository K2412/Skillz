# Generation Workflow

1. Run corpus ingestion to create `ingestion.json`.
2. Verify `summary.total_units > 0`.
3. Review:
   - `summary.source_kind_counts`
   - `skipped_files`
   - `warnings`
4. Build course payload from ingestion.
5. Feed payload modules into lesson/exercise generation.

## Payload Intent

- `summary`: quick context for model setup.
- `modules`: coherent chunks for lesson planning.
- `recommended_exercise_prompts`: deterministic exercise seeds from source files.

## Extension Points

- Add source adapters by extending `detect_source_kind` and extractors in `ingest_corpus.py`.
- Add module heuristics in `build_course_payload.py` without changing ingestion output shape.
