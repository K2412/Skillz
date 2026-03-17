# Normalized Event Schema

All log adapters must produce a list of `NormalizedEvent` objects. This schema decouples the mining logic from log format specifics.

## NormalizedEvent Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `timestamp` | ISO 8601 string | yes | When the event occurred |
| `session_id` | string | yes | Unique identifier for the session/conversation |
| `event_type` | enum | yes | See event types below |
| `tool_name` | string | no | Tool invoked (for tool_call/tool_result events) |
| `tool_input` | dict | no | Tool input parameters (redacted if --redact) |
| `tool_output` | dict | no | Tool result summary (redacted if --redact) |
| `approval_required` | bool | no | Whether this tool call required user approval |
| `approved` | bool | no | Whether the user approved it |
| `duration_ms` | int | no | How long the tool call took |
| `file_paths` | list[str] | no | File paths involved (redacted if --redact) |
| `exit_code` | int | no | Exit code for bash/script events |

## Event Types

| Type | Description |
|---|---|
| `tool_call` | Agent requested a tool |
| `tool_result` | Tool returned a result |
| `user_message` | User sent a message |
| `assistant_message` | Agent produced output |
| `approval_request` | Agent requested approval for a tool |
| `approval_granted` | User granted approval |
| `approval_denied` | User denied approval |
| `session_start` | Session/conversation began |
| `session_end` | Session/conversation ended |

## Episode Segmentation

Events are grouped into **episodes** — contiguous sequences of tool calls addressing the same task. Episode boundaries are detected by:

- Time gap > 30 minutes between events
- User message that starts with a new goal (heuristic: no reference to prior context)
- `session_start` event

## Example (Python dataclass)

```python
@dataclass
class NormalizedEvent:
    timestamp: str          # "2026-03-14T10:23:45Z"
    session_id: str         # "proj-abc123"
    event_type: str         # "tool_call"
    tool_name: str = ""     # "Bash"
    tool_input: dict = field(default_factory=dict)
    tool_output: dict = field(default_factory=dict)
    approval_required: bool = False
    approved: bool = False
    duration_ms: int = 0
    file_paths: list = field(default_factory=list)
    exit_code: int | None = None
```
