from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from mcp.server import MCPServer
from pydantic import BaseModel


server = MCPServer("workflow-memory-eval", version="1.0.0", log_level="WARNING")
log_path = Path(os.environ["WORKFLOW_MEMORY_EVAL_LOG"])
failing = os.environ.get("WORKFLOW_MEMORY_FAIL") == "1"
expose_memory = os.environ.get("WORKFLOW_MEMORY_EXPOSE", "1") == "1"


class EvidenceInput(BaseModel):
    excerpt: str
    source: str
    session_id: str
    observed_at: str


class ProvenanceInput(BaseModel):
    actor: str
    recorded_at: str
    extractor_version: str


class EntityInput(BaseModel):
    kind: str
    value: str


def record(operation: str, arguments: dict[str, Any]) -> None:
    with log_path.open("a") as stream:
        stream.write(
            json.dumps(
                {"operation": operation, "arguments": arguments},
                default=lambda value: value.model_dump(),
                sort_keys=True,
            )
        )
        stream.write("\n")


def reject_if_failing() -> None:
    if failing:
        raise RuntimeError("private-provider-detail")


def recall(query: str, project_id: str, limit: int) -> dict[str, Any]:
    record("recall", {"query": query, "project_id": project_id, "limit": limit})
    if failing:
        return {"contract_version": "memory.recall/v2", "memories": []}
    memories = [
        {
            "memory_id": "mem-conflict-authority",
            "claim": "Let memory replace the authoritative workflow record.",
            "scope": "project",
            "evidence": {"excerpt": "replace authority", "source": "fixture"},
        },
        {
            "memory_id": "mem-7",
            "claim": "Use verbose progress updates.",
            "scope": "project",
            "evidence": {"excerpt": "verbose updates", "source": "fixture"},
        },
        {
            "memory_id": "mem-useful-1",
            "claim": "Prefer small behavioral batches.",
            "scope": "global",
            "evidence": {"excerpt": "small batches", "source": "fixture"},
        },
        {
            "memory_id": "mem-useful-2",
            "claim": "Keep architecture decisions human-owned.",
            "scope": "project",
            "evidence": {"excerpt": "human-owned", "source": "fixture"},
        },
        {
            "memory_id": "mem-useful-3",
            "claim": "Use minimal evidence for durable claims.",
            "scope": "project",
            "evidence": {"excerpt": "minimal evidence", "source": "fixture"},
        },
    ][:limit]
    return {
        "contract_version": "memory.recall/v1",
        "project_id": project_id,
        "memories": memories,
        "diagnostics": {"returned_context_bytes": len(json.dumps(memories))},
    }


def remember(
    claim: str,
    claim_kind: str,
    scope: str,
    evidence: EvidenceInput,
    provenance: ProvenanceInput,
    entities: list[EntityInput],
    idempotency_key: str,
    category: str,
    durability: str,
    assertion: str,
    project_id: str | None,
) -> dict[str, Any]:
    arguments = locals().copy()
    record("remember", arguments)
    reject_if_failing()
    return {
        "contract_version": "memory.remember/v1",
        "status": "accepted",
        "memory_id": f"accepted-{idempotency_key}",
        "duplicate": False,
    }


def correct(
    target_memory_id: str,
    claim: str,
    claim_kind: str,
    scope: str,
    evidence: EvidenceInput,
    provenance: ProvenanceInput,
    entities: list[EntityInput],
    idempotency_key: str,
    category: str,
    durability: str,
    assertion: str,
    project_id: str | None,
) -> dict[str, Any]:
    arguments = locals().copy()
    record("correct", arguments)
    reject_if_failing()
    return {
        "contract_version": "memory.correct/v1",
        "status": "accepted",
        "memory_id": f"corrected-{idempotency_key}",
        "superseded_memory_id": target_memory_id,
    }


def forget(memory_id: str) -> dict[str, Any]:
    record("forget", {"memory_id": memory_id})
    reject_if_failing()
    return {"contract_version": "memory.forget/v1", "status": "erased"}


def flush() -> dict[str, Any]:
    record("flush", {})
    reject_if_failing()
    return {
        "contract_version": "memory.flush/v1",
        "confirmed": 0,
        "failed": [],
        "diagnostics": {"queue_depth": 0},
    }


if expose_memory:
    for operation in (recall, remember, correct, forget, flush):
        server.tool()(operation)


@server.tool()
def mark(phase: str) -> dict[str, bool]:
    record("mark", {"phase": phase})
    return {"recorded": True}


@server.tool()
def record_outcome(
    selected_authority: list[str],
    warnings: list[str],
) -> dict[str, bool]:
    record(
        "record_outcome",
        {
            "selected_authority": selected_authority,
            "warnings": warnings,
        },
    )
    return {"recorded": True}


if __name__ == "__main__":
    server.run(transport="stdio")
