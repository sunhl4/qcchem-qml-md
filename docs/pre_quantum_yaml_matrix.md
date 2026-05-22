# Pre-quantum YAML 组合矩阵（验收表）

维护者与 CI 用：描述 **进入量子阶段之前** 允许的 `ExperimentConfig` 组合。规则实现在 `qchem_stack.config._experiment_validation`；一次性调用全部门禁可用 `validate_pre_quantum_contract(cfg)`；负例见 `tests/test_config_pre_quantum_combos.py`。

## 图例

| 符号 | 含义 |
|------|------|
| Y | 允许（配置加载 + 默认 pre-quantum 路径） |
| N | `ConfigurationError` 于 `load_experiment_config` |
| P | 仅 `embedding.mode=plugin` 或 `scf.driver=precomputed` |
| Py | 需要 `scf.driver=pyscf` |
| Ψ | 需要 `scf.driver=psi4` + capability 门控（见 `SolverCapabilities`） |

## 主矩阵（简表）

> **Schema v2（nested）**：DMET 字段在 `embedding.dmet.*`；projection 在 `embedding.projection.*`；plugin 在 `embedding.plugin.*`。详见 [`docs/说明_embedding配置.md`](说明_embedding配置.md)。

| scf.driver | embedding.mode | active_space.strategy | dmet.hamiltonian_source / projection | 默认 qubit 路径 |
|------------|----------------|----------------------|--------------------------------------|-----------------|
| pyscf | none | cas / manual | — | canonical pack → Y |
| pyscf | none | avas | — | AVAS → canonical → Y；`configs/example_h2_avas.yaml` |
| pyscf | dmet | cas | whole_active_system | canonical pack → Y |
| pyscf | dmet | cas | schmidt_atomic_production | Schmidt impurity → Y (RHF only)；`configs/example_h4_schmidt_multifragment.yaml` |
| pyscf | projection | cas | fragment_mulliken_mo | Mulliken MO → Y |
| psi4 | none | cas / manual | — | canonical pack (Psi4 CASCI) → Ψ；`configs/example_h2_psi4_rhf_sto3g.yaml` |
| psi4 | none | avas | — | AVAS（委托 PySCF 核）→ Ψ；`configs/example_h2_psi4_avas.yaml` |
| psi4 | dmet | cas | schmidt_atomic_production | Schmidt impurity → Ψ；`configs/example_h2_psi4_schmidt_dmet.yaml` |
| psi4 | projection | cas | fragment_mulliken_mo | Mulliken MO → Ψ；`configs/example_h2_psi4_projection_mulliken.yaml` |
| precomputed | none | * | — | bundle → Y；`configs/example_h2_precomputed_bundle.yaml` |
| precomputed | dmet / projection | * | schmidt / projection / avas | N（bundle-only；live embedding 拒绝） |
| precomputed | * | * | * + benchmark/RDM | N |
| * | plugin | * | — | decomposition JSON → P |

## P0 校验条目（与计划项 1 对应）

1. `precomputed` 禁止 `classical_benchmark_enabled` 与非 `none` 的 `rdm_correction_method`
2. `embedding.dmet.hamiltonian_source=schmidt_atomic_production` 要求 `scf.method=RHF`
3. Schmidt / Mulliken projection / AVAS 在 **load 期** 按 **`SolverCapabilities`** 门控；`precomputed` 与无 capability 的后端拒绝 live embedding（Schmidt、projection、`strategy=avas`）；PySCF 与 Psi4 均允许（Psi4 部分 L3 核委托 PySCF，见 `chem/integration/presets.py` 的 `capability_notes`）
4. `embedding.dmet.schmidt.dmet_max_cycles` ≤ 50（常量 `SCHMIDT_DMET_MAX_CYCLES_LIMIT`）
5. PBC 开启时禁止 CASSCF audit / AVAS refine

## 代码驱动分支注册表

<!-- BEGIN:PRE_QUANTUM_PATH_REGISTRY -->
- `PreQuantumPath` 枚举值（稳定顺序）：
  - `precomputed_bundle`
  - `embedding_plugin`
  - `schmidt_atomic_production`
  - `projection_fragment_mulliken_mo`
  - `canonical_active_space_integral_pack`
<!-- END:PRE_QUANTUM_PATH_REGISTRY -->

## 基线命令（波次 0）

```bash
./scripts/venv-run pytest tests/test_orchestration_pipeline.py tests/test_pre_quantum_input_contract.py tests/test_backend_capability_conformance.py -q
./scripts/venv-run pytest tests/test_run_build_cache.py tests/test_validate_pre_quantum_contract.py tests/test_config_pre_quantum_combos.py -q
./scripts/venv-run pytest -m psi4 tests/test_psi4_pre_quantum_pipeline.py tests/test_psi4_pyscf_h2_canonical_parity.py tests/test_psi4_pyscf_alignment.py -q  # optional
cd docusaurus-site && npm run build
```

Parity 导出（含 run 结果）会镜像 `pre_quantum_input_from_run` / `pre_quantum_build_cache_from_run`（`scripts/export_parity_criteria_table.py --results`）。
