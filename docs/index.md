# agent-company-core

An alpha Python framework for durable, policy-aware multi-agent workflows.
Bring your own model, keep missions in durable storage, and make the boundary
between a model decision and an application effect explicit.

```powershell
python -m pip install agent-company-core
agent-company demo
```

The demo is deterministic and offline. It exercises mission persistence,
capability delegation, typed decisions, audit events, approval, and STOP.

## Start here

- [Quickstart](quickstart.md) for the first library mission.
- [Provider matrix](providers.md) for optional model adapters.
- [Examples](examples.md) for complete small workflows.
- [Architecture](development/architecture.md) before changing the core.
- [Security](security.md) before enabling consequential effects.
