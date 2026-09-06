# Automatic workflow-memory release gate

Run the combined gate from the Skillz repository with the existing `agent-memory` checkout supplying
the MCP SDK and public daemon executable:

```bash
uv run --project ../agent-memory python -m workflow_memory_release.evaluate \
  --agent-memory-source ../agent-memory \
  --state-dir /tmp/workflow-memory-release-state \
  --report /tmp/workflow-memory-release-report.json
```

The state directory must not exist. The command runs each materialized workflow instruction through
Claude Code's non-interactive runner with authoritative fixtures and an instrumented fake MCP server.
It scores the server's observed calls rather than generated prose. It then seeds a new encrypted
database through public MCP operations and scores the checked-in queries independently of generated
output. Because the public daemon owns the fixed loopback port, the harness records whether the user
LaunchAgent is running, stops it while the isolated daemon owns the port, and restores it in `finally`.

The command refuses activation unless recall-at-five is at least 90 percent, project and inactive
leaks are both zero, every workflow guard passes, and exactly the released skills (`pair` and `teach`)
request the active byte-equivalent shared reference. Installation also refuses before its first
mutation unless the checked-in passing report names exactly those workflows, meets the thresholds, and
matches both fixture hashes. The report contains identifiers, ranks, versions, settings, counts, and latency only;
it contains no claim, evidence, prompt, or generated response content.
