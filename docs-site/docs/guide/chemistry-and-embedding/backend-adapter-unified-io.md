# 统一输入输出适配：多计算化学软件接入合同

目标：让用户在同一套 `ExperimentConfig`/YAML 下切换不同经典后端（PySCF、Psi4、后续更多），下游量子流程不需要感知上游软件差异。

## 统一输入（用户视角）

- 用户只提供 `molecule`、`scf`、`active_space`、`embedding` 等标准配置。
- 每个后端适配器负责把标准输入转换为该软件原生输入格式。
- 适配器必须通过 `ChemIntegralSolver` 注册到 `qchem_stack.chem.solvers.registry`。

## 统一输出（工程视角）

当前已落地的统一输出层：

- `MolecularMeanFieldResult`：统一 SCF 结果容器。
- `MeanFieldLike`：统一 mean-field 句柄包装（桥接层）。
- `CanonicalActiveSpaceIntegralPack`：统一活性空间积分包（哈密顿量构造输入）。
- `QubitHamiltonian`：统一量子哈密顿量输出。

一旦进入 `MolecularMeanFieldResult` / `ClassicalMeanFieldReference`，后续编排层应当对具体后端**零感知**，仅通过 `SolverCapabilities` 决定是否允许某个分支。

## 最小后端适配合同（MVP）

一个新后端最少需要：

1. 实现 `ChemIntegralSolver` 协议（`set_physical_data`、`compute_mean_field` 等）。
2. 声明 `SolverCapabilities`（尤其是 `supports_restricted_active_space_qubit_hamiltonian`）。
3. 如果暂不支持活性空间哈密顿量路径，明确设置  
   `supports_restricted_active_space_qubit_hamiltonian=False`，pipeline 会给出精确错误。
4. 若支持该路径，需提供与 `CanonicalActiveSpaceIntegralPack` 等价的积分供给能力。

可选能力（按需开启）也通过 `SolverCapabilities` 明确声明：

- `supports_projection_fragment_mulliken_hamiltonian`
- `supports_schmidt_atomic_hamiltonian`
- `supports_embedding_input_ao_lowdin`
- `supports_casscf_orbital_audit`
- `supports_avas_active_space_projection`（PySCF 示例：`active_space.strategy=avas`）
- `supports_rdm_correction_hooks`
- `supports_rdm_nevpt2_casci`
- `supports_get_integrals`

## 目前实现进度

- PySCF：
  - 已支持统一 mean-field 桥接、`CanonicalActiveSpaceIntegralPack`，以及默认活性空间哈密顿量主路径。
  - **几何**：`molecule.ecp`、`molecule.zmatrix`（与 Cartesian `coordinates` **互斥**，经 PySCF `gto.M`）。
  - **RI/DF**：`scf.density_fit`、`scf.density_fit_auxbasis`（`driver_meta`：`scf_density_fit`、`scf_density_fit_auxbasis`）。
  - **冻轨**：非空 `active_space.frozen_orbitals` → `driver_meta.active_space_frozen_orbitals` → CASCI **`frozen`**（须满足 PySCF 冻结电子偶等约束）。
  - **轨道后处理**：`chemistry_extended.mo_coeff_transform_hook`（审计 **`mo_coeff_transform_hook_v1`**）。
  - **一电子算符**：`PySCFDriver.compute_one_electron_operator_fermion` / `compute_one_electron_operator_pauli`（`kin|nuc|hcore|ovlp|r|rr|dm`）。
  - restricted MO 「量子问题三元组」仍以 **闭壳层 RHF** mean-field 为前提。
- Psi4：
  - 已接入 solver registry；**`supports_molecular_scf=True`**，环境具备 Psi4 时可跑 **RHF 总能量**（energy-only `MolecularMeanFieldResult`，**尚无** `CanonicalActiveSpaceIntegralPack` / 默认管线哈密顿量通道）。
  - `supports_restricted_active_space_qubit_hamiltonian=False`；无 Psi4 时 `compute_mean_field` 报清晰 **import** 原因。
- Pipeline：
  - 已按 capability 做门控，不再用 `scf.driver=="pyscf"` 硬编码。
  - `embedding.mode=plugin` 路径可独立于该门控运行。

## 推荐接入顺序（新增后端）

1. 打通 `compute_mean_field`，先满足统一 SCF 输出。
2. 补齐活性空间积分导出，接入 `CanonicalActiveSpaceIntegralPack`。
3. 将 capability 从 `False` 切换为 `True`。
4. 增加 backend conformance + pipeline smoke 测试。

## 快速上手

- [后端适配快速接入（模板 + 自检）](/guide/chemistry-and-embedding/backend-adapter-quickstart)

## 迁移示例（收口后）

兼容 wrapper 已移除；新代码必须直接走 `ClassicalMeanFieldReference` 统一入口。

```python
# recommended（backend-agnostic）
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.hamiltonian import molecular_hamiltonian_from_classical_reference

ref = ClassicalMeanFieldReference(
    mf=rhf.mf,
    e_tot=float(rhf.e_tot),
    mo_energy=rhf.mo_energy,
    molecular_system=rhf.molecular_system,
    driver_meta=dict(rhf.driver_meta),
)
qh = molecular_hamiltonian_from_classical_reference(
    ref,
    n_active_orbitals=2,
    n_active_electrons=2,
)
```

## 回归矩阵（建议）

- `tests/test_backend_capability_conformance.py`：后端 capability 基线与合同闸门。
- `tests/test_pipeline_backend_gate.py`：canonical pack / projection / schmidt 门控行为。

## 收口看板与兼容退场

### 当前收口状态（已完成）

- 统一中间层已固定：`MolecularMeanFieldResult`、`ClassicalMeanFieldReference`、`CanonicalActiveSpaceIntegralPack`。
- pipeline 走 capability gate，而非 `scf.driver` 品牌硬编码。
- Hamiltonian 路径统一到 `*_from_classical_reference`，兼容 helper 已删除。

### 可以停止“统一接口改造”并转向新工作的判定标准

满足以下条件即可视为本方向阶段性完成：

1. 至少一个非 PySCF backend（含 mock/stub）通过 adapter contract + pipeline gate 回归；
2. 文档示例统一使用 `ClassicalMeanFieldReference` 入口；
3. 新增 PR 不再引入 `scf.driver` 品牌判断（adapter 边界除外）。
