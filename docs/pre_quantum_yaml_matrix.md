# Pre-quantum YAML 组合矩阵（验收表）

维护者与 CI 用：描述 **进入量子阶段之前** 允许的 `ExperimentConfig` 组合。规则实现在 `qchem_stack.config._experiment_validation`；一次性调用全部门禁可用 `validate_pre_quantum_contract(cfg)`；负例见 `tests/test_config_pre_quantum_combos.py`。

## 图例

| 符号 | 含义 |
|------|------|
| Y | 允许（配置加载 + 默认 pre-quantum 路径） |
| N | `ConfigurationError` 于 `load_experiment_config` |
| P | 仅 `embedding.mode=plugin` 或 `scf.driver=precomputed` |
| Py | 需要 `scf.driver=pyscf` |
| Ψ | 需要 `scf.driver=psi4` + 可选 Psi4 绑定（活性空间 CASCI 积分） |

## 主矩阵（简表）

| scf.driver | embedding.mode | active_space.strategy | dmet_hamiltonian_source | 默认 qubit 路径 |
|------------|----------------|----------------------|-------------------------|-----------------|
| pyscf | none | cas / manual | — | canonical pack → Y |
| pyscf | dmet | cas | whole_active_system | canonical pack → Y |
| pyscf | dmet | cas | schmidt_atomic_production | Schmidt impurity → Y (RHF only)；样例 `configs/example_h4_schmidt_multifragment.yaml` |
| pyscf | projection | cas | — | Mulliken MO → Y |
| psi4 | none | cas / manual | — | canonical pack (Psi4 CASCI) → Ψ |
| psi4 | dmet/projection | * | schmidt / projection | N |
| precomputed | none | * | — | bundle → Y；样例 `configs/example_h2_precomputed_bundle.yaml`（parity export 抽样） |
| precomputed | * | * | * + benchmark/RDM | N |
| * | plugin | * | — | decomposition JSON → P |

## P0 校验条目（与计划项 1 对应）

1. `precomputed` 禁止 `classical_benchmark_enabled` 与非 `none` 的 `rdm_correction_method`
2. `schmidt_atomic_production` 要求 `scf.method=RHF`
3. 非 PySCF 禁止 Schmidt、Mulliken projection、AVAS（Psi4 在实现 canonical pack 后仍禁止 Schmidt/AVAS）
4. `schmidt_dmet_max_cycles` ≤ 50（常量 `SCHMIDT_DMET_MAX_CYCLES_LIMIT`）
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
./scripts/venv-run pytest tests/test_run_build_cache.py tests/test_validate_pre_quantum_contract.py -q
./scripts/venv-run pytest -m psi4 tests/test_psi4_pre_quantum_pipeline.py tests/test_psi4_pyscf_h2_canonical_parity.py -q  # optional
cd docusaurus-site && npm run build
```

Parity 导出（含 run 结果）会镜像 `pre_quantum_input_from_run` / `pre_quantum_build_cache_from_run`（`scripts/export_parity_criteria_table.py --results`）。
