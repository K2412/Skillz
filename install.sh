#!/usr/bin/env bash
# Restores all skills to ~/.agents/skills/ (or $AGENTS_HOME/skills)
set -euo pipefail

SKILLS_DIR="${AGENTS_HOME:-$HOME/.agents}/skills"
mkdir -p "$SKILLS_DIR"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

installed=0
for skill_dir in "$SCRIPT_DIR"/*/; do
  name=$(basename "$skill_dir")
  [[ -f "$skill_dir/SKILL.md" ]] || continue
  cp -r "$skill_dir" "$SKILLS_DIR/$name"
  echo "Installed: $name"
  ((installed++))
done

echo ""
echo "Done. $installed skill(s) installed to $SKILLS_DIR"
echo "Restart Claude Code to pick up new skills."
