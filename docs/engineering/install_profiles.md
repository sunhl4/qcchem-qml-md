# Install profiles

Matrix of supported `pip install` combinations. See also [pypi_release.md](pypi_release.md).

| Profile | Extras | Python | OS | Use case |
|---------|--------|--------|-----|----------|
| minimal | *(core)* | 3.10–3.12 | linux / mac / win | Precomputed pipeline, strict repro export |
| chem | `chem` | 3.10–3.12 | linux (PySCF wheels) | Live PySCF SCF + Hamiltonian build |
| quantum | `chem,quantum` | 3.10–3.12 | linux | VQE/ADAPT + Qiskit Aer |
| api | `chem,quantum,api` | 3.12 | linux | HTTP API + SQLite worker |
| full | `dev` (+ optional `pytket,nexus`) | 3.12 | linux | Maintainer / **`release_precheck.sh`** (requires ruff, pyright, pip-audit, pytest-cov) |
| md-classical | `chem` only | 3.12 | linux | Classical H₂ FF + QMEF (no QML-FF). **Profile name, not a pip extra.** |
| all | `all` = chem,quantum,pytket,nexus | 3.12 | linux | Full open-stack surface without UQC |
| all-cloud | `all-cloud` = all + uqc | 3.12 | linux | Experimental UQC cloud client |
| jobs-postgres | `api,jobs-postgres` | 3.12 | linux | HA worker with Postgres job ledger |
| observability | `observability` | 3.12 | linux | OTLP export for pipeline events |

## Extras notes

- **`dev`** installs `chem,quantum,api` plus test/lint tools — **does not** pull `uqc` or `all`.
- **`dev-uqc`** = `dev` + experimental `uqc` (see [SECURITY.md](../../SECURITY.md) for CVE allowlist scope).
- **`all`** = `chem,quantum,pytket,nexus` (no uqc). Use **`all-cloud`** when you need UQC.
- **`md-classical`** is only a documentation profile: `pip install -e ".[chem]"` (classical MD bridge ships in core / chem; there is no empty `md-classical` extra).

## Examples

```bash
pip install -e ".[chem,dev]"
pip install -e ".[chem,quantum,api,jobs-postgres]"
pip install -e ".[dev,observability]"
pip install -e ".[all]"
pip install -e ".[all-cloud]"   # experimental UQC
pip install -e ".[dev-uqc]"     # maintainer tools + UQC
```

QML-FF remains a sibling editable install; see root [README.md](../../README.md).

## Local Postgres conformance (optional)

Run job-store protocol tests against Postgres without CI:

```bash
docker compose up -d postgres   # see docker-compose.yml
export QCHEM_JOB_DATABASE_URL=postgresql://qchem:qchem@127.0.0.1:5432/qchem_jobs  # pragma: allowlist secret
pytest tests/jobs/test_job_store_protocol_conformance.py -q
```

See [`job_store_extension.md`](job_store_extension.md).
