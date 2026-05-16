# 工程深度路线图：与 InQuanto / Tangelo **公开叙事**可对标的交付框架

**文档性质**：在 [与 InQuanto 能力差距与实施计划](与InQuanto能力差距与实施计划.md)、[公开 parity 矩阵](inquanto_public_parity_matrix.md)、[算法面广度索引](算法面广度_InQuanto_Tangelo对照索引.md) 之上，给出一份**按深度维度组织的完整计划**（目标 → 工作包 → 验收 → 依赖），供中长期迭代使用。  
**边界**：全文默认 **L1**（公开文档可追溯 + 机读 JSON + CI）；**不**将闭源二进制、Nexus/HQC 真云、专有硬件专优、JKMN/HCB 可执行映射（未单独立项前）纳入承诺。

**竞品锚点（公开侧）**

| 来源 | 用途 |
|------|------|
| [Quantinuum InQuanto 文档](https://docs.quantinuum.com/inquanto/) | Protocols、Algorithms、Mitigation、Resource estimation、How-to 叙事 |
| Tangelo / 教程生态（JW/BK、激发池命名、分解叙事） | 通过 [算法面广度索引](算法面广度_InQuanto_Tangelo对照索引.md) §2–§3 与本栈 `tangelo_public_mapping_alias_surface_v1` 对齐 |

**机读真源（本栈）**

- HTTP：`GET /v1/meta/capability-surface`（`capability_surface_v1` 顶层键集）。  
- 导出：`scripts/export_parity_criteria_table.py`；稳定键：`protocols/inquanto_contract.py`（import **`qchem_stack.protocols.inquanto_contract`**；frozenset/gap 字面量 **`internal_reports/competitor/inquanto_contract.py`**，见 [CONTRIBUTING](../CONTRIBUTING.md#parity-and-workflow-preview-stable-imports)）（含 `RESOURCE_ESTIMATION_PREVIEW_V1_DOCUMENTED_KEYS`、`METHODS_RESOURCE_UNIFIED_V1_DOCUMENTED_KEYS` 等）。  
- 差距分类：`inquanto_gap_categories()`。

---

## 1. 「深度足够」的可验收定义

在与 InQuanto / Tangelo **对比**时，本路线图所称 **深度**指下面四类证据至少满足其一项，且 **写入矩阵 / gap / 契约注册**：

| 层级 | 含义 | 验收示例 |
|------|------|----------|
| **D1 叙事对齐** | 公开文档中能逐句对应到本栈模块或诚实 `partial` | 矩阵行 + gap id + 技术文档锚点 |
| **D2 机读对齐** | 同一语义在 YAML → `repro` / export / HTTP 中可解析 | 键注册 + pytest / `check_parity_export_sample` |
| **D3 数值/行为切片** | 有限配置下可重复数值或确定性行为 | L3 代表 YAML、`algorithm_benchmark_bundle_v1` |
| **D4 工程扩展面** | 开源可插拔、多后端、审计链（故意超越「纯文档包」之处） | `open_stack_differentiators_v1` 条目 + 证据模块路径 |

**不构成深度承诺**：未列入契约或未注册键的「静默实现」；未写 SLA 的长期 `partial`。

---

## 2. 能力轴 × 深度目标（摘要）

下列每一轴在 [parity 矩阵](inquanto_public_parity_matrix.md) 中均有对应行；此处只固定 **深度目标档位** 与 **权威入口**，避免与 §1 差距长表重复维护细节。

| 能力轴 | InQuanto / Tangelo 公开对照点 | 本栈深度目标（2026–2027） | 权威代码 / 文档入口 |
|--------|------------------------------|---------------------------|---------------------|
| **经典化学与嵌入** | 多 driver、活性空间、嵌入 / 分解叙事 | D2+D3：ChemIntegralSolver 扩展；AVAS/CASSCF **诚实 partial**；Schmidt–DMET 可检证子集 | `chem/`、`integrations/schmidt_dmet_self_consistent.py`；差距 §1「经典化学」；P2-W3 |
| **费米子映射与哈密顿量** | JW/BK/SCBK、教程别名 | D2：`tangelo_public_mapping_alias_surface_v1`；JKMN/HCB **披露不执行**直至专项 | `chem/fermion_mapping_registry.py`；`技术文档_UCCSD_JW与BK_SCBK电路边界.md` |
| **算法与算符池** | Algorithms API、激发 taxonomy | D2+D3：registry export；L3 代表集；**不冒充**全套闭源 taxonomy | `quantum/algorithm_registry.py`、`operator_pool_registry.py`；算法面广度索引 §4–§5 |
| **协议与资源语义** | Resource estimation、dataframe_circuit_shot | D2：`resource_estimation_preview_v1` 与 `methods_resource_unified_v1` **镜像一致**；Pauli 三路径 token | `integrations/resource_estimation_preview.py`、`methods_resource_unified.py`；设备比特串技术文档 |
| **缓解** | Qermit MitRes/MitEx | D2：DAG + 线性迹不变量；进阶 ZNE/PMSV **可回归块** | `mitigation/`；`mitigation_PMSV_ZNE_Qermit_mapping.md`；P2-W4 |
| **工作流与 Computable** | 五阶段、Computable | D2：`workflow-preview`、`computable_graph_v2`、可选 `computables_rich_v1` | `integrations/inquanto_workflow_preview.py`（`qchem_stack.integrations.inquanto_workflow_preview`；[CONTRIBUTING](../CONTRIBUTING.md#parity-and-workflow-preview-stable-imports)） |
| **作业与 HTTP** | Nexus 叙事（非真云） | D2：runs API、capability-surface 同源 | `api/app.py`、`jobs/` |
| **MD/ML** | 非 InQuanto 主宣传 | D2+D4：长板钉扎 | `md_bridge/`；矩阵 MD/ML 行 |

---

## 3. 三阶段总览（节奏）

| 阶段 | 时间建议 | 主题 | 与现有执行文档关系 |
|------|----------|------|-------------------|
| **Phase A — 机读与 Methods 深化** | 已完成 + 滚动 | export 键全集注册、preview ↔ unified 镜像、capability-surface 文档同源 | Day91–Day120；P2-W1 |
| **Phase B — 经典与缓解纵深** | 2–4 季度 | AVAS/CASSCF 边界文档 + 可选数值切片；mitigation 进阶块；多求解器能力矩阵 | P2-W3、P2-W4；[统一经典接口日历](execution/day001_day090_unified_chemistry_interface_calendar.md) 延续项 |
| **Phase C — 可比基准与叙事封口** | 并行 | L3 扩充、`algorithm_benchmark_bundle_v1` 论文级表；**Docusaurus** 三路径；Day121–Day180 对照收口 | [day121_day180_inquanto_tangelo_calendar_2026Q3.md](execution/day121_day180_inquanto_tangelo_calendar_2026Q3.md)；[day91_next_phase_plan_2026Q3.md](execution/day91_next_phase_plan_2026Q3.md) Week5–6 |

---

## 4. 工作包明细（WBS）

每项：**目标** | **交付物** | **验收（闸门）** | **依赖 / 备注**

### WP-A1 — Methods 导出链闭环（进行中）

- **目标**：任意代表 YAML 上，`resource_estimation_preview_v1` 与 `methods_resource_unified_v1` 对同一 `run_summary` **协议字段**与 **经典 benchmark 摘要（`classical_benchmark_*`）** **零漂移**。  
- **交付物**：YAML 镜像字段；`classical_benchmark_enabled_yaml`（config）；pipeline 下 `_attach_classical_benchmark_preview_alignment` 与 unified 同源合并；注册表与 `tests/test_methods_resource_unified_export.py`（含 benchmark 启用样例与 preview 对拍）。  
- **验收**：`pytest tests/test_methods_resource_unified_export.py tests/test_*_key_registry.py`；差距计划 §2 已钉 export 对齐句。  
- **依赖**：无。

### WP-A2 — capability-surface 与矩阵 §0 同源纪律

- **目标**：HTTP / parity / CONTRIBUTING 不因新增 export 键而漂移。  
- **交付物**：变更 checklist（CONTRIBUTING 已有）；重大变更走矩阵 §0 + gap。  
- **验收**：`test_capability_surface_matches_inquanto_contract`。  
- **依赖**：WP-A1。

### WP-B1 — P2-W3：AVAS / CASSCF「产品边界」文档 + 最小数值切片

- **目标**：与 InQuanto「全套默认 UX」区分清晰的前提下，把 **已落地路径**写到 D2+D3。  
- **交付物**：矩阵 §3、专用 ADR/技术小节更新；1–2 个 fixture YAML 专测 export + run_summary。  
- **验收**：不升格矩阵为虚假 `yes`；`partial` 均有 gap 或 SLA。  
- **依赖**：PySCF 路径；与 [附录 A W3](与InQuanto能力差距与实施计划.md) 一致。

### WP-B2 — P2-W4：Mitigation 进阶块（优先 ZNE 变体）

- **目标**：公开 errmit 叙事下，Methods 导出与 **`parity_snapshot`** 在 **ZNE mode / scales** 上可对读、可对拍（不等价商业 MitRes）。  
- **交付物（滚动）**：`resource_estimation_preview_v1` 含 **`mitigation_zne_mode_yaml`**、**`mitigation_zne_scales_yaml`**、（pipeline）**`parity_snapshot_mitigation_zne_*`**；**`methods_resource_unified_v1`** 顶键镜像 **`run_summary`** 中同源 YAML 字段；映射表见 [mitigation_PMSV_ZNE_Qermit_mapping.md](mitigation_PMSV_ZNE_Qermit_mapping.md)。PEC / quasi-probability 仍为文档占位，不默认开 DAG。  
- **验收**：`pytest tests/test_methods_resource_unified_key_registry.py::test_preview_unified_zne_yaml_matches_after_pipeline`；DAG 迹不变量既有测试保持绿。  
- **依赖**：与 Qiskit Pauli / `zne_qiskit_unification_v1` 文档一致。

### WP-B3 — ChemIntegralSolver 第二后端「浅数值」（Psi4 或契约驱动 stub）

- **目标**：强化「IntegralSolver（Tangelo toolbox shape）」叙事至 **D2**（接口 + 能力声明）；数值 MF 仍按需 **D3**（可选安装 Psi4）。  
- **交付物（已滚动）**：仓库样例 **`configs/example_h2_psi4_rhf_sto3g.yaml`**；`export_parity_criteria_table` 既有 **`registered_solvers`** / **`solver_capabilities_snapshot`** / **`scf_driver`**；**`scripts/check_parity_export_sample.py`** 抽样已纳入该 YAML；说明见 [统一经典化学接口…](统一经典化学接口_ChemIntegralSolver与下游无关性.md) §4；回归 **`tests/test_export_parity_golden.py::test_export_repo_psi4_example_yaml_capabilities_snapshot`**。  
- **验收**：`python scripts/check_parity_export_sample.py`；上述 pytest。  
- **依赖**：Psi4 可选安装（CI 不强制）；[subprocess 风险清单](execution/subprocess_chem_risk_checklist.md) 仍适用于未来 subprocess 适配。

### WP-C1 — L3 基准集扩充与报告脚本固化

- **目标**：算法对比表可达 **D3**（能量、nfev、墙钟）且可一键再生。  
- **交付物（已滚动）**：`L3_PYTEST_YAMLS` 含基线 **`configs/example_h2.yaml`（VQE）**，与 ADAPT / IQEB 代表池及别名、激发 smoke 共 **7** 条；模块内 **增量准则**；`scripts/l3_algorithm_benchmark_report.py` 指向 `DEFAULT_BENCHMARK_YAMLS` / `L3_PYTEST_YAMLS`。  
- **验收**：`QCHEM_RUN_L3=1 pytest -m l3`；merged bundle schema 稳定。  
- **依赖**：WP-A1。

### WP-C2 — Tangelo 映射与教程词条对齐（滚动）

- **目标**：教程常用名 ↔ 栈内 canonical **可查**（不发「等价执行」假信号）。  
- **交付物（已滚动）**：JW 行 `public_aliases` 增补 **`Jordan-Wigner transformation`**（`chem/fermion_mapping_registry.py`；`test_fermion_qubit_mapping`）；后续别名仍须伴随测试或 caveat。  
- **验收**：capability-surface 测试通过；广度索引 §5 同步。  
- **依赖**：OpenFermion 白名单策略。

### WP-C3 — `docusaurus-site` / examples 「三路径」与文档同源

- **目标**：新用户能从 onboarding 跑到 **带 repro 导出** 的最短路径（**主站**：`docusaurus-site/`；`docs-site/` VitePress 为补充/自动化遗留面）。  
- **交付物（滚动）**：`guide/onboarding-three-paths`、parity 矩阵与差距计划入口页与仓库 `docs/` 母稿互链；`examples/` 与教程交叉引用。  
- **验收**：手工链接巡检或脚本；P2-W7 闸门。  
- **依赖**：无。

---

## 5. 全局闸门（每个里程碑必须过）

1. `ruff check` + `ruff format --check`（约定路径）。  
2. `pytest`（或 CI 等价子集）。  
3. `python scripts/check_parity_export_sample.py`。  
4. 若改契约：`inquanto_contract` 注册集更新 + 相关 `test_*_key_registry.py`。  
5. 若改 HTTP：`app.py` 为真源，同步 [HTTP 技术契约](技术文档_HTTP_API与SQLite作业队列及可观测性契约.md) / docs-site。

---

## 6. 非目标（重申，防止深度「越界」）

- 声称 **L0**（闭源 wheel / 内部默认 / 全组合数值等价）。  
- 实现 **商业 Nexus IAM、HQC 货币、MitEx 批量运行时** 等与公开文档「形似」但虚假的云对齐。  
- **JKMN/HCB 可执行映射** 在未完成独立设计与金样前默认 **不执行**（与 capability-surface 披露一致）。  
- **cuTensorNet / inquanto-cutensornet** 化学尺度收缩的产品级等价。

---

## 7. 维护方式

- **主清单**：仍以 [与 InQuanto 能力差距与实施计划](与InQuanto能力差距与实施计划.md) 附录 A–F 为任务台账；**本文提供维度视图与 WBS 优先级**。  
- **按日执行**：Day91–Day120、Day121–Day180 日历填证据链；重大收口更新本节「三阶段」状态一行（日期 + 指向 execution/*.md）。  
- **矩阵**：任何 WP 关闭或降级需在 [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) 留痕。

---

*Epistemic note：路线图深度以 **可辩护的 L1+L3 切片** 为上限；与 Tangelo **开源教程**对齐优先于与 **闭源 InQuanto 产品默认值**对齐。*
