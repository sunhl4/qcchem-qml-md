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

## 4. Common commands (cheat sheet)

| Task | Command |
|------|---------|
| Drain queued jobs from SQLite | `qchem-jobs-worker --db ./jobs.sqlite` (same as `qchem-pipeline-worker`) |
| Run the local API | `uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000` |
| Repo smoke test | `python scripts/smoke_pipeline.py` (flags like `--sampled`, `--qiskit-shots`, …) |

Full list: **[CLI & scripts](/en/reference/cli-and-scripts)**.

## Next

- [Product features](/en/product/features)  
- [Workflow & YAML](/en/tutorial/workflow-overview)  
- [Guides overview](/en/guide/)  
- [CLI & scripts](/en/reference/cli-and-scripts) · [HTTP API](/en/reference/http-api-sqlite-jobs)  
- Deeper: [Principles & reading](/en/guide/principles-and-reading); internal benchmark: [Positioning & roadmap](/en/product/)  
