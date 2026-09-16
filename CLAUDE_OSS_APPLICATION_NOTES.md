# Open-source program notes

## Public project

- Repository: https://github.com/Nhaooo/agent-company-core
- Documentation: https://nhaooo.github.io/agent-company-core/
- PyPI: https://pypi.org/project/agent-company-core/
- Release: `v0.2.0`, published 2026-09-16
- Installation: `python -m pip install agent-company-core==0.2.0`
- License: Apache-2.0

`agent-company-core` is an early-stage Python framework for durable,
provider-neutral multi-agent workflows. It separates typed model decisions from
the effects an application is allowed to apply. The framework provides
persistent SQLite missions, checkpoints, idempotency, capability-based
delegation, model fallback, risk-aware human approval, persistent STOP and
recovery controls, memory and tool abstractions, and redacted audit events.

The v0.2.0 onboarding path adds an offline `agent-company demo`, a small
`agent-company init` scaffold, an operator-oriented `doctor` command, optional
Anthropic Claude and generic OpenAI-compatible adapters, a documented Ollama
path through the compatible endpoint, and runnable examples covering durable
missions, delegation, approvals, STOP/recovery, tools, providers, a generic
research team, and FastAPI.

The core and CI remain credential-free. Provider adapters are tested with
injected fakes; no paid live provider call is required. The restricted local
runner is experimental and disabled by default; it is not a hostile-code
sandbox and does not provide OS, container, or VM isolation.

## Quality and security evidence

- Main CI: green on Python 3.11, 3.12, 3.13, and Windows Python 3.13; the
  package/offline smoke job also passes.
- Release CI: green for `v0.2.0`, including 29 tests, Ruff, strict mypy,
  fallback scan, wheel/sdist build, Twine validation, and the offline example
  smoke suite.
- Secret scanning: official Gitleaks and the dependency-free fallback pass with
  zero findings on the tracked tree and complete Git history.
- Dependency audit: `pip-audit` reports no unresolved known vulnerability in
  the resolved development environment.
- Supply chain: Dependabot, secret scanning, push protection, and an OpenSSF
  Scorecard workflow are enabled where the repository plan supports them.
- Publishing: PyPI Trusted Publishing/OIDC uses the dedicated `pypi` GitHub
  environment and `release.yml`; no long-lived PyPI token is used.

## Current public metrics

These are point-in-time public values checked on 2026-09-16. They are not
targets and no artificial activity was created.

| Metric | Value | Notes |
| --- | ---: | --- |
| GitHub stars | 1 | GitHub repository API |
| GitHub forks | 0 | GitHub repository API |
| Repository contributors | 1 | The repository contributor list contains only `Nhaooo` |
| Merged external PRs | 0 | Merged PRs are maintainer-authored |
| Open contributor issues | 10 | Issues 7 through 16; all are genuine remaining roadmap work |
| `good first issue` issues | 4 | Issues 7, 8, 9, and 13 |
| `help wanted` issues | 3 | Issues 11, 14, and 15 |
| Releases | 2 | `v0.1.0` and `v0.2.0` |
| PyPI downloads | unknown | Public statistics endpoint was rate-limited during this check |
| Dependent repositories | unknown | GitHub dependents endpoint was unavailable to this account |
| OpenSSF Scorecard score | unknown | The workflow is green; a score was not recorded |

Four automated Dependabot pull requests are currently open; they are not
counted as contributor issues or external contributors.

## Why Claude Max would materially benefit this project

Claude Max would support legitimate maintainer work with high context demand:

- implementing and testing additional provider integrations while preserving
  the provider-neutral core;
- reviewing larger multi-file contributor PRs and keeping strict typing and
  safety invariants intact;
- building the PostgreSQL and Temporal reference integrations listed in the
  roadmap;
- improving contributor documentation, examples, and conformance fixtures;
- performing deeper security, dependency, and supply-chain reviews;
- investigating real upstream issues in dependencies when a reproducible,
  useful contribution is available.

The benefit would be maintainer throughput and review quality, not fabricated
adoption. No Anthropic application has been submitted as part of this work.

## Current weaknesses and honest next steps

The project is still alpha software with no measured external adoption beyond
the public metrics above. It has one default SQLite store, no full PostgreSQL
store, no complete Temporal worker package, and no MCP, Redis, or OpenTelemetry
export implementation. The optional Claude adapter is present and mocked in
CI, but live provider compatibility is deliberately not asserted without a
safe, explicit API call. The local restricted runner must not be described as
a sandbox. The next legitimate growth steps are useful contributors, tested
integrations, and feedback from developers who build real agent workflows.
