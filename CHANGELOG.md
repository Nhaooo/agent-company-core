# Changelog

## 0.2.0 - 2026-09-16

### Added

- Added optional Anthropic Claude and generic OpenAI-compatible async adapters
  with configurable model IDs, structured decision validation, normalized
  timeout/error handling, and injected-client tests.
- Added the offline-first `agent-company` CLI with `doctor`, `demo`, `init`, and
  `run` commands.
- Added a local Ollama path through the OpenAI-compatible adapter.
- Added focused runnable examples for missions, approvals, STOP/recovery,
  delegation, tools, custom providers, providers, FastAPI, and a research team.
- Added a lightweight MkDocs site, provider/feature matrices, architecture
  notes, contributor guidance, and reproducible example/package smoke checks.

### Changed

- Made `pip install agent-company-core` the primary onboarding path and exposed
  project, documentation, changelog, and issue URLs in package metadata.
- Expanded CI across Python 3.11, 3.12, and 3.13 on Linux plus a Windows job,
  and added offline wheel/sdist CLI smoke tests.
- Closed SQLite connections explicitly so short-lived applications can cleanly
  remove or rotate runtime directories on Windows.

### Security

- Kept provider SDKs optional and credentials out of examples and CI.
- Provider and mission errors no longer persist raw provider error text in the
  audit log.
- Added least-privilege documentation deployment and OpenSSF Scorecard
  workflows with immutable action references.

## 0.1.0 - 2026-09-16

- Initial local alpha release of the provider-neutral orchestration core.
- Added durable SQLite missions, events, checkpoints, approvals, and memory.
- Added structured routing, neutral agent selection, tool registry, STOP, and
  redacted audit logging.
- Added optional Google, Temporal, and PostgreSQL integration boundaries.
- Added a fake-model reference application and contributor/security docs.
