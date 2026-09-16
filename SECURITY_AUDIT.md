# Security audit

The public repository has a separate Git history and contains no private
source history, internal runtime data, or copied internal report. The review
below covers the v0.2.0 release candidate on 2026-09-16.

## Findings

- Actual secret values: 0 found.
- Credential files, `.env` files, service-account JSON, and private keys: 0
  found.
- Personal absolute paths, personal usernames, and private project identifiers:
  0 found.
- Private source-repository identifiers and internal persona names: 0 found.
- Private URLs or personal email addresses: 0 found.
- Tracked files reviewed: 133.

The generic matches for `secret`, `token`, `password`, `credential`, and API
key names are documentation, environment-variable names, redaction rules,
workflow permission names, or safe test fixtures. The local Ollama key value is
an explicit non-secret placeholder. No real value is present in source,
examples, tests, logs, or documentation.

## Scanner evidence

Official Gitleaks v8.30.1 was run with redacted output against both the current
working tree and the complete Git history of this repository:

- Working tree: PASS, 0 findings.
- Full history: PASS, 0 findings across all 13 commits.
- Dependency-free fallback scanner: PASS, 0 findings in all 133 tracked files.

No secret value is reproduced in this document or in scan output.

## Runtime and provider boundary

The restricted local runner is experimental, disabled by default, and is not a
hostile-code sandbox. It does not provide OS, container, or VM isolation.
Untrusted code requires a separately isolated execution service. Optional
provider adapters read credentials from the host application's standard
configuration and never print them. Provider tests use injected fakes and do
not make paid or network calls.

## Dependencies and licensing

`pip-audit` found no unresolved known vulnerability in the resolved test
environment. Provider SDKs and integrations remain optional. No third-party
source is copied; dependency notices and licenses remain the responsibility of
their respective licensors as described in `THIRD_PARTY_NOTICES.md`.

The v0.2.0 release is not complete until the release workflow passes its
credential-free tests and the PyPI Trusted Publishing identity remains exact.
