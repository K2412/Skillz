#!/usr/bin/env bash
# Installs all skills to ~/.agents/skills/ (the source-of-truth),
# regenerates ~/.agents/AGENTS.md and ~/.claude/CLAUDE.md (symlink) so Claude
# Code and OpenCode always reflect the current skill set,
# installs orchestrator-only instruction modules to ~/.pi/agent/instructions/,
# installs Pi extensions to ~/.pi/agent/extensions/, and symlinks skills into
# ~/.claude/skills/ and ~/.codex/skills/ so those CLIs pick them up. Tool dirs
# that don't exist on this machine are skipped silently.
#
# Override the source-of-truth location with AGENTS_HOME if needed.
set -euo pipefail

AGENTS_HOME_DIR="${AGENTS_HOME:-$HOME/.agents}"
AGENTS_DIR="$AGENTS_HOME_DIR/skills"
PI_INSTRUCTIONS_DIR="${PI_HOME:-$HOME/.pi/agent}/instructions"
PI_EXTENSIONS_DIR="${PI_HOME:-$HOME/.pi/agent}/extensions"
mkdir -p "$AGENTS_DIR" "$PI_INSTRUCTIONS_DIR" "$PI_EXTENSIONS_DIR"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Pull the `description:` out of a SKILL.md frontmatter block. Handles plain
# scalars, quoted scalars, and folded/literal blocks (`description: >`), which
# a naive one-line grab renders as a bare ">".
skill_description() {
  awk '
    NR == 1 && $0 !~ /^---[[:space:]]*$/ { in_fm = 1 }
    NR == 1 && $0 ~ /^---[[:space:]]*$/  { in_fm = 1; next }
    in_fm && !collecting && $0 ~ /^---[[:space:]]*$/ { exit }
    !in_fm { next }
    !collecting && $0 ~ /^description:/ {
      v = $0
      sub(/^description:[[:space:]]*/, "", v)
      # Folded (>) or literal (|) block scalar: body is on the following lines.
      if (v ~ /^[>|][0-9]*[+-]?[[:space:]]*$/) { collecting = 1; next }
      gsub(/^["\047]|["\047]$/, "", v)
      buf = v
      exit
    }
    collecting {
      # Any unindented line ends the block scalar.
      if ($0 ~ /^[^[:space:]]/) exit
      l = $0
      sub(/^[[:space:]]+/, "", l)
      sub(/[[:space:]]+$/, "", l)
      if (l == "") next
      buf = (buf == "" ? l : buf " " l)
    }
    END { print buf }
  ' "$1"
}

# Trim a description down to a listing-sized blurb: prefer the first sentence,
# and if that is still long, cut on a word boundary rather than mid-word.
summarize_description() {
  local text="$1" limit="${2:-150}" first cut
  first="${text%%. *}"
  [ "$first" != "$text" ] && first="$first."
  [ "${#first}" -le "$limit" ] && { printf '%s' "$first"; return; }
  cut="${first:0:$limit}"
  cut="${cut% *}"
  printf '%s…' "${cut%%[,;:] }"
}

# Emit the `- **`/name`** — description` bullets for every installed skill.
# Both the global AGENTS.md and the repo's own listing render from this, so the
# two cannot drift apart.
emit_skill_bullets() {
  local skill_dir sname desc
  for skill_dir in "$AGENTS_DIR"/*/; do
    [ -f "$skill_dir/SKILL.md" ] || continue
    sname=$(basename "$skill_dir")
    desc=$(skill_description "$skill_dir/SKILL.md")
    printf -- '- **`/%s`** — %s\n' "$sname" "$(summarize_description "$desc")"
  done
}

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
    # Skip tool dirs that are really the source-of-truth dir itself (e.g.
    # ~/.claude/skills symlinked to ~/.agents/skills). Symlinking into it
    # would delete the real copy just made and leave a self-referential link.
    if [ "$(cd "$tool_dir" && pwd -P)" = "$(cd "$AGENTS_DIR" && pwd -P)" ]; then
      continue
    fi
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

instruction_count=0
if [ -d "$SCRIPT_DIR/instructions" ]; then
  for instruction_file in "$SCRIPT_DIR"/instructions/*.md; do
    [ -f "$instruction_file" ] || continue
    cp "$instruction_file" "$PI_INSTRUCTIONS_DIR/$(basename "$instruction_file")"
    echo "Instruction: $(basename "$instruction_file") -> $PI_INSTRUCTIONS_DIR"
    instruction_count=$((instruction_count + 1))
  done
fi

extension_count=0
if [ -d "$SCRIPT_DIR/pi-extensions" ]; then
  for extension_file in "$SCRIPT_DIR"/pi-extensions/*.ts; do
    [ -f "$extension_file" ] || continue
    cp "$extension_file" "$PI_EXTENSIONS_DIR/$(basename "$extension_file")"
    echo "Pi extension: $(basename "$extension_file") -> $PI_EXTENSIONS_DIR"
    extension_count=$((extension_count + 1))
  done
fi

# Regenerate ~/.agents/AGENTS.md with current skill listing
AGENTS_MD="$AGENTS_HOME_DIR/AGENTS.md"
{
  cat << 'HEADER'
# Global Agent Instructions

## Standing Rules

- **Planning always lives in [`K2412/planning`](https://github.com/K2412/planning)** (private).
  Every spec epic, task sub-issue and wayfinder map goes there — never in a code repo, and never in
  the tracker the work came from. Pass `-R K2412/planning` on every `gh issue` / `gh label` /
  `gh api repos/...` call; `gh` otherwise targets the repo you're standing in.
- **Never write to a shared team tracker** (Linear, Jira) — read tickets, but don't comment, edit or
  change status. What appears there is the user's to write.
- **Prototypes are throwaway**: never branch and never commit one. The artifact goes to a gitignored
  directory in the repo; only the verdict, its numbers, and the settings it depends on carry forward.

## Available Skills

Skills load automatically from `~/.agents/skills/`. Use `/skill-name` or describe what you need.

HEADER
  emit_skill_bullets
  echo ""
  echo "> Source of truth: \`~/.agents/skills/\` — managed via [K2412/Skillz](https://github.com/K2412/Skillz). Run \`install.sh\` to sync."
} > "$AGENTS_MD"
echo "Generated: $AGENTS_MD"

# Regenerate the repo's own skill listing from the same bullets, so the
# checked-in docs can't drift from what is actually installed.
REPO_AGENTS_MD="$SCRIPT_DIR/AGENTS.md"
BEGIN_MARKER="<!-- skillz:available-skills -->"
END_MARKER="<!-- /skillz:available-skills -->"
if [ -f "$REPO_AGENTS_MD" ] \
  && grep -qF "$BEGIN_MARKER" "$REPO_AGENTS_MD" \
  && grep -qF "$END_MARKER" "$REPO_AGENTS_MD"; then
  repo_tmp=$(mktemp)
  {
    awk -v m="$BEGIN_MARKER" 'index($0, m) { exit } { print }' "$REPO_AGENTS_MD"
    echo "$BEGIN_MARKER"
    echo "## Available Skills"
    echo ""
    echo "Skills load automatically from \`~/.agents/skills/\` (shared across Claude Code, Codex, and OpenCode). Invoke with \`/skill-name\` or just describe what you need:"
    echo ""
    emit_skill_bullets
    echo ""
    echo "> Skill source of truth: \`~/.agents/skills/\` — managed via the Skillz repo. Run its \`install.sh\` to sync."
    echo "$END_MARKER"
    awk -v m="$END_MARKER" 'found { print } index($0, m) { found = 1 }' "$REPO_AGENTS_MD"
  } > "$repo_tmp"
  mv -f "$repo_tmp" "$REPO_AGENTS_MD"
  echo "Regenerated: $REPO_AGENTS_MD (skill listing)"
else
  echo "Skipped: $REPO_AGENTS_MD (missing skillz:available-skills markers)"
fi

# Symlink ~/.claude/CLAUDE.md -> ~/.agents/AGENTS.md for Claude Code global context
CLAUDE_MD="$HOME/.claude/CLAUDE.md"
ln -sf "$AGENTS_MD" "$CLAUDE_MD"
echo "Symlinked: $CLAUDE_MD -> $AGENTS_MD"

echo ""
echo "Done. $installed skill(s) installed to $AGENTS_DIR."
echo "      $instruction_count instruction module(s) installed to $PI_INSTRUCTIONS_DIR."
echo "      $extension_count Pi extension(s) installed to $PI_EXTENSIONS_DIR."
if [ "$linked" -gt 0 ]; then
  echo "      $linked symlink(s) created across tool dirs."
else
  echo "      No tool dirs found (~/.claude/skills, ~/.codex/skills)."
fi
echo "Restart Claude Code or OpenCode to pick up skill changes."
