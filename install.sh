#!/usr/bin/env bash
# Installs all skills to ~/.agents/skills/ (the source-of-truth) and
# symlinks them into ~/.claude/skills/ and ~/.codex/skills/ so that
# Claude Code and Codex CLI both pick them up. Tool dirs that don't
# exist on this machine are skipped silently.
#
# Override the source-of-truth location with AGENTS_HOME if needed.
set -euo pipefail

AGENTS_DIR="${AGENTS_HOME:-$HOME/.agents}/skills"
mkdir -p "$AGENTS_DIR"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Tool dirs to symlink into, if present. Add more as new CLIs adopt skills.
TOOL_DIRS=(
  "$HOME/.claude/skills"
  "$HOME/.codex/skills"
)

installed=0
linked=0
for skill_dir in "$SCRIPT_DIR"/*/; do
  name=$(basename "$skill_dir")
  [[ -f "$skill_dir/SKILL.md" ]] || continue

  # Replace any prior copy so removed files don't linger.
  if [ -e "$AGENTS_DIR/$name" ]; then
    find "$AGENTS_DIR/$name" -depth -delete
  fi
  cp -r "$skill_dir" "$AGENTS_DIR/$name"
  echo "Installed: $name"
  installed=$((installed + 1))

  # Create a symlink in each tool dir that exists on this machine.
  for tool_dir in "${TOOL_DIRS[@]}"; do
    [ -d "$tool_dir" ] || continue
    link="$tool_dir/$name"
    # `ln -sfn` overwrites an existing symlink in place. If a real
    # directory is sitting there from an older install, take it down
    # first so the link can be created cleanly.
    if [ -d "$link" ] && [ ! -L "$link" ]; then
      find "$link" -depth -delete
    fi
    ln -sfn "$AGENTS_DIR/$name" "$link"
    echo "          linked: $link -> $AGENTS_DIR/$name"
    linked=$((linked + 1))
  done
done

echo ""
echo "Done. $installed skill(s) installed to $AGENTS_DIR."
if [ "$linked" -gt 0 ]; then
  echo "      $linked symlink(s) created across tool dirs."
else
  echo "      No tool dirs found (~/.claude/skills, ~/.codex/skills)."
fi
echo "Restart Claude Code or Codex to pick up new skills."
