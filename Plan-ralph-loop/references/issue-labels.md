# Issue Label Protocol

Labels used by the ralph loop to select, track, and communicate issue state.

## Selection Labels

| Label | Meaning |
|---|---|
| `ralph` | Issue is eligible for autonomous processing |
| `blocked` | Issue is excluded from selection (human intervention needed) |

Ralph selects issues matching `is:open label:ralph -label:blocked`, ordered by issue number ascending.

## Sizing Labels

Apply one sizing label per issue to communicate expected effort:

| Label | Meaning |
|---|---|
| `S` | Small — single file, isolated change, 1 iteration expected |
| `M` | Medium — multi-file, 2-4 iterations expected |
| `L` | Large — architectural, 5+ iterations or human steering recommended |

`L` issues are eligible for `ralph-once` (human-in-the-loop) rather than `ralph-loop`.

## Status Labels (applied by ralph)

| Label | Applied when |
|---|---|
| `ralph-in-progress` | Loop starts an iteration on this issue |
| `ralph-pr-opened` | A PR has been opened for this issue |
| `ralph-needs-review` | Agent emitted COMPLETE, awaiting human review |
| `ralph-failed` | Gate failure halted the loop on this issue |

## Convention

- Human adds `ralph` + size label when ready for automation.
- Human adds `blocked` when the issue requires input (ralph removes it when issue is re-queued).
- Ralph never removes `blocked` — only humans do.
