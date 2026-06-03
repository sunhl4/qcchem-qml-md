# Contributor quick start (English)

Shortest path from a YAML experiment to understanding pipeline output. For full architecture see
[`docs/ENGINEERING_ARCHITECTURE.md`](ENGINEERING_ARCHITECTURE.md).

**Role-based onboarding:** [Three paths](../docusaurus-site/docs/guide/onboarding-three-paths.md) · [Tutorial index](../docusaurus-site/docs/tutorial/tutorial-index-three-paths.md).

## 0. Fifteen-minute path (no PySCF required)

**Fastest bootstrap** (creates `.venv`, installs `[dev]`, runs precomputed smoke):

```bash
cd qchem_qml_md
./scripts/bootstrap_dev.sh
export QCHEM_STACK_PYTHON="$(pwd)/.venv/bin/python"
```

Manual steps if you prefer:

1. **Environment** — pick an install profile from [README Install](../README.md#install-profiles-pip-extras) (`[dev]` for maintainers).
2. **Interpreter** — `export QCHEM_STACK_PYTHON=/path/to/python` or rely on repo `.venv` via [`scripts/venv-run`](../scripts/venv-run).
3. **Smoke without PySCF** — precomputed lane only:

```bash
cd qchem_qml_md
pip install -e ".[dev]"
./scripts/venv-run python scripts/smoke_pipeline.py --precomputed-only
```

4. **Architecture** — read [`ENGINEERING_ARCHITECTURE.md`](ENGINEERING_ARCHITECTURE.md) §1 (layer model).
5. **Full chemistry smoke** (needs PySCF): `./scripts/venv-run python scripts/smoke_pipeline.py`

## 1. Install and smoke

```bash
cd qchem_qml_md
pip install -e ".[dev]"
./scripts/venv-run python scripts/smoke_pipeline.py
```

This runs `configs/example_h2.yaml`: PySCF RHF → active space → VQE → optional Pauli protocol.

## 2. Run in Python

```python
from pathlib import Path
from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync
from qchem_stack.orchestration.pipeline_result import assert_pipeline_result_core_keys

cfg = load_experiment_config("configs/example_h2.yaml")
out = run_pipeline_sync(cfg, cfg_path=Path("configs/example_h2.yaml"))

assert_pipeline_result_core_keys(out)
print(out["schema"])              # pipeline_result_v1
print(out["scf_energy"])
print(out["energy_after_variational"])
print(out["pre_quantum_input"]["hamiltonian_fingerprint"])
print(out["repro"]["run_summary"]["stages_completed"])
```

Async job lane (SQLite):

```python
from qchem_stack.sdk import run_pipeline_from_config  # or: qchem_stack.orchestration.pipeline

out = run_pipeline_from_config("configs/example_h2.yaml", job_db=Path("jobs.sqlite"))
# out["job"], out.get("job_result"), out["repro"]["run_summary"]
```

## 3. Pipeline stages (sync)

| Stage | What happens |
|-------|----------------|
| `scf` | Classical mean field via `scf.driver` registry (default `pyscf`) |
| `pre_quantum` | Build `PreQuantumInput` → `QubitHamiltonian` |
| `variational` | VQE / ADAPT / registry plugin |
| `embedding_workflow` | Optional DMET / Schmidt / projection (YAML `embedding:`) |
| `excited` | Optional VQD / QSE / SCEOM |
| `protocol_finalize` | Optional Pauli averaging, resource summary, repro finalize |

Implementation: `qchem_stack.orchestration.pipeline.run_pipeline_sync`.

## 4. Core output keys (`PipelineResultV1`)

Always present after a successful sync run:

| Key | Meaning |
|-----|---------|
| `schema` | `pipeline_result_v1` |
| `repro` | Parity snapshot, run summary, optional profile/trace |
| `scf_energy` | Classical reference total energy (a.u.) |
| `energy_after_variational` | Variational ground energy (a.u.) |
| `angles` | Optimized circuit parameters |
| `pre_quantum_input` | Handoff summary (`source`, `backend_tag`, fingerprint, …) |
| `energy_components` | Nuclear / MF / solvent accounting |
| `hamiltonian_meta` | Qubit Hamiltonian branch metadata |
| `pre_quantum_build_cache` | Per-run memoization stats |

Common optional keys: `energy_pauli_protocol`, `resource_summary`, `protocol_counts`,
`vqd` / `qse` / `sceom`, `embedding_workflow`, `job`.

Typed definitions: `qchem_stack.orchestration.pipeline_result`.

## 5. `repro` block (export)

- **`repro.parity_snapshot`** — config-only audit fields captured at run start.
- **`repro.run_summary`** — `stages_completed`, energies, shot budgets, algorithm meta.
- **`repro.pipeline_profile`** — per-stage wall times (`pipeline_profile_v1`).
- **`repro.run_context`** — trace/request ids when passed in.

Strict JSON (no `default=str`):

```python
from qchem_stack.repro.export import repro_json_dumps
text = repro_json_dumps(out["repro"])
```

## 6. Where to change things

### chem recommended imports

**Style standard:** [chem_模块风格约定.md](chem_模块风格约定.md) · **Module reference:** [说明_chem模块技术参考手册.md](说明_chem模块技术参考手册.md) · **Package index:** [`src/qchem_stack/chem/README.md`](../src/qchem_stack/chem/README.md)

| Area | Import from |
|------|-------------|
| **Top-level (preferred)** | `qchem_stack.chem` — `create_solver`, `classical_mean_field_reference_from_config`, `build_pre_quantum_input`, `restricted_active_space_quantum_problem_from_config` |
| Classical drivers | `qchem_stack.chem.solvers` (`ChemIntegralSolver`, `SolverCapabilities`, registry detail) |
| Bridge interchange | `qchem_stack.chem.bridges` (canonical pack, `fork_driver_meta`) |
| Qubit Hamiltonian | `qchem_stack.chem.hamiltonian` |
| Pre-quantum assembly | `qchem_stack.chem.pre_quantum_build` (branch registry internals) |
| Embedding (chem-only) | `qchem_stack.chem.embedding` (projection, Schmidt production builders) |
| Integrals | `qchem_stack.chem.integrals` (PySCF exports); Psi4: `qchem_stack.chem.integrals.psi4_active_space` |

Variational sidecars that call `quantum.*` live under `qchem_stack.integrations` (for example `schmidt_per_fragment_vqe`, `dmet_fragment_solvers`).

| Goal | Start here |
|------|------------|
| New classical backend | `chem/solvers/registry.py`, template `custom_solver_template.py` |
| YAML fields | `config/experiment.py` + section validators in `config/_*_validation.py` |
| New variational algorithm | `quantum/variational_plugins/registry.py` |
| Product / gap exports | `protocols/product_contract.py` |
| Integration stubs vs product | [`src/qchem_stack/integrations/README.md`](../src/qchem_stack/integrations/README.md) |

## 7. CI parity (local)

```bash
./scripts/venv-run ruff check src/qchem_stack tests scripts examples
./scripts/venv-run ruff format --check src/qchem_stack tests scripts examples
./scripts/venv-run pytest tests -q --tb=short
```

See [`CONTRIBUTING.md`](../CONTRIBUTING.md) for merge gates and optional markers.

## Test pyramid

| Tier | When | Command |
|------|------|---------|
| **PR (required)** | Every push/PR | `pytest tests -m "not slow and not perf"` |
| **PR extras (3.12)** | CI only | smoke scripts, `check_parity_export_sample.py`, API tests |
| **Nightly** | schedule / `[nightly]` | `pytest -m "slow or perf"`; `QCHEM_RUN_L3=1 pytest -m l3` |
| **Local optional** | Before release | `pytest -m psi4`, `pytest -m l1_md_ml`, `pytest -m uqc_mock` |

Markers: `slow`, `perf`, `l3`, `l1_excited`, `l1_md_ml`, `pyscf`, `psi4`, `uqc_mock` — see `pyproject.toml`.
