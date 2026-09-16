# Open-source program notes

`agent-company-core` is an alpha, locally testable Python framework for
durable multi-agent orchestration. Its technical value is the explicit seam
between a model's typed decision and the effects applied by an engine. That
seam supports mission persistence, idempotency keys, checkpoints, risk-based
human approval, persistent STOP, provider-neutral routing, memory interfaces,
tool contracts, and redacted audit records.

The repository contains a deterministic fake model so the core suite runs
without cloud credentials or paid APIs. Optional integrations are clearly
separated and are not represented as available unless their adapter is
installed and exercised.

Publication record:

- Public repository: https://github.com/Nhaooo/agent-company-core
- Public package: https://pypi.org/project/agent-company-core/
- Release: `v0.1.0`, published 2026-09-16
- Installation: `pip install agent-company-core==0.1.0`
- License: Apache-2.0
- CI: main and release workflows green; release validation included 20 passing
  tests, Ruff, mypy, build, metadata validation, and fallback secret scan.
- Public functionality: typed durable mission orchestration, checkpoints,
  capability-based delegation, provider-neutral routing, approval/risk
  boundaries, persistent STOP controls, memory/audit/tool abstractions, a
  deterministic local fake model, and optional integration boundaries.

Adoption metrics are intentionally factual only: stars, users, downloads,
contributors, dependent repositories, and external endorsements are currently
zero or unknown; no adoption claim is made.
