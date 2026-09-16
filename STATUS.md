# Status

The v0.2.0 impact sprint is implemented on a clean release-candidate tree.
The public GitHub repository and PyPI package `agent-company-core==0.1.0`
remain live; v0.2.0 is pending its deliberate GitHub Release trigger.

The candidate includes optional Anthropic and OpenAI-compatible adapters, an
offline CLI and starter scaffold, ten runnable examples, a MkDocs site, a
provider matrix, multi-version CI, Dependabot, Scorecard, and package smoke
tests. The 29-test suite, Ruff, strict mypy, package build, Twine metadata
validation, pip-audit, fallback scan, and official Gitleaks scans pass. The
restricted runner remains disabled by default and is explicitly not a
hostile-code sandbox.
