#!/usr/bin/env bash
# ralph-once.sh — Human-in-the-loop single ralph iteration
# Usage: bash scripts/ralph-once.sh
# Set RALPH_ISSUE_NUMBER to target a specific issue.
# Configure via environment variables or .env file.

set -euo pipefail

# ─── Load .env if present ────────────────────────────────────────────────────
if [[ -f ".env" ]]; then
  # shellcheck disable=SC1091
  source .env
fi

# ─── Defaults ────────────────────────────────────────────────────────────────
RALPH_DRAFT_PR="${RALPH_DRAFT_PR:-true}"
RALPH_HALT_ON_GATE_FAIL="${RALPH_HALT_ON_GATE_FAIL:-false}"
RALPH_ISSUE_LABEL="${RALPH_ISSUE_LABEL:-ralph}"
RALPH_BLOCKED_LABEL="${RALPH_BLOCKED_LABEL:-blocked}"
RALPH_PROGRESS_FILE="${RALPH_PROGRESS_FILE:-progress.txt}"
RALPH_BRANCH_PREFIX="${RALPH_BRANCH_PREFIX:-ralph}"
RALPH_AGENT_CMD="${RALPH_AGENT_CMD:-claude}"
RALPH_AGENT_TIMEOUT="${RALPH_AGENT_TIMEOUT:-600}"
RALPH_COMMIT_PREFIX="${RALPH_COMMIT_PREFIX:-[ralph]}"
RALPH_PR_LABELS="${RALPH_PR_LABELS:-ralph}"
RALPH_ISSUE_NUMBER="${RALPH_ISSUE_NUMBER:-}"

RALPH_GATE_TYPECHECK_ENABLED="${RALPH_GATE_TYPECHECK_ENABLED:-true}"
RALPH_TYPECHECK_CMD="${RALPH_TYPECHECK_CMD:-mypy .}"
RALPH_GATE_LINT_ENABLED="${RALPH_GATE_LINT_ENABLED:-true}"
RALPH_LINT_CMD="${RALPH_LINT_CMD:-ruff check .}"
RALPH_GATE_TEST_ENABLED="${RALPH_GATE_TEST_ENABLED:-true}"
RALPH_TEST_CMD="${RALPH_TEST_CMD:-pytest}"
RALPH_GATE_COVERAGE_ENABLED="${RALPH_GATE_COVERAGE_ENABLED:-false}"
RALPH_COVERAGE_CMD="${RALPH_COVERAGE_CMD:-pytest --cov}"
RALPH_GATE_DUPLICATION_ENABLED="${RALPH_GATE_DUPLICATION_ENABLED:-false}"
RALPH_DUPLICATION_CMD="${RALPH_DUPLICATION_CMD:-jscpd .}"
RALPH_GATE_ENTROPY_ENABLED="${RALPH_GATE_ENTROPY_ENABLED:-false}"
RALPH_ENTROPY_CMD="${RALPH_ENTROPY_CMD:-}"

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROMPT_FILE="${SKILL_DIR}/references/prompt.md"

# ─── Helpers ─────────────────────────────────────────────────────────────────
log() { echo "[ralph-once] $*"; }

pick_issue() {
  if [[ -n "${RALPH_ISSUE_NUMBER}" ]]; then
    gh issue view "${RALPH_ISSUE_NUMBER}" --json number,title \
      --jq '"\(.number) \(.title)"' 2>/dev/null || true
  else
    gh issue list \
      --search "is:open label:${RALPH_ISSUE_LABEL} -label:${RALPH_BLOCKED_LABEL}" \
      --json number,title \
      --jq '.[0] | "\(.number) \(.title)"' 2>/dev/null || true
  fi
}

run_gate() {
  local name="$1" enabled_var="$2" cmd="$3"
  if [[ "${!enabled_var}" != "true" ]]; then
    log "Gate ${name}: skipped"
    return 0
  fi
  log "Gate ${name}: running..."
  if eval "${cmd}"; then
    log "Gate ${name}: PASS"
    return 0
  else
    log "Gate ${name}: FAIL"
    return 1
  fi
}

# ─── Main ─────────────────────────────────────────────────────────────────────
log "Starting ralph-once"

# Determine iteration number from progress file
iteration=1
if [[ -f "${RALPH_PROGRESS_FILE}" ]]; then
  iteration=$(( $(grep -c "^\[iter-" "${RALPH_PROGRESS_FILE}" 2>/dev/null || echo 0) + 1 ))
fi

# 1. Select issue
issue_line="$(pick_issue)"
if [[ -z "${issue_line}" ]]; then
  log "No eligible issues found."
  exit 1
fi
issue_number="$(echo "${issue_line}" | awk '{print $1}')"
issue_title="$(echo "${issue_line}" | cut -d' ' -f2-)"
log "Issue #${issue_number}: ${issue_title}"

# 2. Create branch
branch="${RALPH_BRANCH_PREFIX}/issue-${issue_number}/iter-${iteration}"
git checkout -b "${branch}" 2>/dev/null || git checkout "${branch}"
log "Branch: ${branch}"

# 3. Build agent prompt
issue_body="$(gh issue view "${issue_number}" --json body --jq '.body')"
progress_context=""
if [[ -f "${RALPH_PROGRESS_FILE}" ]]; then
  progress_context="$(cat "${RALPH_PROGRESS_FILE}")"
fi

agent_prompt="$(cat "${PROMPT_FILE}")

## Issue #${issue_number}: ${issue_title}

${issue_body}

## Progress History

${progress_context}"

# 4. Run agent
log "Running agent (timeout=${RALPH_AGENT_TIMEOUT}s)..."
agent_output=""
agent_output="$(timeout "${RALPH_AGENT_TIMEOUT}" ${RALPH_AGENT_CMD} --print "${agent_prompt}" 2>&1)" || true

# 5. Run feedback gates
gates_ok=true
gate_results=""
for gate_name in typecheck lint test coverage duplication entropy; do
  upper="${gate_name^^}"
  enabled_var="RALPH_GATE_${upper}_ENABLED"
  cmd_var="RALPH_${upper}_CMD"
  if [[ "${!enabled_var:-false}" == "true" ]] && [[ -n "${!cmd_var:-}" ]]; then
    if ! run_gate "${gate_name}" "${enabled_var}" "${!cmd_var}"; then
      gates_ok=false
      gate_results+=" ${gate_name}:FAIL"
    else
      gate_results+=" ${gate_name}:PASS"
    fi
  fi
done

# 6. Commit & PR
pr_url=""
if [[ "${gates_ok}" == "true" ]]; then
  git add -A
  if ! git diff --cached --quiet; then
    git commit -m "${RALPH_COMMIT_PREFIX} resolve issue #${issue_number} (iter ${iteration})"

    pr_flag=""
    [[ "${RALPH_DRAFT_PR}" == "true" ]] && pr_flag="--draft"

    pr_url="$(gh pr create \
      --title "${RALPH_COMMIT_PREFIX} Issue #${issue_number}: ${issue_title}" \
      --body "Automated by ralph-once (iteration ${iteration}). Resolves #${issue_number}." \
      --label "${RALPH_PR_LABELS}" \
      ${pr_flag} 2>&1)" || true

    if [[ -n "${pr_url}" ]]; then
      gh issue comment "${issue_number}" --body "PR opened by ralph-once: ${pr_url}"
    fi
  else
    log "No changes to commit."
  fi
fi

# 7. Persist progress
echo "[iter-${iteration}] issue=#${issue_number} branch=${branch} gates_ok=${gates_ok}${gate_results}" >> "${RALPH_PROGRESS_FILE}"

# 8. Summary
log "─── Summary ────────────────────────────────"
log "Issue:   #${issue_number} ${issue_title}"
log "Branch:  ${branch}"
log "Gates:   ${gates_ok}${gate_results}"
[[ -n "${pr_url}" ]] && log "PR:      ${pr_url}"
if echo "${agent_output}" | grep -q '<promise>COMPLETE</promise>'; then
  log "Status:  COMPLETE (agent signalled resolution)"
else
  log "Status:  IN PROGRESS (review and re-run if needed)"
fi
log "────────────────────────────────────────────"
