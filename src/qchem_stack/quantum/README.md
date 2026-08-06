# `qchem_stack.quantum`

Quantum algorithms: variational ground state, excited-state sidecars, demo tracks — consumes `PreQuantumInput` / `QubitHamiltonian` only.

**代码与架构风格标准（必读）：** [docs/quantum_模块风格约定.md](../../../docs/quantum_模块风格约定.md)

**YAML 配置：** [docs/说明_quantum配置.md](../../../docs/说明_quantum配置.md)

## Layout

| Area | Modules | Notes |
|------|---------|-------|
| Algorithms | `algorithms/` | `VQE`, `GQE`, SQD/QSCI sampling family (`sqd/`), `FermionicAdaptVQE`, `IQEBVQE`, `VQD`, `QSE`, QPE/VQS demos; UCCSD mapping in `uccsd_mapping.py`, CircuitIR in `uccsd_circuit.py` |
| Variational plugins | `variational_plugins/` | `run_variational_stage`, `register_variational_plugin` |
| Excited plugins | `excited_plugins/` | VQD / QSE / SCEOM sidecar dispatch |
| Branch factory | `variational_branch.py` | Shared UCCSD vs HEA wiring |
| Registries | `algorithm_registry`, `ansatz_registry`, `operator_pool_registry` | Export / materialization / pools |
| Statevector kernel | `statevector.py` | HEA circuits, dense Pauli expectations |
| Runtime helpers | `runtime.py` | `vqe_from_experiment_config` (lazy config import) |

## Build chain (canonical)

```text
PreQuantumInput / QubitHamiltonian
  → run_variational_stage(VariationalRunContext)     # quantum.algorithm registry
  → run_excited_stages_from_context(ExcitedRunContext)  # quantum.excited.* flags
  → protocol finalize (Pauli averaging via `protocols/ansatz_prep`, demo sidecars — orchestration)
```

Config is read in plugin runners via `config.quantum_helpers`; algorithm classes receive typed parameters only.

Excited-stage shot/resource accounting is emitted as `out["excited_resource_summary"]` by orchestration (not on `ExcitedStageOutcome`).

## Recommended imports

`quantum/__init__.py` intentionally exports nothing (avoids import cycles). Use:

```python
from qchem_stack.quantum.algorithms.vqe import VQE
from qchem_stack.quantum.algorithms.excited import VQD, QSE
from qchem_stack.quantum.variational_plugins.registry import run_variational_stage
from qchem_stack.quantum.excited_plugins.registry import (
    run_excited_stages_from_context,
    register_excited_plugin,
)
from qchem_stack.quantum.variational_branch import (
    build_uccsd_variational_model,
    run_uccsd_vqe_from_config,
)
from qchem_stack.quantum.runtime import vqe_from_experiment_config
from qchem_stack.quantum.algorithm_registry import build_registered_algorithm
from qchem_stack.quantum.operator_pool_registry import build_registered_operator_pool
```

Subpackage `quantum.algorithms` re-exports common algorithm classes via its `__all__`.

## Conventions (summary)

Full rules: [quantum_模块风格约定.md](../../../docs/quantum_模块风格约定.md).

- **No YAML parsing** in algorithm modules; use `VariationalRunContext` / `ExcitedRunContext`.
- **No orchestration imports** at module scope in `quantum/`.
- **UCC fermionic generators** from `qchem_stack.chem.kernels.spin_ucc` (not new code via `integrations.ucc_reference`).
- **Fermion→qubit mapping names** live in `chem.fermion_mapping_registry`; ansatz UX names in `ansatz_registry`.
