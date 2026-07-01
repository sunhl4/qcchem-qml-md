# Install profiles

Matrix of supported `pip install` combinations. See also [pypi_release.md](pypi_release.md).

| Profile | Extras | Python | OS | Use case |
|---------|--------|--------|-----|----------|
| minimal | *(core)* | 3.10–3.12 | linux / mac / win | Precomputed pipeline, strict repro export |
| chem | `chem` | 3.10–3.12 | linux (PySCF wheels) | Live PySCF SCF + Hamiltonian build |
| quantum | `chem,quantum` | 3.10–3.12 | linux | VQE/ADAPT + Qiskit Aer |
| api | `chem,quantum,api` | 3.12 | linux | HTTP API + SQLite worker |
| full | `all,api,dev` | 3.12 | linux | Maintainer / **`release_precheck.sh`** (requires ruff, pyright, pip-audit, pytest-cov) |
| md-classical | `chem,md-classical` | 3.12 | linux | Classical H₂ FF + QMEF (no QML-FF) |
| jobs-postgres | `api,jobs-postgres` | 3.12 | linux | HA worker with Postgres job ledger |
| observability | `observability` | 3.12 | linux | OTLP export for pipeline events |

## Examples

```bash
pip install -e ".[chem,dev]"
pip install -e ".[chem,quantum,api,jobs-postgres]"
pip install -e ".[dev,observability]"
```

QML-FF remains a sibling editable install; see root [README.md](../../README.md).

## Local Postgres conformance (optional)

Run job-store protocol tests against Postgres without CI:

```bash
docker compose up -d postgres   # see docker-compose.yml
export QCHEM_JOB_DATABASE_URL=postgresql://qchem:qchem@127.0.0.1:5432/qchem_jobs
pytest tests/jobs/test_job_store_protocol_conformance.py -q
```

See [`job_store_extension.md`](job_store_extension.md).
