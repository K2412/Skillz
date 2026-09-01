# Automatic Workflow Memory Boundary

## Architecture Contract

**Contract:** Automatic Workflow Memory Boundary
**Authorized behavior:** `pair`, `implement`, `architecture`, and `teach` automatically use qualified generic memory at lifecycle boundaries while continuing normally when memory is absent or incompatible.
**Module:** Shared workflow memory protocol
**Protected policy:** Planning issues, repository guidance, architecture contracts and decision records, and teaching mission and learning records remain authoritative. Generic memory cannot approve work, establish task state, or prove learning.
**Knowledge owned:** Top-level versus nested session ownership, top-five recall, authority precedence, strict event qualification, scope defaults, correction behavior, evidence minimization, warning suppression, and final-flush behavior.

### Interface

- **Open:** After authoritative state and project identity are resolved, the outermost workflow quietly recalls at most five cited project and global memories. It filters conflicts in favor of authority and returns advisory context. A nested workflow inherits the active session and does not recall again.
- **Capture:** After a durable event occurs, the owning skill submits only a stable preference, constraint, accepted decision, explicit correction, or reusable lesson. Ambiguous scope defaults to project. A known contradiction uses `correct`; without a known target it is not saved as a competing claim.
- **Close:** The outermost workflow calls `flush` at normal completion, explicit pause or stop, and handoff. Nested skills do not flush. Already queued events provide the only crash recovery.
- All operations fail open. Successful operation is quiet; unavailability is reported at most once per workflow session without private content.

### Dependency Direction

- Allowed: the four workflow skills -> injected `references/memory/` protocol -> versioned MCP tools -> shared daemon.
- Allowed: each skill -> its existing authoritative planning, repository, architecture, or teaching state.
- Forbidden: skills -> SQLite, FastEmbed, outbox, client configuration, or daemon internals.
- Forbidden: recalled task intent entering implement's fresh-worker prompt unless corroborated by issue or repository data.
- Forbidden: generic memory recording task status, contract bodies, patches, mission state, demonstrated learning, reps, debts, or raw session summaries.
- Boundary data: versioned MCP requests and outcomes, minimal evidence spans, and a small advisory result set.

### Scope

- Allowed neighborhood: `shared/memory/`, shared manifests, the four skill instructions and evals, installation distribution checks, memory glossary and ADRs, and rollout documentation.
- Predicted touchpoints: `pair`, `implement`, `architecture`, and `teach`; their `.shared` manifests and evals; the shared memory reference; installation and README guidance.
- Outside this slice: other skills, service schema or storage changes, mission-specific generic scope, remote storage, and per-message memory.

### Verification

- Hard guards: authority-first and conflict scenarios; top-five bound; quiet success; one warning; absent or incompatible service fail-open; immediate strict capture; project-default scope; known-target correction; pause, handoff, and completion flush; nested-session suppression; no task-state or learning duplication; no direct storage, embedding, or config dependencies; and identical shared-module installation in all four skills.
- Hard guards: all four remain disabled from installed automatic use until one combined release evaluation passes at least 90 percent relevant recall within five results and zero project-scope or inactive-memory leaks.
- Diagnostic signals: recalled count and context bytes, filtered conflicts, captured and rejected candidates, duplicate rate, warning count, and flush outcome.

### Escalate When

- A supported client cannot expose the five MCP tools consistently to a skill.
- Nested session ownership requires a new service operation or persistent state.
- A workflow needs generic memory to override or duplicate its authority.
- Teach needs mission-specific generic scope.
- Privacy-safe evidence cannot support a candidate.
- Retrieval misses the release threshold.

### Checkpoint

- Build the shared protocol and one complete `pair` integration first, then architecture-check the exact isolated patch.
- Implement `implement`, `architecture`, and `teach` as bounded tasks after Continue.
- Install and enable all four only after the combined release evaluation passes.
