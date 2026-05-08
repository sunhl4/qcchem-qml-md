# Backend Adapter Quickstart (Template + Contract Check)

This is the shortest path to integrate a new classical chemistry backend into the unified qchem_stack I/O surface.

Optional first step: generate a scaffold and then fill TODOs.

```bash
python scripts/create_solver_adapter_scaffold.py my_backend
# Also emit a runnable register + contract-check demo (default: ``scripts/register_my_backend_demo.py``; runs registration + the same contract checks as ``check_solver_adapter_contract.py`` **in-process**):
python scripts/create_solver_adapter_scaffold.py my_backend --with-demo-register
python scripts/register_my_backend_demo.py
```

## 1) Copy the template and rename it

Template file: `src/qchem_stack/chem/solvers/custom_solver_template.py`

Recommended copy:

- `src/qchem_stack/chem/solvers/my_backend_solver.py`
- rename `CustomExternalIntegralSolver` to `MyBackendIntegralSolver`
- set `capabilities.backend_id` to your backend identifier

## 2) Implement the minimum methods

MVP methods:

- `set_physical_data(cfg)`
- `compute_mean_field(periodic=False)` (or `run_molecular_mean_field`)
- `capabilities` with accurate support flags

`compute_mean_field` must return `MolecularMeanFieldResult`.

## 3) Register in solver registry

Runtime registration is a good first step:

```python
from qchem_stack.chem.solvers import register_solver
from qchem_stack.chem.solvers.my_backend_solver import MyBackendIntegralSolver

register_solver("my_backend", MyBackendIntegralSolver.from_experiment_config)
```

Then use:

```yaml
scf:
  driver: my_backend
```

If you want a runnable reference first:

- adapter example: `src/qchem_stack/chem/solvers/mock_external_solver_example.py`
- one-command demo: `python scripts/demo_mock_external_backend.py`
- the adapter marks three edit anchors: `TODO[1]`, `TODO[2]`, `TODO[3]` (capabilities / SCF call / integral export)

## 4) Run adapter contract checks

Script: `scripts/check_solver_adapter_contract.py`

```bash
python scripts/check_solver_adapter_contract.py configs/example_h2.yaml --driver my_backend
python scripts/check_solver_adapter_contract.py configs/example_h2.yaml --driver my_backend --run-mean-field
```

If your backend is not numerically runnable yet, run without `--run-mean-field` first.

## 5) Enable active-space Hamiltonian path later

If active-space integrals are not ready yet, keep:

- `supports_restricted_active_space_qubit_hamiltonian=False`

Pipeline then fails with a precise message for that stage, while plugin mode (`embedding.mode=plugin`) remains usable.

After implementing canonical-pack-equivalent integral support, switch that capability to `True`.

## 6) Suggested regression checks

- `tests/test_chem_integral_solver_tangelo_aliases.py`
- `tests/test_solver_adapter_contract.py`
- `tests/test_orchestration_pipeline.py`
- `tests/test_mock_external_backend_example.py`
- (optional) `python scripts/check_solver_adapter_contract.py ... --run-mean-field --require-mean-field-success`

## Related pages

- [Unified backend adapter I/O contract](/en/guide/chemistry-and-embedding/backend-adapter-unified-io)
- [CLI and scripts](/en/reference/cli-and-scripts)
