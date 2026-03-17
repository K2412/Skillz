"""
Claude Code adapter — parses JSONL session logs produced by claude CLI.

Log format: one JSON object per line, each representing a message or event
in the conversation. Tool use appears as content blocks with type "tool_use"
and tool results as type "tool_result".
"""

import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from workflow_miner import NormalizedEvent


class ClaudeCodeAdapter:
    def parse(self, log_file: Path) -> list[NormalizedEvent]:
        events = []
        session_id = log_file.parent.name

        for line in log_file.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            ts = record.get("timestamp") or record.get("created_at") or ""
            msg_type = record.get("type") or record.get("role") or ""

            # Conversation message with content blocks
            content = record.get("content") or []
            if isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    block_type = block.get("type", "")

                    if block_type == "tool_use":
                        tool_name = block.get("name", "")
                        tool_input = block.get("input") or {}
                        file_paths = _extract_file_paths(tool_input)

                        events.append(NormalizedEvent(
                            timestamp=ts,
                            session_id=session_id,
                            event_type="tool_call",
                            tool_name=tool_name,
                            tool_input=tool_input,
                            file_paths=file_paths,
                        ))

                    elif block_type == "tool_result":
                        events.append(NormalizedEvent(
                            timestamp=ts,
                            session_id=session_id,
                            event_type="tool_result",
                            tool_name="",
                            tool_output={"content": str(block.get("content", ""))[:200]},
                        ))

            # Plain text messages
            if msg_type in ("user", "human"):
                events.append(NormalizedEvent(
                    timestamp=ts,
                    session_id=session_id,
                    event_type="user_message",
                ))
            elif msg_type in ("assistant",):
                events.append(NormalizedEvent(
                    timestamp=ts,
                    session_id=session_id,
                    event_type="assistant_message",
                ))

        return events


def _extract_file_paths(tool_input: dict) -> list[str]:
    """Extract file path values from tool input parameters."""
    paths = []
    for key in ("file_path", "path", "command"):
        val = tool_input.get(key)
        if isinstance(val, str) and "/" in val:
            paths.append(val)
    return paths
