# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.1.x   | Yes       |
| 1.0.x   | Best effort (upgrade to 1.1.x) |
| < 1.0   | No        |

## Reporting a Vulnerability

Please **do not** open public GitHub issues for security-sensitive reports.

1. Email the maintainers via the contact on the [PyPI project page](https://pypi.org/project/qchem-stack/) or open a private security advisory on [GitHub](https://github.com/sunhl4/qcchem-qml-md/security/advisories/new).
2. Include: affected version, reproduction steps, impact assessment, and suggested fix if available.
3. Expect an initial response within **7 business days**.

## Production Hardening

When exposing the HTTP API or job worker beyond localhost, see [`docs/engineering/production_deployment.md`](docs/engineering/production_deployment.md):

- Set `QCHEM_STACK_REQUIRE_API_KEY=1` and a strong `QCHEM_STACK_API_KEY`
- Set `QCHEM_PROTOCOL_HMAC_KEY` (never use dev defaults)
- Keep `QCHEM_ALLOW_LEGACY_PICKLE=0` in production after blob migration
