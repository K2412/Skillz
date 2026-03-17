"""
OpenCode adapter — parses session logs produced by OpenCode CLI.

OpenCode stores sessions as JSONL files with event objects containing
a "type" field. Tool calls appear as type "tool" with a "tool" field.
"""

import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from workflow_miner import NormalizedEvent


class OpenCodeAdapter:
    def parse(self, log_file: Path) -> list[NormalizedEvent]:
        events = []
        session_id = log_file.stem

        for line in log_file.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            ts = record.get("time") or record.get("timestamp") or ""
            event_type = record.get("type") or ""

            if event_type == "tool":
                tool = record.get("tool") or {}
                tool_name = tool.get("name") or tool.get("type") or str(tool)
                tool_input = tool.get("input") or {}

                events.append(NormalizedEvent(
                    timestamp=ts,
                    session_id=session_id,
                    event_type="tool_call",
                    tool_name=tool_name,
                    tool_input=tool_input,
                ))

            elif event_type == "tool_result":
                events.append(NormalizedEvent(
                    timestamp=ts,
                    session_id=session_id,
                    event_type="tool_result",
                    tool_output={"output": str(record.get("output", ""))[:200]},
                ))

            elif event_type in ("message", "user"):
                role = record.get("role") or event_type
                events.append(NormalizedEvent(
                    timestamp=ts,
                    session_id=session_id,
                    event_type="user_message" if role == "user" else "assistant_message",
                ))

        return events
