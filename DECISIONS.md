# Decisions

## Fresh public repository

The public repository is a separate fresh Git history so private source
history, internal runtime data, and unrelated worktree state cannot be
published accidentally. The private `AI-COMPANY` repository is not a remote
for this repository and is not modified by the publication process.

## OIDC-only PyPI publishing

PyPI publication uses the dedicated `pypi` GitHub environment and PyPA's
Trusted Publishing action with job-scoped `id-token: write`. No long-lived
PyPI API token is used or stored.

## Restricted runner terminology

The local skill runner is documented as an experimental restricted runner,
disabled by default and not a hostile-code sandbox. A separately isolated
execution service is required for untrusted code.
