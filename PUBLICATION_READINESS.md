# Publication readiness

Status is based on local evidence from this extraction. `NEEDS HUMAN REVIEW`
means the owner must make the final decision; it is not a hidden pass.

| Area | Status | Evidence / follow-up |
| --- | --- | --- |
| Apache-2.0 license | PASS | `LICENSE` present; original source only |
| Secret scan | PASS | dependency-free fallback reports 0 findings; gitleaks is not installed locally and remains a human pre-publication check |
| PII/local-path scan | PASS | new tracked tree contains no personal paths or identities |
| Tests | PASS | `uv run --extra dev --extra app pytest`: 20 passed |
| Lint | PASS | Ruff check passes locally |
| Type checking | PASS | mypy strict check passes locally |
| Package build | PASS | `uv build` produced wheel and sdist; `twine check` passed |
| Dependency audit | PASS | `pip-audit --local` found no known vulnerabilities; local unpublished package was skipped |
| Third-party licensing | NEEDS HUMAN REVIEW | no copied source; resolve dependency notices before release |
| Documentation | PASS | README, security, contributor, roadmap, provenance docs present |
| Provider neutrality | PASS | core imports no provider SDK; Google adapter is optional |
| Security model | PASS | approval, STOP, redaction, runner threat model documented |
| PyPI readiness | NEEDS HUMAN REVIEW | owner must review metadata and test distributions |
| GitHub readiness | NEEDS HUMAN REVIEW | owner must create repository, configure security contact, and review CI |

No publication command was executed.

## Name check

At the local check on 2026-09-16, the exact PyPI and GitHub URLs for
`agent-company-core` returned 404. Similar names exist, so these are retained
as contingency choices if the owner finds a conflict during publication:

- `durable-agent-core`
- `agent-orchestration-core`
- `policy-agent-runtime`
- `mission-agent-core`
- `durable-multiagent`
