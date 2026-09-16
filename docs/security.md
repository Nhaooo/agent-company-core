# Security

The project is alpha and does not replace an application threat model.

- Approval is exact-match and risk-aware, but operator authentication belongs
  to the host application.
- STOP is a persistent local signal and cannot recall an already-issued remote
  request.
- Audit logging redacts common token/key patterns as defense in depth; protect
  the audit file and underlying runtime directory.
- `RestrictedRunner` is an experimental local runner, disabled by default. It
  is not a secure sandbox and provides no OS/container isolation.
- Optional provider SDKs inherit the host application's credential, network,
  retention, and data residency responsibilities.

Keep secrets out of source, examples, logs, issue bodies, and generated runtime
files. Report unpatched vulnerabilities privately rather than in a public issue.
