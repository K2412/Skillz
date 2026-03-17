#!/usr/bin/env bash
# Wrapper that runs codebase-tutor from the PocketFlow project directory.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="/Users/kevinkab/Documents/Personal-Projects/PocketFlow-Tutorial-Codebase-Knowledge"

cd "$PROJECT_DIR"

# Load .env if present
if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  source <(grep -v '^#' .env | grep -v '^\s*$' | grep -v '[<>]')
  set +a
fi

exec uv run codebase-tutor "$@"
