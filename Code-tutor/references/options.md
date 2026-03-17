# codebase-tutor — Full Option Reference

## Source (one required, mutually exclusive)
| Flag | Type | Description |
|------|------|-------------|
| `--repo URL` | string | GitHub repository URL |
| `--dir PATH` | path | Local directory path |

## Identity
| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `-n, --name NAME` | string | auto | Project name (output folder + title) |
| `-t, --token TOKEN` | string | $GITHUB_TOKEN | GitHub PAT for private repos |

## Output
| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `-o, --output DIR` | path | `./output` | Base output directory |

## File Filtering
| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `-i, --include PATTERN` | string (repeatable) | common source patterns | Glob to include |
| `-e, --exclude PATTERN` | string (repeatable) | common ignore patterns | Glob to exclude |
| `-s, --max-size BYTES` | int | 100000 | Skip files larger than this |

## LLM Options
| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--language LANG` | string | `english` | Output language |
| `--no-cache` | flag | off | Disable response caching |
| `--max-abstractions N` | int | 10 | Max chapters to generate |

## Common Exclude Patterns for JS/TS Projects
```
--exclude "**/node_modules/**"
--exclude "**/dist/**"
--exclude "**/build/**"
--exclude "**/.venv/**"
--exclude "**/migrations/**"
--exclude "**/__pycache__/**"
--exclude "*.min.js"
--exclude "*.map"
--exclude "**/staticfiles/**"
```
