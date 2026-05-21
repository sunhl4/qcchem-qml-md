# `qchem_stack.config`

Experiment YAML → typed [`ExperimentConfig`](experiment.py) models.

**代码与架构风格标准（必读）：** [docs/config_校验分层约定.md](../../../docs/config_校验分层约定.md)

**模块技术参考手册（网页文档底稿）：** [docs/说明_config模块技术参考手册.md](../../../docs/说明_config模块技术参考手册.md)

## Layout

| Area | Models | User docs |
|------|--------|-----------|
| Top-level | `experiment.py` | [说明_实验配置加载_io.md](../../../docs/说明_实验配置加载_io.md) |
| Embedding | `embedding*.py` | [说明_embedding配置.md](../../../docs/说明_embedding配置.md) |
| Quantum | `quantum*.py` | nested 字段见 style doc §3.1 |
| Active space | `active_space.py` | [说明_active_space配置.md](../../../docs/说明_active_space配置.md) |
| Chemistry extended | `chemistry_extended*.py` | style doc §3.2 |
| Mitigation / MD-ML | `mitigation*.py`, `md_ml_export.py` | nested `zne` / `pmsv` / `stubs`; `trajectory` |
| Molecule / SCF / IO | `molecule.py`, `scf.py`, `io.py`, `geometry_files.py` | [说明_molecule配置与自旋多重度.md](../../../docs/说明_molecule配置与自旋多重度.md), [说明_scf配置.md](../../../docs/说明_scf配置.md) |

## YAML load chain

```text
raw dict
  → preprocess_top_level_yaml_dict (unknown keys → extra)
  → geometry_file / scf.precomputed.bundle_path preprocess
  → Pydantic section models (extra=forbid on nested blocks)
  → ExperimentConfig cross-section validators
  → optional validate_pre_quantum_contract() at pipeline entry
```

**Note:** `validate_pbc_k_mesh_solver_capability` runs at `ExperimentConfig` construction only; it is not part of `validate_pre_quantum_contract()`.

## Conventions (summary)

Full rules: [config_校验分层约定.md](../../../docs/config_校验分层约定.md).

- Nested YAML path = Python attribute path (`cfg.quantum.vqe.maxiter`).
- **`schema_version: "2"`** required; flat legacy keys are rejected at load.
- New sections: `{section}_enums.py` + `{section}_specs.py` + `{section}.py` + `_{section}_validation.py` (+ helpers as needed).
- Field docs: one-line `Field(description=...)` in code; long prose in `docs/说明_*.md`.
- SCF cross-field rules: `_scf_validation.py`; driver normalization: `_driver_helpers.scf_driver_id`.
