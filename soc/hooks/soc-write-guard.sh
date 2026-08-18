#!/usr/bin/env bash
# soc write-guard — PreToolUse hook on Edit|Write|NotebookEdit.
#
# While a soc session is active, the agent must NOT write the user's work: soc
# guides, the human types. Activation is signalled by a sentinel file that /soc
# drops at the start of a session and removes at the end.
#
# FAIL-OPEN by construction: no sentinel, or ANY error, => allow the write. The
# only path that denies is "a fresh sentinel exists AND this isn't soc's own
# ledger bookkeeping", so a bug here can never block normal editing.

set -u
SENTINEL="$HOME/.claude/.soc-active"

# Not in soc-mode => allow everything.
[ -f "$SENTINEL" ] || exit 0

# Stale guard: a sentinel left behind by an abandoned/crashed session (older
# than 6h) is ignored and cleaned up, so soc-mode can never get stuck on.
now=$(date +%s 2>/dev/null) || exit 0
mtime=$(stat -f %m "$SENTINEL" 2>/dev/null) || exit 0
if [ $(( now - mtime )) -gt 21600 ]; then
  rm -f "$SENTINEL" 2>/dev/null
  exit 0
fi

# Allow soc's own bookkeeping: writing the learning ledger is the agent's job,
# not the user's work. Everything under the ledger dir passes.
path=$(jq -r '.tool_input.file_path // .tool_input.notebook_path // ""' 2>/dev/null) || path=""
case "$path" in
  "$HOME/Documents/Learning/ledger/"*) exit 0 ;;
esac

# Active soc session, and this is the user's work => deny via the harness
# permission decision (house pattern).
printf '%s' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"soc-mode is active: you guide, you do not type. Ask the user for their next line — do not use Edit/Write/NotebookEdit on their behalf. The user ends the soc session (or deletes ~/.claude/.soc-active) to lift this."}}'
true
