# Ingestion Rules

## Input Model

- Accept one required `--input-dir`.
- Scan recursively.
- Build one `IngestionUnit` per supported file.

## Supported Sources

- PDF: `.pdf`
- Transcript/docs text: `.md`, `.txt`, `.rst`
- Code: `.py`, `.js`, `.ts`, `.tsx`, `.php`, `.go`, `.rs`, `.java`, `.c`, `.cpp`, `.cs`, `.rb`, `.swift`, `.kt`, `.sql`, `.sh`
- Data-like docs: `.json`, `.yaml`, `.yml`, `.toml`, `.ini`

## Skip Behavior

- Skip hidden directories and common dependency/build folders:
  - `.git`, `.hg`, `.svn`, `node_modules`, `vendor`, `dist`, `build`, `.next`, `.cache`
- Skip files over `--max-bytes`.
- Skip binary/unsupported extensions.
- Record each skip reason in `skipped_files`.

## Normalization

- Normalize line endings to `\n`.
- Collapse repeated spaces and 3+ blank lines.
- For transcript-like text, remove timestamps and simple speaker labels.
- Extract fenced code blocks from markdown for exercise seed generation.

## Failure Policy

- Per-file extraction failures become warnings.
- Return non-zero only when no usable content is ingested.
