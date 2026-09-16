# Publication readiness

This record describes the v0.2.0 release candidate on 2026-09-16. The
existing v0.1.0 release remains public; the v0.2.0 GitHub release and PyPI
publication are intentionally performed only after the gates below pass.

| Area | Status | Evidence / follow-up |
| --- | --- | --- |
| Apache-2.0 license | PASS | `LICENSE` is present and GitHub recognizes Apache-2.0. |
| Secret scan | PASS | Official Gitleaks v8.30.1 reports 0 findings in the working tree and across all 16 Git commits; the dependency-free fallback also reports 0 findings in 133 tracked files. |
| PII/local-path scan | PASS | Tracked filenames and content contain no personal username, absolute user path, private project identifier, or private source-repository name. Generic security terms and safe test placeholders were reviewed. |
| Tests | PASS | GitHub main and PR CI pass; 29 tests pass with one existing Starlette deprecation warning. |
| Lint | PASS | Ruff check passes in local and GitHub CI. |
| Type checking | PASS | Strict mypy passes in local and GitHub CI. |
| Package build | PASS | Wheel and sdist build; Twine metadata check passes; both artifacts install and run the offline CLI demo. |
| Dependency audit | PASS | `pip-audit` reports no unresolved known vulnerability in the resolved environment. |
| Third-party licensing | PASS | No third-party source is copied; resolved dependency licenses were inspected and notices remain attributable to their licensors. |
| Documentation | PASS | README, MkDocs site, provider guides, examples, security, contributor, roadmap, and changelog are present. |
| Provider neutrality | PASS | Anthropic and OpenAI-compatible SDKs are optional; core imports no provider SDK. |
| Security model | PASS | Approval, STOP, redaction, and the disabled-by-default restricted runner threat model are documented accurately. |
| GitHub readiness | PASS | Public repository, Apache-2.0 recognition, Dependabot, secret scanning, push protection, Scorecard, Pages, and green main CI are configured. |
| PyPI Trusted Publishing | PASS | Dedicated `pypi` environment and OIDC release workflow are configured for owner `Nhaooo`, repository `agent-company-core`, workflow `release.yml`. The v0.2.0 release trigger remains pending. |
| Name check | PASS | The exact GitHub and PyPI names are now occupied by this intended project; no unrelated conflict was found before publication. |

## Finalization controls

- Gitleaks binary: official v8.30.1 Windows x64 release, checksum verified.
- Working-tree scan: PASS, 0 findings.
- Full-history scan: PASS, 0 findings across all 16 commits in this new
  repository.
- Fallback scan: PASS, 0 findings in 133 tracked files.
- Release workflow: `.github/workflows/release.yml` builds and validates from
  the GitHub Release, then publishes through PyPI Trusted Publishing using the
  `pypi` environment and job-scoped OIDC permission.

## Published baseline and pending release

- GitHub: https://github.com/Nhaooo/agent-company-core
- Existing release: https://github.com/Nhaooo/agent-company-core/releases/tag/v0.1.0
- PyPI: https://pypi.org/project/agent-company-core/
- Candidate package: `agent-company-core`, version `0.2.0`
- Candidate publisher identity: GitHub owner `Nhaooo`, repository
  `agent-company-core`, workflow `release.yml`, environment `pypi`.

The v0.2.0 release must not be created until the working tree is clean, main
CI is green, and the release workflow identity still matches this record.
