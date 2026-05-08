# InQuanto-PySCF 叙事对照：量子问题三元组与 AO 视图

对应 Quantinuum 文档里常见的分子 **PySCF driver → Hamiltonian / Fock space / Hartree–Fock reference → VQE 等变分算法** 路径。本仓库为 **开源独立实现**：API 不必同名，但下列能力覆盖教程里的工程意图。

## 1. `get_system()` 类路径（MO 活性空间 → OpenFermion）

InQuanto：返回积分算符、Fock/占据空间、HF 参考态等。

`qchem_stack`：

- :meth:`qchem_stack.chem.drivers.pyscf_driver.PySCFDriver.get_restricted_active_space_quantum_problem`
- 返回 :class:`~qchem_stack.chem.molecular_problem.RestrictedActiveSpaceQuantumProblem`，字段包含：
  - **`compact_mo_operator`** — :class:`~qchem_stack.chem.restricted_integral_operator.RestrictedActiveSpaceIntegralOperatorCompact`：保留 PySCF CASCI ``get_h2eff`` 的 **紧凑或稠密**缓冲；可按需 ``dense_h2_chemist_spatial()`` / ``to_interaction_operator()`` 展开；并提供 **`df_mo_integrals()` / `df()`**（pandas）用于表格化检视（叙事上对齐教程里的 ``df()`` 预览）。
  - **`interaction_operator`** — :class:`openfermion.InteractionOperator`
  - **`fermion_space`** — :class:`~qchem_stack.chem.fermion.FermionSpace`
  - **`hartree_fock_state_jw`** — OpenFermion **Jordan–Wigner** HF 振幅向量
  - **`qubit_hamiltonian`** — :class:`~qchem_stack.chem.hamiltonian.QubitHamiltonian`

底层 CASCI 拆分入口：:func:`~qchem_stack.chem.drivers.pyscf_driver.active_space_casci_raw_blocks`；OpenFermion 映射仍统一走 Tangelo 约定的积分重排（见 :mod:`qchem_stack.chem.integral_convention`）。

## 2. `get_system(symmetry=…)`（对称性 + 紧凑 MO 双电子块）

InQuanto：`ChemistryRestrictedIntegralOperatorCompact` 等在经典侧压缩双电子存储。

`qchem_stack`：

- **对称性启用**：`chemistry_extended.pyscf_symmetry` → ``pyscf.gto.M(..., symmetry=...)``，加速经典 SCF / 积分阶段。
- **紧凑容器**：`RestrictedActiveSpaceIntegralOperatorCompact` 保存 ``get_h2eff`` 原始布局（``eri_raw_ndim`` / ``eri_raw_n_elements`` 写入 ``symmetry_meta``）；仅在调用 ``dense_h2_chemist_spatial`` / ``to_interaction_operator`` 时按要求 ``ao2mo.restore`` 展开为 `(na,na,na,na)`。
- **量子映射（Jordan–Wigner）**：可选两条路径。（1）默认：`InteractionOperator` + OpenFermion 专用 JW 内核；可选 `active_space.jordan_wigner_coeff_atol`（正值）跳过数值上可忽略的 Pauli 壳。（2）省 JW 步自旋四维 ERI：设 `active_space.prefer_restricted_spatial_fermion_for_jordan_wigner: true`（须 `fermion_qubit_mapping: jordan_wigner`），由空间 MO 直接构造 `FermionOperator` 再 JW。**统一编排入口**：`molecular_hamiltonian_from_classical_reference`；`PySCFDriver.get_restricted_active_space_quantum_problem` 保持可用。`interaction_operator` 仍会按需 materialize 以保持 API（教程 ``df()`` / 契约导出）。通过 :meth:`~qchem_stack.chem.drivers.pyscf_driver.PySCFDriver.from_config` 构造驱动后，调用 ``get_restricted_active_space_quantum_problem`` 时若省略对应关键字参数，则会从 ``cfg.active_space``（即 YAML 的 ``active_space`` 段）继承上述开关。
- **说明**：紧凑积分容器仍用于 **推迟 `ao2mo.restore`** 与 **表格导出**；超大体系仍需 DF/TN 等单独后端，而非单靠上述 JW 技巧。

### 2.1 AVAS / CASSCF（PySCF 可选阶段，仍走统一出口）

- **`active_space.strategy=avas`**：`chemistry_extended.avas_ao_labels` **必填**，仅 `scf.driver=pyscf`；PySCF **`mcscf.avas.AVAS`** 阈值投影后旋转 **`mf.mo_coeff`**，管线写入 **`qchem_active_space_resolution_v1`** 并回填 `active_space` 尺寸；样例 `configs/example_h2_avas.yaml`。
- **`chemistry_extended.casscf_orbital_optimization_for_integrals`**：与 **`casscf_orbital_optimization_audit`** **共用**一次 **`mcscf.CASSCF`** kernel；前者可将优化轨道接到后续 CASCI 型活性积分（审计块见 `casscf_orbital_audit_v1`）。
- **诚实边界**：不等价于 InQuanto **封闭产品**里「默认全套 driver + UX」的 AVAS/CASSCF；见 [公开矩阵 §3 Classical chemistry](/parity/public-matrix) 与 [附录 §10](/parity/gap-implementation-plan#p2-w3-avas-casscf-boundary)。

### 2.2 几何、RI/DF、冻轨、轨道钩子与一电子算符（PySCF）

> 注：PySCF 在本工程中是**默认适配器示例**，不是唯一绑定后端；统一入口仍是 `create_solver` + `SolverCapabilities`。

- **`molecule.ecp`**、**`molecule.zmatrix`**：与 Cartesian `coordinates` **互斥**；经 PySCF `gto.M` 构建。
- **`scf.density_fit`** / **`scf.density_fit_auxbasis`**：`driver_meta` 记录 `scf_density_fit*`。
- **冻轨**：**`active_space.frozen_orbitals`** → **`driver_meta.active_space_frozen_orbitals`** → CASCI **`frozen`**（须满足 PySCF 电子数等约束）。
- **轨道后处理**：**`chemistry_extended.mo_coeff_transform_hook`**（`identity`、`reverse_mo_columns` 或 ``module:function``），审计 **`mo_coeff_transform_hook_v1`**。
- **一电子算符**：`PySCFDriver.compute_one_electron_operator_fermion` / `compute_one_electron_operator_pauli`（``kin|nuc|hcore|ovlp|r|rr|dm``）；**不等价**闭源 `compute_one_electron_operator` 全集。
- **restricted 量子问题路径**：仍以 **闭壳层 RHF** mean-field 为前提；UHF/ROHF 等会显式报错。
- **Psi4**：registry 已接；可选环境下 **`compute_mean_field`** 可返回 **RHF 总能量** 占位 MF；仍 **`supports_restricted_active_space_qubit_hamiltonian=False`**。

## 3. `get_system_ao()`（AO + PySCF `mf` 句柄）

InQuanto：`PySCFChemistryRestrictedIntegralOperator` 包装 SCF，利于 AO/FMO 叙事。

`qchem_stack`：

- :meth:`qchem_stack.chem.drivers.pyscf_driver.PySCFDriver.get_system_ao` → :class:`~qchem_stack.chem.drivers.pyscf_driver.PySCFAOSystem`
- **表格摘要**：:meth:`~qchem_stack.chem.drivers.pyscf_driver.PySCFAOSystem.ao_driver_summary_df` 输出 ``nao_nr``、电子数、``groupname`` 等（pandas）。

嵌入 / Schmidt 另见 `get_lowdin_system` 与编排管线。

## 4. 坐标单位（Å / Bohr）

分子几何可使用 **`coordinates` + `coordinate_unit`**（默认 **Å**），或兼容旧键 **`coordinates_bohr`**（省略单位时按 **Bohr**）。详见配置模型 `MoleculeSpec`。

## 5. 可运行示例（站内镜像）

- 仓库脚本：`examples/example_inquanto_style_quantum_problem.py`（在仓库根目录执行）。

```bash
python examples/example_inquanto_style_quantum_problem.py
```

## 相关入口

- [活性空间指定、冻结轨道与 AVAS（理论·实践·开源对照）](../../../../docs/活性空间指定与AVAS_理论实践与开源对照.md)（母稿在仓库 `docs/`，本站为相对链接，克隆根目录下可读）
- [二次量子化读表：Fock 态与费米哈密顿量](./second-quantization-fock-hamiltonian-readout.md)
- [P1 化学与嵌入](./index.md)
- [公开契约矩阵 §3 Classical chemistry](/parity/public-matrix)
