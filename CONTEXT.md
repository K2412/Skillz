# Agent Memory

This context covers durable personal and project knowledge shared by Claude Code, Codex, and OpenCode. It does not replace repository documentation, executable skills, raw conversation history, or the learning ledger.

## Language

**Memory**:
An atomic, durable claim that may help an agent in a later session. It includes scope, evidence, lifecycle state, and extraction provenance.
_Avoid_: Note, transcript

**Durable claim**:
A stable preference, standing instruction, settled decision, correction, recurring constraint, or reusable lesson. Task-local chatter and an agent's unaccepted suggestions are not durable claims.
_Avoid_: Potentially useful text

**Global memory**:
A memory intentionally visible from every project, such as a stable personal preference. Global is an explicit scope, not the absence of a project identifier.
_Avoid_: Unscoped memory

**Project memory**:
A memory visible only while working in its named project. Default recall combines the current project's memories with global memories and excludes other projects.
_Avoid_: Local memory

**Project identity**:
The normalized owner/repository slug from a workspace's primary Git remote. A non-Git workspace must provide an explicit stable identifier rather than derive identity from its local path.
_Avoid_: Directory name

**Memory event**:
A durable observation that triggers automatic extraction during work. A final flush at a skill checkpoint or session end processes relevant context not captured by earlier events.
_Avoid_: Every message

**Evidence span**:
The smallest exact, privacy-filtered excerpt that supports an inferred memory, stored with its source agent, session, observation time, and extractor version.
_Avoid_: Transcript, rationale

**Entity**:
A normalized person, project, tool, or concept linked to one or more memories for filtering and ranking. Version one does not treat entity links as a traversable knowledge graph.
_Avoid_: Tag, graph node

**Supersession**:
A correction that makes an older memory inactive while preserving both memories and their relationship. It is the default way to change a claim without losing history.
_Avoid_: Overwrite

**Erasure**:
An explicit request to remove memory content from live tables, vectors, outboxes, and projections. A content-free deletion marker may remain, and provider recovery copies may persist until Turso's published retention window expires.
_Avoid_: Retraction, tombstone

**Memory outbox**:
An encrypted local retry queue used only when a validated remote write cannot complete. Entries leave the outbox after Turso confirms the write; it is not an alternative memory store.
_Avoid_: Local memory

**Memory service**:
The separately versioned local Model Context Protocol server that owns extraction validation, persistence, retrieval, correction, erasure, and retry policy for every supported agent.
_Avoid_: Memory skill, Turso client

**Temporary local memory**:
The encrypted local `pyturso` database that temporarily owns canonical memories until the approved Turso cutover. Its key lives in the operating-system keychain, and the cutover must preserve every stable identifier and lifecycle record before remote storage becomes authoritative.
_Avoid_: Cache, outbox

**Learning record**:
Evidence in `Learning/ledger` of demonstrated understanding, practice, or debt. It remains authoritative in the ledger and is not a generic memory.
_Avoid_: Learning memory
