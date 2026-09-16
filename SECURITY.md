# Security policy

This project is alpha and should be threat-modeled by the application owner
before use with sensitive data or consequential actions.

## Reporting

Do not disclose an unpatched vulnerability in a public issue. Use GitHub's
private vulnerability reporting channel when enabled, or contact the
maintainer privately through the [Nhaooo GitHub profile](https://github.com/Nhaooo).
Never include credentials or sensitive production data in a report.

## Current model

- `Policy` evaluates structured `ActionRequest` values and can require a
  human approval for high-risk or explicitly listed actions.
- Approval resolution is exact-match and time-limited; modified arguments do
  not silently broaden an approved effect.
- `StopControl` is a persistent operator signal checked before model and tool
  execution. It is a control boundary, not a guarantee that an already-issued
  external request can be recalled.
- Audit events are JSONL and recursively redact common secret keys and token
  patterns. Redaction is defense in depth, not a replacement for access
  controls.

## Skill runner threat model

`RestrictedRunner` is an experimental local runner, not a secure sandbox. It
requires both `allow_execution=True` and `trusted=True`, validates that the
entrypoint is below a configured root, limits the executable to an explicit
allowlist, and enforces a timeout. It does not provide OS/container isolation,
resource quotas, or protection from hostile trusted code. Keep it disabled for
untrusted input and use a separately isolated execution service when needed.

## Scope boundaries

No credentials, service-account files, private URLs, local user paths, or
runtime state belong in the repository. PostgreSQL, Temporal, browser
automation, and provider adapters are optional and inherit the host
application's security responsibilities.
