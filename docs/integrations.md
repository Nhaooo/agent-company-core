# Integrations

The core package is deliberately provider-neutral. Integrations are adapters,
not hidden dependencies of `MissionEngine`.

## Google Gen AI

Install `agent-company-core[google]`, create `GoogleModel(model=...)`, and
provide credentials through the host application's normal Google credential
chain. Do not put credential material in configuration committed to Git.

## Temporal

Install `agent-company-core[temporal]` and use `connect_temporal(...)` as a
client gateway. A host application owns its workflow definitions and must
follow Temporal's deterministic workflow rules. The compact local engine does
not claim Temporal durability guarantees.

## PostgreSQL

Install `agent-company-core[postgres]`. The current release exposes a
dependency check/extension boundary; the default durable repository remains
SQLite. A production PostgreSQL repository is planned and is not claimed as
implemented in version 0.1.0.
