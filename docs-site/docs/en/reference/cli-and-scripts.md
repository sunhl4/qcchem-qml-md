---
title: CLI & scripts
description: Console entry points after install and common repo scripts/
---

Commands you use day-to-day; **authoritative flags** are in `qchem_qml_md/README.md` and source `argparse` handlers.

## Install (pip)

From the repo root `qchem_qml_md/`:

```bash
pip install -e ".[dev]"
```

Optional: `pip install -e ".[all]"` (PySCF, Qiskit, pytket, …), `pip install -e ".[api]"` (FastAPI stack).

## Package entry points (`pyproject.toml` · `[project.scripts]`)

After install:

| Command | Role |
|---------|------|
| `qchem-jobs-worker` | Poll SQLite job store and run `QUEUED` jobs (same as `qchem-pipeline-worker`) |
| `qchem-pipeline-worker` | Same as above |

Example:

```bash
qchem-jobs-worker --db ./jobs.sqlite --sleep 0.5
```

Flags: `--db` (required), `--sleep` (seconds when queue empty, default `0.5`), `--max-retries` (default `2`). Source: `src/qchem_stack/jobs/worker.py`.

## Local HTTP (uvicorn)

Requires the `[api]` extra:

```bash
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

Endpoints: [HTTP API · SQLite jobs](/en/reference/http-api-sqlite-jobs).

## Repo `scripts/` (run with `python` from clone root)

Use an environment where `qchem_stack` is importable.

| Script | Purpose |
|--------|---------|
| `python scripts/smoke_pipeline.py` | Smoke run (default `configs/example_h2.yaml`); flags such as `--excited`, `--sampled`, `--qiskit-shots`, `--iqeb`, `--projection-trace` (see file docstring) |
| `python scripts/export_parity_criteria_table.py <config.yaml>` | Export parity / Methods-oriented field table; optional `--results out.json` |
| `python scripts/check_parity_export_sample.py` | Validate export samples (CI helper) |
| `python scripts/check_solver_adapter_contract.py [config.yaml]` | Validate backend adapter contract for current `scf.driver`; supports `--driver`, `--run-mean-field`, `--require-mean-field-success` |
| `python scripts/create_solver_adapter_scaffold.py <backend_id>` | Generate a solver scaffold (TODO[1/2/3]) and print register/check commands; add `--with-demo-register` to emit `scripts/register_<backend>_demo.py` (in-process contract checks) |
| `python scripts/demo_mock_external_backend.py` | Run a copyable custom-backend example: register `mock_external` and execute one plugin-path pipeline run |
| `python scripts/run_qpe_track_demo.py` | QPE track demo (optional) |
| `python scripts/resource_estimation_demo.py` | Resource demo (optional) |

One-line adapter debug helper:

```bash
python -c "from qchem_stack.chem.solvers import create_solver; from qchem_stack.config import load_experiment_config; c=load_experiment_config('configs/example_h2.yaml'); print(create_solver(c).capabilities)"
```

## Python API (not a shell CLI)

See [15-minute quickstart](/en/tutorial/quickstart):

```python
from pathlib import Path
from qchem_stack.orchestration.pipeline import run_pipeline_from_config

out = run_pipeline_from_config("configs/example_h2.yaml", job_db=Path("jobs.sqlite"))
```

## See also

- [Guides overview](/en/guide/) — feature pillars  
- [HTTP API](/en/reference/http-api-sqlite-jobs) — REST and job lifecycle  
