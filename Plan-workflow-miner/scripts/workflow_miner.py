#!/usr/bin/env python3
"""
workflow_miner.py — Mine AI coding session logs for automation recommendations.

Usage:
    python3 workflow_miner.py --logs PATH --target {claude_code|codex_cli|opencode|auto}
    python3 workflow_miner.py --logs ~/.claude/projects/ --since 7d --out insights.json
    python3 workflow_miner.py --logs . --target auto --redact

See references/normalized-schema.md for event format.
See references/output-schema.md for output format.
"""

import argparse
import json
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path


# ─── Data classes ─────────────────────────────────────────────────────────────


@dataclass
class NormalizedEvent:
    timestamp: str
    session_id: str
    event_type: str
    tool_name: str = ""
    tool_input: dict = field(default_factory=dict)
    tool_output: dict = field(default_factory=dict)
    approval_required: bool = False
    approved: bool = False
    duration_ms: int = 0
    file_paths: list = field(default_factory=list)
    exit_code: int | None = None


@dataclass
class Episode:
    episode_id: str
    session_id: str
    start_time: str
    end_time: str
    events: list = field(default_factory=list)


# ─── Adapters ─────────────────────────────────────────────────────────────────


def load_adapter(target: str):
    if target == "claude_code":
        from adapters.claude_code import ClaudeCodeAdapter
        return ClaudeCodeAdapter()
    if target == "codex_cli":
        from adapters.codex_cli import CodexCliAdapter
        return CodexCliAdapter()
    if target == "opencode":
        from adapters.opencode import OpenCodeAdapter
        return OpenCodeAdapter()
    raise ValueError(f"Unknown target: {target}")


def detect_format(logs_path: Path) -> str:
    """Heuristically detect log format from file contents."""
    for log_file in sorted(logs_path.rglob("*.jsonl"))[:5]:
        try:
            first_line = log_file.read_text().splitlines()[0]
            data = json.loads(first_line)
            if "tool_use" in str(data) or "type" in data and data.get("type") in ("tool_use", "tool_result"):
                return "claude_code"
            if "action" in data and "codex" in str(log_file).lower():
                return "codex_cli"
        except Exception:
            continue
    return "claude_code"  # default


# ─── Parsing ──────────────────────────────────────────────────────────────────


def parse_logs(logs_path: Path, target: str, since: datetime | None, redact: bool) -> list[NormalizedEvent]:
    if target == "auto":
        target = detect_format(logs_path)
        print(f"[workflow-miner] Detected format: {target}", file=sys.stderr)

    adapter = load_adapter(target)
    events = []

    for log_file in sorted(logs_path.rglob("*.jsonl")):
        try:
            file_events = adapter.parse(log_file)
            if since:
                file_events = [e for e in file_events if _parse_ts(e.timestamp) >= since]
            if redact:
                file_events = [_redact_event(e) for e in file_events]
            events.extend(file_events)
        except Exception as exc:
            print(f"[workflow-miner] Warning: could not parse {log_file}: {exc}", file=sys.stderr)

    events.sort(key=lambda e: e.timestamp)
    print(f"[workflow-miner] Parsed {len(events)} events from {logs_path}", file=sys.stderr)
    return events


def _parse_ts(ts: str) -> datetime:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


def _redact_event(event: NormalizedEvent) -> NormalizedEvent:
    event.tool_input = {k: "[redacted]" for k in event.tool_input}
    event.tool_output = {k: "[redacted]" for k in event.tool_output}
    event.file_paths = ["[redacted]"] * len(event.file_paths)
    return event


# ─── Segmentation ─────────────────────────────────────────────────────────────


def segment_episodes(events: list[NormalizedEvent], gap_minutes: int = 30) -> list[Episode]:
    if not events:
        return []

    episodes = []
    ep_id = 0
    current_ep_events = [events[0]]

    for prev, curr in zip(events, events[1:]):
        prev_ts = _parse_ts(prev.timestamp)
        curr_ts = _parse_ts(curr.timestamp)
        if (curr_ts - prev_ts) > timedelta(minutes=gap_minutes):
            ep = Episode(
                episode_id=f"ep-{ep_id:03d}",
                session_id=current_ep_events[0].session_id,
                start_time=current_ep_events[0].timestamp,
                end_time=current_ep_events[-1].timestamp,
                events=current_ep_events,
            )
            episodes.append(ep)
            ep_id += 1
            current_ep_events = [curr]
        else:
            current_ep_events.append(curr)

    if current_ep_events:
        episodes.append(Episode(
            episode_id=f"ep-{ep_id:03d}",
            session_id=current_ep_events[0].session_id,
            start_time=current_ep_events[0].timestamp,
            end_time=current_ep_events[-1].timestamp,
            events=current_ep_events,
        ))

    return episodes


# ─── Mining ───────────────────────────────────────────────────────────────────


def mine_sequences(episodes: list[Episode], min_freq: int = 3) -> list[dict]:
    """Extract frequent sequential tool patterns across episodes."""
    seq_counter: Counter = Counter()

    for ep in episodes:
        tools = [e.tool_name for e in ep.events if e.event_type == "tool_call" and e.tool_name]
        # Extract 2-grams and 3-grams
        for n in (2, 3):
            for i in range(len(tools) - n + 1):
                seq = tuple(tools[i:i + n])
                seq_counter[seq] += 1

    return [
        {"sequence": list(seq), "frequency": count}
        for seq, count in seq_counter.most_common(20)
        if count >= min_freq
    ]


def mine_approval_spam(events: list[NormalizedEvent], min_freq: int = 5) -> list[dict]:
    """Find tool calls that always required (and got) approval."""
    approval_map: dict[str, dict] = {}

    for e in events:
        if e.event_type == "tool_call":
            key = e.tool_name
            if key not in approval_map:
                approval_map[key] = {"tool": key, "approval_count": 0, "denied_count": 0}
            if e.approval_required:
                approval_map[key]["approval_count"] += 1
            if e.approval_required and not e.approved:
                approval_map[key]["denied_count"] += 1

    return [
        v for v in approval_map.values()
        if v["approval_count"] >= min_freq
    ]


# ─── Recommendations ──────────────────────────────────────────────────────────

DENYLIST_PATTERNS = ["git push", "rm -rf", "npm publish", "gh release", "deploy", "production"]


def _is_safe(command: str) -> bool:
    return not any(p in command.lower() for p in DENYLIST_PATTERNS)


def generate_recommendations(sequences: list[dict], approval_spam: list[dict]) -> dict:
    custom_commands = []
    auto_allow_rules = []

    for seq in sequences:
        if seq["frequency"] >= 5:
            custom_commands.append({
                "name": "-".join(s.lower() for s in seq["sequence"]),
                "description": f"Run {' → '.join(seq['sequence'])} sequence (seen {seq['frequency']} times)",
                "frequency": seq["frequency"],
                "trigger_pattern": seq["sequence"],
                "confidence": min(0.99, seq["frequency"] / 50),
            })

    for spam in approval_spam:
        tool = spam["tool"]
        total = spam["approval_count"]
        denied = spam["denied_count"]
        approval_rate = (total - denied) / total if total > 0 else 0
        safe = _is_safe(tool) and approval_rate == 1.0

        if approval_rate >= 0.9 and total >= 5:
            auto_allow_rules.append({
                "name": f"allow-{tool.lower().replace(' ', '-')}",
                "description": f"{tool} approved {total - denied}/{total} times",
                "frequency": total,
                "approval_rate": round(approval_rate, 3),
                "rule": f"Bash({tool}*)" if tool == "Bash" else tool,
                "safe": safe,
                "confidence": round(approval_rate * min(1.0, total / 20), 3),
                "warning": None if safe else "Command matches denylist pattern — review before allowing",
            })

    return {
        "custom_commands": custom_commands,
        "post_edit_hooks": [],  # Requires deeper analysis; extend adapters to detect edit→run patterns
        "auto_allow_rules": auto_allow_rules,
    }


# ─── Main ─────────────────────────────────────────────────────────────────────


def parse_duration(s: str) -> datetime:
    """Parse duration like '7d' or '48h' into a cutoff datetime."""
    now = datetime.now(timezone.utc)
    if s.endswith("d"):
        return now - timedelta(days=int(s[:-1]))
    if s.endswith("h"):
        return now - timedelta(hours=int(s[:-1]))
    raise ValueError(f"Invalid duration format: {s!r}. Use e.g. '7d' or '48h'.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Mine AI coding session logs for automation recommendations.")
    parser.add_argument("--target", default="auto", choices=["claude_code", "codex_cli", "opencode", "auto"])
    parser.add_argument("--logs", required=True, help="Directory containing log files")
    parser.add_argument("--since", default=None, help="Only parse logs from last N days/hours (e.g. 7d, 48h)")
    parser.add_argument("--out", default=None, help="Output file path (default: stdout)")
    parser.add_argument("--redact", action="store_true", help="Redact file paths and content")
    args = parser.parse_args()

    logs_path = Path(args.logs).expanduser().resolve()
    if not logs_path.exists():
        print(f"[ERROR] Logs path not found: {logs_path}", file=sys.stderr)
        sys.exit(1)

    since = parse_duration(args.since) if args.since else None

    events = parse_logs(logs_path, args.target, since, args.redact)
    if not events:
        print("[workflow-miner] No events found.", file=sys.stderr)
        sys.exit(0)

    episodes = segment_episodes(events)
    sequences = mine_sequences(episodes)
    approval_spam = mine_approval_spam(events)
    recommendations = generate_recommendations(sequences, approval_spam)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "log_sources": [str(logs_path)],
        "sessions_analysed": len({e.session_id for e in events}),
        "events_processed": len(events),
        "recommendations": recommendations,
        "patterns": sequences,
        "approval_spam": approval_spam,
    }

    result = json.dumps(output, indent=2)
    if args.out:
        Path(args.out).write_text(result)
        print(f"[workflow-miner] Report written to {args.out}", file=sys.stderr)
    else:
        print(result)


if __name__ == "__main__":
    main()
