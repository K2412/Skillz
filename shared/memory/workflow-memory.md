# Workflow Memory Protocol

Automatic workflow-memory ordinary runs are active for `pair`. Other skills do not use this protocol unless a later release explicitly adds them.

Memory is advisory. User instructions and authoritative planning, repository, architecture, mission,
and learning records always win. Memory cannot approve work, establish task state, or prove learning.

## Compatible tools

Use only these MCP operations and exact version-one contracts:

| Operation | Contract |
| --- | --- |
| `recall` | `memory.recall/v1` |
| `remember` | `memory.remember/v1` |
| `correct` | `memory.correct/v1` |
| `forget` | `memory.forget/v1` |
| `flush` | `memory.flush/v1` |

Treat a missing operation or any other declared contract version as unavailable. Do not call service
storage, embedding, outbox, credential, transport, or client-configuration internals.

## Session ownership

The outermost memory-aware workflow owns one in-context session. Track whether it is outermost,
whether the single warning has been shown, and the IDs and scopes returned by recall. This is
workflow context, not persisted state and not a new service operation.

A nested memory-aware workflow inherits that active session. It may capture its own qualified durable
events, but it does not recall, flush, or start another warning budget.

## Open

1. Load the caller's user instruction and authoritative project, planning, repository, architecture,
   mission, or learning state. Resolve the normalized Git project identity, or use an explicit stable
   project identity for a non-Git workspace.
2. If this is a nested session, inherit the active session and stop the open procedure.
3. Verify the five compatible operations above. On absence or incompatibility, continue the workflow
   unchanged and apply the warning rule below.
4. Call `recall` once with the resolved project identity and `limit: 5`. Query only for context useful
   to the current workflow. The service combines current-project and explicit global scope.
5. Keep at most five results with their memory IDs, claims, scopes, and evidence citations. Remove any
   claim that conflicts with the loaded authorities or current user instruction. Use the remainder
   only as advisory context.

Successful open is quiet. Do not announce recall or memory availability.

## Capture

Capture immediately after a durable event, rather than waiting for close. A candidate qualifies only
when it is one of:

- a stable user preference;
- a recurring or standing constraint;
- a decision explicitly accepted by the user;
- an explicit user correction;
- a reusable lesson supported by the completed work.

Reject task chatter, unaccepted suggestions, raw summaries, task or workflow status, contract bodies,
patches, raw transcripts, mission state, demonstrated learning, reps, and debts. When privacy-safe
minimal evidence cannot support the claim, reject it rather than broadening the evidence.

For a qualified candidate:

1. Apply any stricter scope rule declared by the calling workflow before this generic default. Use
   explicit global scope only when the user clearly made the claim cross-project and the caller permits
   global scope. Otherwise use project scope, including every ambiguous case. Include the identity
   resolved during open on every project-scoped `remember` or `correct` call; omit project identity
   for global scope.
2. Send the smallest exact privacy-filtered evidence excerpt, source, session, observation time,
   extraction provenance, typed entities, and an idempotency key.
3. If an explicit contradiction targets a known recalled memory ID, call `correct` with that target
   and the replacement candidate. If no target ID is known, reject the contradiction instead of
   calling `remember` with a competing claim.
4. Otherwise call `remember` once. Treat `accepted`, `queued`, and `rejected` as non-blocking outcomes.

Never call `forget` automatically. Erasure remains an explicit user operation.

## Close

The outermost owner calls `flush` once at normal completion, explicit pause or stop, and handoff out
of the workflow. A nested workflow never flushes. Continue the host workflow regardless of the flush
outcome; already queued events are the only crash recovery.

## Failure and diagnostics

Every operation fails open: preserve all authoritative and workflow state and continue normal work.
Across one session, report unavailability or incompatibility at most once with a non-secret warning
that contains no claim, evidence, project identity, provider detail, or configuration. Suppress later
warnings. Successful operations are quiet.

For evaluation and checkpoint reports, record only: recalled count and returned context bytes,
filtered-conflict count, accepted/queued/rejected candidate counts, duplicate count, warning count,
and flush outcome. These diagnostics do not change workflow behavior.
