# GitHub-issues plan — shared tracker cookbook

The implementation pipeline (`spec` → `plan-review` → `implement` → `review-change`) tracks work as
**GitHub issues in the code repo you're working in** — issues live with the code, are branch-independent,
and are visible in the GitHub UI without a database query. All commands use `gh`; none touch
`git commit`/`git push`, so the global push guard never fires.

`R` below is the code repo (`gh` defaults to the repo of the current directory; pass `-R owner/repo`
to target another). The **epic** is one issue; each **task** is a sub-issue of it.

## Ensure labels exist (idempotent — run once per repo)

```bash
gh label create "spec:epic"    --color 5319e7 --description "Accepted plan — the epic" --force
gh label create "spec:task"    --color 1d76db --description "Atomic TDD slice under an epic" --force
gh label create "blocked"      --color b60205 --description "Has an open blocker — not on the frontier" --force
gh label create "needs-human"  --color d93f0b --description "Human approval required before proceeding" --force
```

## Create the epic

```bash
EPIC_URL=$(gh issue create --label "spec:epic" \
  --title "<task title, ≤180 chars>" \
  --body "<the full spec from the spec skill>")
EPIC_N=${EPIC_URL##*/}
```

`EPIC_N` is the epic's issue number — the handle every downstream stage uses. Refer to it by **title**
in narration, not a bare `#N`.

## Create a task (sub-issue of the epic)

```bash
# 1. create the task with its body (scope + acceptance criteria as a checklist + the confirmed seam)
TASK_URL=$(gh issue create --label "spec:task" \
  --title "<task title>" \
  --body "$(cat <<'MD'
## Scope
<what this slice delivers, end-to-end>

## Test seam
<the confirmed seam>

## Acceptance criteria
- [ ] <criterion tied to a user story>
- [ ] <criterion>
MD
)")
TN=${TASK_URL##*/}
# 2. link it as a sub-issue of the epic (sub_issue_id is the DATABASE id; -F sends it as an integer)
gh api --method POST repos/$R/issues/$EPIC_N/sub_issues -F sub_issue_id=$(gh api repos/$R/issues/$TN --jq '.id')
```

## Wire blocking + human gates (second pass, after tasks exist)

```bash
# task blocked by another → label + record in body's "Blocked by" line
gh issue edit <TN> --add-label "blocked"          # (edit body to list "Blocked by #<BLOCKER_N>")
# irreversible op (migration, schema change, external write) → gate it
gh issue edit <TN> --add-label "needs-human"      # implement will stop and ask before this one
```

## Read the plan

```bash
# epic body (the spec)
gh issue view <EPIC_N> --json title,body,labels
# all tasks under the epic
gh api repos/$R/issues/<EPIC_N>/sub_issues --jq '.[] | "#\(.number) [\(.state)] \(.title) | \((.labels|map(.name))|join(","))"'
# the frontier = open tasks with no "blocked" label
```

## Attach a prototype pointer to the epic

```bash
gh issue comment <EPIC_N> --body "prototype: branch prototype/<slug> — verdict: <one line>; learned: <one line>"
```

## Complete a task / close the epic

```bash
gh issue close <TN>       # a finished task
gh issue close <EPIC_N>   # the epic, when review passes
```

## Find open epics (for `pair resume`)

```bash
gh issue list --label "spec:epic" --state open --json number,title,url
```

**No `gh`?** Fall back to a Markdown checklist of the spec + tasks and tell the user GitHub tracking
was skipped. There is no local DB — the issues *are* the plan.
