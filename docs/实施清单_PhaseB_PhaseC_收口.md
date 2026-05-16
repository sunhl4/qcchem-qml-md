# 实施清单：Phase B / Phase C 收口记录

## 1. 范围说明

本收口基于 `技术分析_Vendor platform_PySCF_vs_原生PySCF_及工程借鉴.md` 中的分阶段路线：

- **Phase B**：强化嵌入上游输入形态（AO / Löwdin 表示）；
- **Phase C**：RDM 驱动后处理的工程骨架（先走可机读、可回归的 stub 路线）。

---

## 2. Phase B 完成项

- [x] `PySCFDriver.get_system_ao(run_hf=...)`  
  - 返回 `PySCFAOSystem`，保留 SCF 对象句柄，支持 `run_hf=False` 场景。
- [x] `PySCFDriver.get_lowdin_system(...)`  
  - 返回 `PySCFLowdinSystem`（`constant/h1/h2/rdm1`）用于嵌入上游输入。
- [x] 新增配置：`embedding.embedding_input_representation`  
  - 支持 `mo | ao | lowdin_orth_ao`。
- [x] pipeline 接入 AO/Löwdin 输入上下文  
  - 顶层输出 `embedding_input_system`；
  - `embedding_workflow.embedding_input_system` 同步写入（dmet/projection/plugin/none）。
- [x] `run_summary` 镜像  
  - `embedding_input_representation_yaml`；
  - `embedding_input_system_schema`。
- [x] 新增测试：`tests/test_pyscf_driver_phase_b_interfaces.py`、`tests/test_phase_bc_pipeline_wiring.py`（lowdin 路径）。

---

## 3. Phase C 完成项（骨架）

- [x] 新增 `RDMBundle` 类型  
  - 文件：`src/qchem_stack/chem/rdm_bundle.py`。
- [x] 新增 RDM correction 插件骨架  
  - 文件：`src/qchem_stack/integrations/rdm_corrections.py`；
  - 方法：`stub_nevpt2` / `stub_ac0`（机读报告，不做数值内核）。
- [x] 新增配置：`chemistry_extended.rdm_correction_method`  
  - `none | stub_nevpt2 | stub_ac0 | pyscf_nevpt2_casci`（见 §4 Phase 3）。
- [x] pipeline 接入 correction 报告  
  - 输出：`rdm_bundle_meta`、`rdm_correction`；
  - `run_summary` 镜像：`rdm_correction_*`。
- [x] parity/export 接入  
  - `export_parity_criteria_table.py` 增加 config 与 run mirror 字段；
  - `RUN_SUMMARY_DOCUMENTED_KEYS` 已同步扩展。
- [x] 新增测试：`tests/test_phase_bc_pipeline_wiring.py`（rdm stub + Phase 3 NEVPT 路径）。

---

## 4. Phase 3（Phase C 深化）

- [x] **parity 维度**：`rdm_correction_readiness_v1`（`rdm_correction_readiness` + `run_summary` 镜像键）。
- [x] **可选数值内核**：`pyscf_nevpt2_casci` → PySCF `mrpt.NEVPT(CASCI(...))` 相关能增量（**不**宣称与 Vendor platform 闭源 `vendor-pyscf` 行级等价）。
- [x] stub / 数值共用报告字段：`reference_wavefunction`、`kernel_class`、`pyscf_nevpt2` 状态块。

---

## 5. 与产品级能力的边界

以下仍属于后续深化项（本次不宣称完成）：

- AVAS 真实活性空间自动选择；
- **AC0** 及量子测量 RDM 驱动的高阶混合后处理（产品级）；
- 闭源 Vendor platform `vendor-pyscf` 行级行为一致性（开放栈仅提供 **PySCF mrpt.NEVPT** 可选钩子，见 §4）。

---

## 6. 当前结论

在“开放栈、可机读、可回归”的工程目标下，**Phase A + Phase B + Phase C（含 Phase 3 深化）均已收口**。  
后续可在 CASCI→NEVPT 钩子之上扩展 CASSCF 参考态、AC0、以及与量子侧 RDM 的耦合。

---

## 7. 统一接口收口看板（2026-05）

> 目标：把“后续流程不关心上游计算化学软件品牌”从实现事实提升为可验收合同。

### 7.1 完成度清单

- [x] 统一输入：`ExperimentConfig` 作为唯一用户输入面。
- [x] 统一输出中间层：`MolecularMeanFieldResult` / `ClassicalMeanFieldReference` / `CanonicalActiveSpaceIntegralPack`。
- [x] pipeline 能力门控：按 `SolverCapabilities` 判定，不使用 `scf.driver=="pyscf"` 硬编码。
- [x] 公开量子问题与 bundle 构造入口统一为 `ClassicalMeanFieldReference`。
- [x] Hamiltonian helper 提供统一入口：
  - `molecular_hamiltonian_from_classical_reference`
  - `fermionic_active_space_interaction_operator_from_classical_reference`
- [x] 新后端接入工具链：
  - `create_solver_adapter_scaffold.py`
  - `check_solver_adapter_contract.py`
  - `mock_external_solver_example.py`
- [x] 架构不变量已写入：
  - `docs/ENGINEERING_ARCHITECTURE.md`
  - docusaurus-site 中英文架构页

### 7.2 统一接口完成态

- 公共入口仅保留统一类型：`ClassicalMeanFieldReference` / `CanonicalActiveSpaceIntegralPack`。
- pipeline 编排与能力门控不依赖后端品牌分支。
- backend-specific 能力入口仅在显式语义边界内保留（例如 PySCF 专用构造与驱动返回类型）。

### 7.3 收口验收门槛（达到即可转入新方向）

1. 至少一个非 PySCF backend（可 mock/stub）通过 adapter contract + pipeline capability gate 回归。
2. 文档与示例统一使用 backend-agnostic 入口，不再将 compat-only 路径作为可用指南。
3. 新增功能 PR 不得引入新的 `scf.driver` 品牌判断分支（除 adapter 边界）。
4. 回归矩阵持续通过：
   - `tests/test_backend_capability_conformance.py`
   - `tests/test_pipeline_backend_gate.py`
   - `tests/test_canonical_integral_pack.py`

---

## 8. 后续维护边界（完成态）

### 8.1 明确保留项（backend-specific，持续保留）

- `CanonicalActiveSpaceIntegralPack.from_pyscf_reference`
- `RestrictedActiveSpaceIntegralOperatorCompact.from_pyscf_rhf`
- `PySCFRHFResult` 与 `pyscf_driver` 内部返回类型

说明：以上属于“显式 PySCF 专用能力入口”，与 compat-only helper 不同；应在命名和文档上保持 backend-specific 语义，而非硬删除。

### 8.2 当前验收状态

1. 统一入口覆盖主流程与测试主路径。
2. 文档面向统一接口，不引导兼容层调用。
3. backend-specific 入口保留在明确命名与语义边界内。
