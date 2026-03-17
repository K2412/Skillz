"""
Codex CLI adapter — parses JSONL session logs produced by the OpenAI Codex CLI.

Log format: one JSON object per line. Tool calls appear as messages with
role "assistant" and content blocks of type "function_call", results as
"function_call_output".
"""

import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from workflow_miner import NormalizedEvent


class CodexCliAdapter:
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

            ts = record.get("timestamp") or record.get("created_at") or ""
            role = record.get("role") or ""
            content = record.get("content") or []

            if isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    block_type = block.get("type", "")

                    if block_type == "function_call":
                        name = block.get("name") or block.get("function", {}).get("name", "")
                        args_raw = block.get("arguments") or block.get("function", {}).get("arguments", "{}")
                        try:
                            args = json.loads(args_raw) if isinstance(args_raw, str) else args_raw
                        except Exception:
                            args = {"raw": args_raw}

                        events.append(NormalizedEvent(
                            timestamp=ts,
                            session_id=session_id,
                            event_type="tool_call",
                            tool_name=name,
                            tool_input=args,
                        ))

                    elif block_type == "function_call_output":
                        events.append(NormalizedEvent(
                            timestamp=ts,
                            session_id=session_id,
                            event_type="tool_result",
                            tool_output={"output": str(block.get("output", ""))[:200]},
                        ))

            if role == "user":
                events.append(NormalizedEvent(
                    timestamp=ts,
                    session_id=session_id,
                    event_type="user_message",
                ))
            elif role == "assistant":
                events.append(NormalizedEvent(
                    timestamp=ts,
                    session_id=session_id,
                    event_type="assistant_message",
                ))

        return events
