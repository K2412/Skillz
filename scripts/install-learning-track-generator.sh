#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="${ROOT_DIR}/learning-track-generator"
DST_DIR="/Users/kevinkab/.agents/skills/learning-track-generator"

if [[ ! -d "${SRC_DIR}" ]]; then
  echo "Source skill folder missing: ${SRC_DIR}" >&2
  exit 1
fi

if [[ ! -f "${SRC_DIR}/SKILL.md" ]]; then
  echo "SKILL.md missing in source skill folder" >&2
  exit 1
fi

mkdir -p "$(dirname "${DST_DIR}")"
rsync -a --delete "${SRC_DIR}/" "${DST_DIR}/"

if [[ ! -f "${DST_DIR}/SKILL.md" ]]; then
  echo "Install verification failed: SKILL.md not found at destination" >&2
  exit 1
fi

echo "Installed learning-track-generator to ${DST_DIR}"
echo "Restart Codex to pick up new skills."
