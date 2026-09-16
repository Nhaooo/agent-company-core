# Security audit

The new repository was built separately from the private source repository and
contains a fresh Git history. A tracked-file review was run with searches for
credential markers, private keys, cloud project identifiers, personal paths,
private emails, private personas, and internal branding.

Result for the tracked public tree at finalization time:

- Actual secret values: 0 found.
- Credential files or `.env` files: 0 found.
- Personal absolute paths or usernames: 0 found.
- Private personas/internal branding: 0 intended occurrences.
- External publication: not performed.

The dependency-free fallback scanner was run against 73 tracked files and
reported zero secret-pattern findings. Gitleaks v8.30.1 was then installed from
the official release (with a matching published SHA-256 checksum) and run
against both the publication tree and the complete Git history. The final
result was zero findings in both scans across all 5 commits. An initial tree
scan reported 200 `generic-api-key` alerts only in the ignored local virtualenv
file `.venv/Lib/site-packages/license_expression/data/scancode-licensedb-index.json`;
that generated environment was removed and the publication-tree scan was
rerun clean. No finding came from a tracked or committed repository file.

The tracked tree was also searched for personal names, Windows paths, private
repository identifiers, service-account markers, private keys, credential
markers, and email addresses. Matches that remain are generic security
documentation, redaction rules, safe test placeholders, or public dependency
URLs; no personal or private value was found.

The strings in this document and the security documentation describe generic
threat categories only. Gitleaks findings were reviewed by rule and path; no
secret value is reproduced in this audit.
