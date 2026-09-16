# Anthropic Claude

Demonstrates the optional `AnthropicModel`, typed `AgentDecision`, durable
mission state, and the engine's normal policy boundary.

Prerequisites: core package for the default mocked run. For a live call, also
install `agent-company-core[anthropic]`, set `ANTHROPIC_API_KEY`, optionally set
`ANTHROPIC_MODEL`, and pass `--live`.

```powershell
python examples/anthropic_claude/main.py
python examples/anthropic_claude/main.py --live
```

The default run injects a fake async Messages client and makes no network or
paid API call. Model IDs are configurable; `claude-sonnet-4-6` is only the
documented current example and should be checked against Anthropic's catalog.
