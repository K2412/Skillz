#!/usr/bin/env bash
# ralph.sh — AFK continuous issue-processing loop
# Usage: bash scripts/ralph.sh
# Configure via environment variables or .env file.
# See references/config.md for all options.

set -euo pipefail

# ─── Load .env if present ────────────────────────────────────────────────────
if [[ -f ".env" ]]; then
  # shellcheck disable=SC1091
  source .env
fi

# ─── Defaults ────────────────────────────────────────────────────────────────
RALPH_MAX_ITERATIONS="${RALPH_MAX_ITERATIONS:-20}"
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

RALPH_GATE_TYPECHECK_ENABLED="${RALPH_GATE_TYPECHECK_ENABLED:-true}"
RALPH_TYPECHECK_CMD="${RALPH_TYPECHECK_CMD:-mypy .}"
RALPH_GATE_LINT_ENABLED="${RALPH_GATE_LINT_ENABLED:-true}"
RALPH_LINT_CMD="${RALPH_LINT_CMD:-ruff check .}"
RALPH_GATE_TEST_ENABLED="${RALPH_GATE_TEST_ENABLED:-true}"
RALPH_TEST_CMD="${RALPH_TEST_CMD:-pytest}"
RALPH_GATE_COVERAGE_ENABLED="${RALPH_GATE_COVERAGE_ENABLED:-false}"
RALPH_COVERAGE_CMD="${RALPH_COVERAGE_CMD:-pytest --cov}"
RALPH_COVERAGE_THRESHOLD="${RALPH_COVERAGE_THRESHOLD:-80}"
RALPH_GATE_DUPLICATION_ENABLED="${RALPH_GATE_DUPLICATION_ENABLED:-false}"
RALPH_DUPLICATION_CMD="${RALPH_DUPLICATION_CMD:-jscpd .}"
RALPH_GATE_ENTROPY_ENABLED="${RALPH_GATE_ENTROPY_ENABLED:-false}"
RALPH_ENTROPY_CMD="${RALPH_ENTROPY_CMD:-}"

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROMPT_FILE="${SKILL_DIR}/references/prompt.md"

# ─── Helpers ─────────────────────────────────────────────────────────────────

log() { echo "[ralph] $*"; }
progress_append() { echo "$*" >> "${RALPH_PROGRESS_FILE}"; }

pick_issue() {
  gh issue list \
    --search "is:open label:${RALPH_ISSUE_LABEL} -label:${RALPH_BLOCKED_LABEL}" \
    --json number,title \
    --jq '.[0] | "\(.number) \(.title)"' 2>/dev/null || true
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

run_all_gates() {
  local gate_failed=0
  run_gate "typecheck" "RALPH_GATE_TYPECHECK_ENABLED" "${RALPH_TYPECHECK_CMD}" || gate_failed=1
  run_gate "lint"      "RALPH_GATE_LINT_ENABLED"      "${RALPH_LINT_CMD}"      || gate_failed=1
  run_gate "test"      "RALPH_GATE_TEST_ENABLED"       "${RALPH_TEST_CMD}"      || gate_failed=1
  run_gate "coverage"  "RALPH_GATE_COVERAGE_ENABLED"   "${RALPH_COVERAGE_CMD}"  || gate_failed=1
  run_gate "duplication" "RALPH_GATE_DUPLICATION_ENABLED" "${RALPH_DUPLICATION_CMD}" || gate_failed=1
  if [[ -n "${RALPH_ENTROPY_CMD}" ]]; then
    run_gate "entropy" "RALPH_GATE_ENTROPY_ENABLED" "${RALPH_ENTROPY_CMD}" || gate_failed=1
  fi
  return ${gate_failed}
}

check_complete() {
  # Returns 0 (true) if COMPLETE signal found in agent output or progress tail
  local agent_out="$1"
  if echo "${agent_out}" | grep -q '<promise>COMPLETE</promise>'; then
    return 0
  fi
  if [[ -f "${RALPH_PROGRESS_FILE}" ]] && tail -20 "${RALPH_PROGRESS_FILE}" | grep -q '<promise>COMPLETE</promise>'; then
    return 0
  fi
  return 1
}

# ─── Main loop ───────────────────────────────────────────────────────────────

log "Starting ralph loop (max_iterations=${RALPH_MAX_ITERATIONS})"
iteration=0

while (( iteration < RALPH_MAX_ITERATIONS )); do
  iteration=$(( iteration + 1 ))
  log "─── Iteration ${iteration}/${RALPH_MAX_ITERATIONS} ───────────────────"

  # 1. Select issue
  issue_line="$(pick_issue)"
  if [[ -z "${issue_line}" ]]; then
    log "No eligible issues found. Loop complete."
    break
  fi
  issue_number="$(echo "${issue_line}" | awk '{print $1}')"
  issue_title="$(echo "${issue_line}" | cut -d' ' -f2-)"
  log "Selected issue #${issue_number}: ${issue_title}"

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
  if ! run_all_gates; then
    gates_ok=false
    progress_append "[iter-${iteration}] GATE FAILURE on issue #${issue_number}"
    if [[ "${RALPH_HALT_ON_GATE_FAIL}" == "true" ]]; then
      log "Gate failure with RALPH_HALT_ON_GATE_FAIL=true. Stopping."
      break
    fi
  fi

  # 6. Commit & PR (only if gates passed)
  if [[ "${gates_ok}" == "true" ]]; then
    git add -A
    if ! git diff --cached --quiet; then
      git commit -m "${RALPH_COMMIT_PREFIX} resolve issue #${issue_number} (iter ${iteration})"

      pr_flag=""
      [[ "${RALPH_DRAFT_PR}" == "true" ]] && pr_flag="--draft"

      pr_url="$(gh pr create \
        --title "${RALPH_COMMIT_PREFIX} Issue #${issue_number}: ${issue_title}" \
        --body "Automated by ralph-loop (iteration ${iteration}). Resolves #${issue_number}." \
        --label "${RALPH_PR_LABELS}" \
        ${pr_flag} 2>&1)" || true

      if [[ -n "${pr_url}" ]]; then
        gh issue comment "${issue_number}" --body "PR opened by ralph: ${pr_url}"
        log "PR: ${pr_url}"
      fi
    else
      log "No changes to commit for issue #${issue_number}"
    fi
  fi

  # 7. Persist progress
  progress_append "[iter-${iteration}] issue=#${issue_number} branch=${branch} gates_ok=${gates_ok}"

  # 8. Check stop condition
  if check_complete "${agent_output}"; then
    log "COMPLETE signal detected. Loop finished."
    break
  fi

  # Return to default branch for next iteration
  git checkout - 2>/dev/null || true
done

log "Loop ended after ${iteration} iteration(s)."
