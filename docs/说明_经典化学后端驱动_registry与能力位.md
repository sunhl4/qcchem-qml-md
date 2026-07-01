# 经典化学后端：`scf.driver`、Registry 与 `SolverCapabilities`

本文说明本仓库 **如何做到不绑定单一量子化学程序**，以及 **当前内置实现（PySCF / Psi4 等）各自支持什么**。配置字段细节见 [说明_scf配置.md](说明_scf配置.md)；活性空间与映射见 [说明_active_space配置.md](说明_active_space配置.md)。

---

## 架构理念（对外讲解）

**三层模型与接入清单（推荐阅读）**：[execution/multi_backend_integration_philosophy.md](execution/multi_backend_integration_philosophy.md)

- **L1 驱动**：用户熟悉的程序做 SCF/波函数（PySCF、Psi4、自研 ORCA 等）。
- **L2 契约**：`ClassicalMeanFieldReference`、`AOBasisView`、`SolverCapabilities`。
- **L3 共享核**：AVAS/CASCI/NEVPT2 等可委托，不必在每个 driver 里重写。
- **不要求** 与 PySCF 数值完全一致；**要求** `driver_meta.kernel_bindings` 与 `epistemic_bound` 可审计。

代码辅助：`qchem_stack.chem.integration`、`qchem_stack.chem.kernels`；模板见 `chem/solvers/custom_solver_template.py`。

---

## 核心结论（先读这段）

1. **架构上是多后端的**：`scf.driver` 只是 **字符串 id**，通过 `qchem_stack.chem.solvers.registry.create_solver` 解析为 `ChemIntegralSolver` 实现；**禁止**在 orchestration 里写死 `import pyscf` 选路（registry 模块注释即此约定）。
2. **内置已注册**：`pyscf`、`psi4`、`precomputed`，以及可通过 **entry point** `qchem_stack.chem_solvers` 挂载的第三方插件（见 `mock_external_solver_example`、`custom_solver_template`）。
3. **能力用 `SolverCapabilities` 声明**，`ExperimentConfig` 加载时用 **capabilities 布尔位** 拒绝 YAML 组合（`validate_backend_capabilities_for_pre_quantum_path`），而不是「只有 PySCF 才能跑」。
4. **`strategy: avas` 加载期门控**：`_experiment_validation.validate_avas_strategy_requires_labels_and_capability` 只查 **`supports_avas_active_space_projection`** 与非空 **`avas_ao_labels`**（不再要求 `scf.driver='pyscf'`）。Psi4 等后端可在 SCF 后委托 PySCF `mcscf.avas`（见 `driver_meta.kernel_bindings`）。

---

## 数据流（后端无关部分 vs 后端相关部分）

```text
experiment.yaml
  molecule:          # 几何、电荷、multiplicity、基组 — 与 driver 无关
  scf.driver:        # 选择经典后端 id
  active_space:      # 尺寸、strategy、费米子→量子比特映射 — 与 driver 无关（校验层）
        │
        ▼
ExperimentConfig 加载
  ├─ ActiveSpaceSpec + _active_space_validation.py   （不 import 任何 QC 包）
  └─ _experiment_validation.py                      （读 driver + capabilities）
        │
        ▼
create_solver(cfg)  →  PySCFIntegralSolver | Psi4IntegralSolver | …
        │
        ▼
pre_quantum_build / hamiltonian                     （OpenFermion 等；映射与 driver 解耦）
```

**`active_space.fermion_qubit_mapping`、JW/BK/SCBK、`ncas`/`nelecas` 的规范化** 不依赖 PySCF；只要后端能提供 **restricted active-space 积分 / MO 系数**，即可走同一套 qubit 哈密顿量构建（具体路径见 BK/SCBK 备忘文档）。

---

## 内置 `scf.driver` 与能力位对照（当前代码）

实现类：`src/qchem_stack/chem/solvers/pyscf_solver.py`、`psi4_solver.py`、`precomputed_solver.py`。  
能力 dataclass：`src/qchem_stack/chem/solvers/base.py` → `SolverCapabilities`。

| 能力位 | PySCF | Psi4 | precomputed | 含义（简） |
|--------|:-----:|:----:|:-----------:|------------|
| `supports_molecular_scf` | ✅ | ✅ | ✅ | 分子 SCF |
| `supports_pbc_scf` | ✅ | ✅ (Γ-only) | ❌ | 周期边界 SCF |
| `supports_rhf` / `rohf` / `uhf` | ✅/✅/✅ | ✅/✅/✅ | ✅/✅/✅ | 平均场类型 |
| `supports_restricted_active_space_qubit_hamiltonian` | ✅ | ✅ | ❌ | 默认 pre-quantum 活性空间 → qubit H |
| `supports_avas_active_space_projection` | ✅ | ✅ | ❌ | `strategy: avas` |
| `supports_projection_fragment_mulliken_hamiltonian` | ✅ | ✅ | ❌ | embedding 分片 Mulliken |
| `supports_schmidt_atomic_hamiltonian` | ✅ | ✅ | ❌ | Schmidt DMET |
| `supports_embedding_input_ao_lowdin` | ✅ | ✅ | ❌ | AO / Löwdin 导出 |
| `supports_casscf_orbital_audit` | ✅ | ✅ | ❌ | CASSCF 轨道审计/feed |
| `supports_rdm_correction_hooks` | ✅ | ✅ | ❌ | RDM bundle |
| `supports_rdm_nevpt2_casci` | ✅ | ✅ | ❌ | NEVPT2 类后关联 |
| `supports_get_integrals` | ✅ | ✅ | ❌ | `get_integrals` API |

因此：

- **H₂ 默认管线**（`cas` + JW）对 `driver: pyscf` 与 `driver: psi4` 均在配置加载时允许。
- **Psi4 示例**：`configs/example_h2_psi4_rhf_sto3g.yaml`、`configs/example_h2_psi4_schmidt_dmet.yaml`、`configs/example_h2_psi4_avas.yaml`。
- **本地安装 Psi4（推荐）**：`./scripts/setup_psi4_micromamba.sh` → 使用 `.micromamba/envs/.conda-psi4/bin/python -m pytest -m psi4`。
- **Psi4 限制**：PBC 仅 `pbc_kpoint_mesh: [1,1,1]`；`ddcosmo` 映射为 Psi4 PCM。
- **跨后端算法核（科学边界需知）**：
  - **AVAS**：`strategy: avas` 时 Psi4 路径用 `build_pyscf_rhf_shadow` 导入 MO，再跑 PySCF `mcscf.avas`（`avas_source=pyscf_mcscf_avas_on_imported_mo_v1`），**不再**对 Psi4 重复 SCF。
  - **NEVPT2**：`psi4_nevpt2_casci` 与 `pyscf_nevpt2_casci` 均调用 **同一** PySCF `mrpt.NEVPT(CASCI)`；Psi4 仅在 MO 来源上不同（`pyscf_mrpt_on_psi4_imported_mo_v1`）。
  - **Schmidt 杂质 ERI**：Psi4 用 `MintsHelper.ao_eri` + MO 变换；PySCF 用 `ao2mo.full`。
  - **Mulliken 投影**：Psi4 CASCI 块计算时临时改写 `wfn.Ca()`，结束后恢复，避免污染参考波函数。
  - **Psi4 1.10 API**：SCF 返回 `core.RHF`（非 `Wavefunction`）；`MintsHelper` 使用 `ao_overlap`/`ao_kinetic`/`ao_potential`；无 `energy('casci')` 时走 Mints CASCI 有效哈密顿量回退。
  - **Parity CI**：`pytest -m psi4` 含 `tests/chem/test_psi4_pyscf_h2_canonical_parity.py` 与 `tests/chem/test_psi4_pyscf_alignment.py`（H₂ 软阈值）。

---

## Registry 如何扩展新后端（不修改核心 orchestration）

1. 实现 `ChemIntegralSolver`（可参考 `custom_solver_template.py`）。
2. 在 `capabilities` 中如实填写 `SolverCapabilities`（`adapter_contract` 会做一致性检查）。
3. 注册：
   - **内置**：在 `registry.py` 的 bootstrap 中增加 id（与 `pyscf`/`psi4` 同级），或  
   - **插件**：`pyproject.toml` / entry point 组 `qchem_stack.chem_solvers`。
4. YAML 中 `scf.driver: <your_id>`。
5. 为所用能力补测试；若涉及 `active_space.strategy: avas`，实现投影 hook 后将 `supports_avas_active_space_projection=True`。

**不要**在 `config/_active_space_validation.py` 里 `import` 新后端；跨能力组合放在 `_experiment_validation.py`。

---

## 与 `active_space` 相关的「看起来绑定 PySCF」的条目

| 用户可见行为 | 实际机制 | 未来演进 |
|--------------|----------|----------|
| `strategy: avas` | AVAS **投影核** 为 PySCF `mcscf.avas`；加载期仅查 **capability** + `avas.ao_labels`（C2 已完成） | Psi4 等：`build_pyscf_rhf_shadow` 导入 MO 后跑同一 AVAS 核（`configs/example_h2_psi4_avas.yaml`） |
| `chemistry_extended.avas_ao_labels` | PySCF AVAS 输入格式 | 可演进为后端中性「AO 选择 DSL」，由 adapter 翻译 |
| `chemistry_extended.pyscf_symmetry` | 名称带 pyscf，属扩展段 | 可并行增加 `psi4_*` 或通用 `point_group` 字段 |
| JW/BK/SCBK 映射 | OpenFermion + 本仓库 `hamiltonian.py` | 与 driver 无关 |

---

## 实验配置加载时的后端相关校验（索引）

| 函数 | 文件 |
|------|------|
| `validate_backend_capabilities_for_pre_quantum_path` | `_experiment_validation.py` |
| `validate_avas_strategy_requires_labels_and_capability` | `strategy: avas` → capability + `avas_ao_labels` |
| `validate_pbc_excludes_casscf_hooks` | 同上 |
| `validate_precomputed_driver_excludes_live_hooks` | 同上 |
| `validate_schmidt_requires_rhf` / `validate_schmidt_cycle_bounds` | 同上（embedding × scf） |

活性空间 **模块内** 待办与跨模块待办：**[说明_active_space配置.md — 后续开发备忘](说明_active_space配置.md#后续开发备忘)**。

---

## 源码索引

| 内容 | 路径 |
|------|------|
| `scf.driver` 字段 | `src/qchem_stack/config/scf.py` |
| Solver 注册表 | `src/qchem_stack/chem/solvers/registry.py` |
| 能力位定义 | `src/qchem_stack/chem/solvers/base.py` |
| PySCF / Psi4 实现 | `pyscf_solver.py` / `psi4_solver.py` |
| 实验级校验 | `src/qchem_stack/config/_experiment_validation.py` |
