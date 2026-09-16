# Publication readiness

Status is based on local evidence from this extraction. `NEEDS HUMAN REVIEW`
means the owner must make the final decision; it is not a hidden pass.

| Area | Status | Evidence / follow-up |
| --- | --- | --- |
| Apache-2.0 license | PASS | `LICENSE` present; original source only |
| Secret scan | NEEDS HUMAN REVIEW | local regex scan below; run gitleaks before publication |
| PII/local-path scan | PASS | new tracked tree contains no personal paths or identities |
| Tests | PASS | local core suite currently passes |
| Lint | PASS | Ruff check passes locally |
| Type checking | PASS | mypy strict check passes locally |
| Package build | NEEDS HUMAN REVIEW | run `uv build` and `twine check dist/*` on release machine |
| Dependency audit | NEEDS HUMAN REVIEW | run `pip-audit` with a fresh lock/resolution |
| Third-party licensing | NEEDS HUMAN REVIEW | no copied source; resolve dependency notices before release |
| Documentation | PASS | README, security, contributor, roadmap, provenance docs present |
| Provider neutrality | PASS | core imports no provider SDK; Google adapter is optional |
| Security model | PASS | approval, STOP, redaction, runner threat model documented |
| PyPI readiness | NEEDS HUMAN REVIEW | owner must review metadata and test distributions |
| GitHub readiness | NEEDS HUMAN REVIEW | owner must create repository, configure security contact, and review CI |

No publication command was executed.
