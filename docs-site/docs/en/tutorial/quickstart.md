# 15-minute quickstart

Excerpted from the repo `README`. **Authoritative install / parameters live in `qchem_qml_md/README.md`** — please double-check against the source.

## 1. Install

```bash
cd qchem_qml_md
pip install -e ".[dev]"
```

`pip install -e ".[all]"` pulls every declared extra (PySCF, Qiskit, pytket, FastAPI).

## 2. Minimal end-to-end (YAML)

```python
from pathlib import Path
from qchem_stack.orchestration.pipeline import run_pipeline_from_config

out = run_pipeline_from_config("configs/example_h2.yaml", job_db=Path("jobs.sqlite"))
# out: scf_energy, variational energy, Pauli protocol, resource_summary, repro, job_result
```

## 3. Optional HTTP API

```bash
pip install -e ".[api]"
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

Contract and endpoints: see [HTTP API · SQLite jobs](/en/reference/http-api-sqlite-jobs).

## Next

- [Guides overview](/en/guide/)
- [Public parity matrix](/en/parity/public-matrix)
- [Engineering architecture](/en/concept/engineering-architecture)
