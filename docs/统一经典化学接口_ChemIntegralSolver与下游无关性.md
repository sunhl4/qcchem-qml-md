# 统一经典化学接口：`ChemIntegralSolver` 与下游无关性

## 1. 目标陈述

本工程把**不同计算化学程序**（PySCF、Psi4、后续 ORCA / CFOUR / 预计算积分包等）收敛到**同一套经典侧契约**：

1. **工厂**：`qchem_stack.chem.solvers.create_solver(cfg)` 按 `scf.driver` 选择已注册的适配器。
2. **协议**：`ChemIntegralSolver`（`set_physical_data`、`compute_mean_field`、可选 `get_integrals`）。
3. **交换物**：`MolecularMeanFieldResult`（`mf` 为 `MeanFieldLike` 包装、`e_tot`、`mo_energy`、`driver_meta`），再升为 `ClassicalMeanFieldReference` 供哈密顿量 / 嵌入消费。

**一旦数据进入上述交换物，后续编排（活性空间哈密顿量、嵌入、激发态、Pauli 协议、编译、作业）不得再假设底层是 PySCF。**

PySCF 是当前**实现最完整**的适配器，不是架构上的唯一真源。

## 2. 与 `scf.driver` 的关系

- `scf.driver` 仅是 **YAML 侧的程序选择键**，对应 registry 中的实现名（如 `pyscf`、`psi4`）。
- **能力门控**必须使用 `SolverCapabilities`（例如 `supports_restricted_active_space_qubit_hamiltonian`），避免在 `orchestration` 中写死 `scf.driver == "pyscf"`。

## 3. 「PySCF 专属」扩展应落在何处

下列能力天然依赖 PySCF 对象或 API，允许保留 **PySCF 插件 / 钩子** 形态，且必须在文档与错误信息中标明：

- `active_space.strategy=avas`（`mcscf.avas`）
- `chemistry_extended` 中与 `CASSCF` 轨道优化审计强绑定的路径
- `pyscf_active_space_hooks`、`PySCFDriver` 提供的量子问题三元组等

这些路径应在**进入统一交换物之前**完成，或在门控处明确：**当前 reference 是否暴露 PySCF MF**（见 `pipeline._require_pyscf_reference` 类工具函数）。

## 4. 维护纪律

- 新增经典后端：实现 `ChemIntegralSolver` + `register_solver(name, factory)` + 填满 `SolverCapabilities`。
- 新增编排阶段：只依赖 `ClassicalMeanFieldReference` / `CanonicalActiveSpaceIntegralPack` / capability，不直接 `import pyscf`。
- 90 天执行日历：`docs/execution/day001_day090_unified_chemistry_interface_calendar.md`。
- **Parity / Methods 导出**：`scripts/export_parity_criteria_table.py`（config-only）写出 **`registered_solvers`**（`chem.solvers.registered_solver_ids()`）与 **`solver_capabilities_snapshot`**（当前 YAML 选中驱动）；**`scf.driver=psi4`** 的代表样例：`configs/example_h2_psi4_rhf_sto3g.yaml`（已纳入 `scripts/check_parity_export_sample.py` 抽样）。完整经典路径仍以 PySCF 为主；Psi4 为 **能量/注册表** 浅接入，能力位见 `Psi4IntegralSolver.capabilities`。

## 5. 可选经典钩子：按 backend 插件挂载

- AVAS、CASSCF 轨道审计、AO/Lowdin 输入、Schmidt impurity 构造等属于 **backend plugin hook**，不属于通用编排内核。
- 编排层只能检查能力位（`supports_*`），并在缺失时给出明确报错，不允许散落 `if driver == "pyscf"` 语句。
- 当前实现中，PySCF 是这些钩子的默认提供者；Psi4 仍保持 energy-only 路径，能力位显式为 `False`。

## 6. `classical_benchmark_backend` 与上游标签对齐

| 字段 | 来源 | 说明 |
|---|---|---|
| `chemistry_extended.classical_benchmark_backend` | YAML 输入 | `auto|stub|pyscf|psi4`：表示 benchmark 选择策略 |
| `run_summary.classical_backend_id` | pipeline 运行时 | 当前 `scf.driver` 选中的后端 |
| `driver_meta.upstream_classical_software_tag` | bridge 规范头 | 统一引用上游经典软件标签 |

`auto` 场景下优先使用 `driver_meta.upstream_classical_software_tag`，并在 export/repro 中保留可追溯字段，避免 benchmark 数据与实际后端脱节。

## 7. 参考代码入口

- `src/qchem_stack/chem/solvers/registry.py` — 注册表
- `src/qchem_stack/chem/solvers/base.py` — `ChemIntegralSolver`、`SolverCapabilities`
- `src/qchem_stack/chem/bridges/facade.py` — `classical_mean_field_via_solver_bridge`
- `tests/test_solver_registry_contract.py` — 契约测试
