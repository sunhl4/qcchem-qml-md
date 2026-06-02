# Config field index

Authoritative nested schema: [`说明_config模块技术参考手册.md`](../说明_config模块技术参考手册.md).

| YAML path | Python path | Section |
|-----------|-------------|---------|
| `schema_version` | `ExperimentConfig.schema_version` | root |
| `scf.driver` | `cfg.scf.driver` | classical |
| `scf.pyscf.*` | `cfg.scf.pyscf` | PySCF knobs |
| `scf.psi4.*` | `cfg.scf.psi4` | Psi4 knobs |
| `active_space.cas.*` | `cfg.active_space.cas` | CAS counts |
| `active_space.fermion_qubit_mapping` | `cfg.active_space.mapping` | JW/BK/SCBK |
| `embedding.mode` | `cfg.embedding.mode` | none/schmidt/dmet/projection |
| `quantum.algorithm` | `cfg.quantum.algorithm` | VQE/ADAPT/VQD/… |
| `quantum.vqe.*` | `cfg.quantum.vqe` | variational |
| `backend.provider` | `cfg.backend.provider` | statevector/qiskit/uqc |
| `mitigation.zne.*` | `cfg.mitigation.zne` | ZNE |
| `md_ml_export.*` | `cfg.md_ml_export` | QMEF attachment |
