# Roadmap

## Shipped in 0.2.0

- Optional Anthropic Claude and OpenAI-compatible model adapters.
- Offline-first CLI, starter scaffold, provider matrix, and runnable examples.
- MkDocs documentation structure and multi-version CI with package smoke tests.
- Accurate provider error handling and explicit SQLite connection cleanup.

## 0.2.x

- Conformance fixtures for additional stores and providers.
- Better event querying/filtering and richer CLI diagnostics.
- Improve memory ranking and add an embedding-backed implementation.
- Add operator authentication hooks around approval resolution.

## 0.3

- Full PostgreSQL durable repository with migrations and integration tests.
- Tested Temporal worker/reference workflow package with deterministic replay
  fixtures.
- Optional OpenTelemetry export with documented data minimization.
- Additional local/provider adapters only when they share a stable contract.

## Future

- Container-backed skill execution with documented isolation guarantees.
- Redis-backed coordination where the consistency model is explicit.
- Reference UI and operational metrics that never imply work not actually run.

Community contribution opportunities are kept as open GitHub issues and are
only created for work that remains genuinely unimplemented. The order is
provisional; no adoption, performance, or compatibility claim is made until it
is measured and documented.
