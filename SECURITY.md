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
- Set `QCHEM_QUANTUM_STRICT=1` to reject custom `quantum.algorithm_factory` import paths so only built-in registered algorithm ids are accepted (prevents arbitrary `module:callable` imports from YAML in production). Operator-pool ids are already validated in all modes.

## UQC (experimental) and pip-audit allowlist

The **`uqc`** extra (and **`all-cloud`** / **`dev-uqc`**) pulls the experimental UQC cloud client and its transitive pins (notably `aiohttp` / `python-socketio`). Those pins currently require CVE ignore entries in [`pip-audit.toml`](pip-audit.toml).

- Core CI **`security-audit`** installs `.[dev]` **without** UQC and runs `pip-audit` **without** the allowlist.
- Optional **`security-audit-uqc`** installs `.[dev-uqc]` and applies `pip-audit.toml` ignores only on that job.
- Do **not** add direct-dependency CVEs to the allowlist; drop UQC-related ignores once upstream relaxes pins.
