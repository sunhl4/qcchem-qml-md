# 竞争定位与路线图：对标 Quantinuum 产品路线与技术路线

::: tip 产品与「镜像」的关系
**qchem-stack** 定位为**独立可竞争的开源编排产品线**（开放可审计、多后端、Methods 可发表）；`/mirror/` 仅对照 Quantinuum **公开**文档树做 gap 盘点，**不是**闭源 InQuanto 或 Nexus/H 系列的替代品。叙事母稿与长分析在仓库 `PandM/.../literature/` 与 `docs/architecture-report-quantinuum-inquanto-web/` 维护，**不**作为本站页面树的一部分。
:::

**文档角色**：在 [公开 parity 矩阵](/parity/public-matrix) 与工程记忆之上，**规定本仓库作为「可竞争产品」的边界、差异化与分阶段工程目标**。**不**声称在离子阱真机、InQuanto 闭源或 Nexus 商业云上「功能对等」。

---

## 1. Quantinuum 产品路线（公开信息归纳）

| 层次 | 代表组件 | 作用 |
|------|----------|------|
| 化学前处理与嵌入 | InQuanto-PySCF、active space、AVAS/CASSCF 驱动、DMET/投影嵌入/QM/MM | 大体系**下折叠**为量子子问题，符合工业案例叙事（药化、MOF、催化、生物、锕系等） |
| 量子工作流中枢 | InQuanto：`FermionSpace` / 算子 / `Computable` / `Protocol` / `Algorithm*` | 把「要算什么」与「怎么测、多少 shots、如何缓解」绑成**可复用**对象与流水线 |
| 编译与后端 | TKET / pytket、chemically aware 综合 | 线路优化与硬件门集重定向；与自家硬件强协同 |
| 云与资产 | Nexus / `qnexus`、项目与作业、HQC/资源估计 | 客户锁定与可计费工作流，**非** 单机包体验 |
| 硬件 | H-Series、Reimei、Helios 等 | 中端测量、QEC 与长期叙事承载 |

**一句话**：以 **InQuanto + 自家硬件** 为交付单元，**PySCF + TKET + Nexus** 为公开可见的产品三角。

---

## 2. Quantinuum 技术路线（双轨 + 嵌入优先）

- **近端（NISQ）**：VQE/ADAPT/IQEB、激发态 VQD/QSE/SCEOM、PMSV 等；真实案例大量依赖 **小活性空间 + 嵌入/fragment solver**，不宣称「全体系一次上量子机」。
- **长线（谱与容错）**：QPE 系、Bayesian/Phayes、QEC 化学；与 NISQ 在**资源形态**上不同，但在产品里作为**同一平台**的扩展路线。
- **方法哲学**：**embedding-first**（DMET/投影/fragment）与 **可审计工作流**（协议、资源表、云作业）是文档级主线。

---

## 3. 我们**可以**去竞争的那类「产品」

在闭源、硬件、云计价位**不**正面对打的前提下，本仓库的**可竞争产品定义**是：

> **「开放、可审计、可写进论文 Methods 的量子计算化学编排层 + 在 MD/ML 与多后端上可插拔的扩展面」**  
> 即：与 Quantinuum 在 **orchestration 抽象、判据/复现、嵌入叙事接口、双轨技术故事** 上**可比**；在 **H 系列真机、Nexus 计费、InQuanto 闭源能力** 上**明确不宣称等价**。

**差异化卖点（对学术与工程合作方）**：

1. **全链路开源可 fork**：可审计、可改、无许可黑箱（对比 InQuanto 主体闭源）。  
2. **公开「可证伪判据」出口**：`parity_snapshot`、`export_parity_criteria_table`、Hamiltonian `meta`、资源双轨（`spec` + 可选 [pytket](/reference/circuitir-tket-jobs)）。  
3. **多后端**：`statevector` / Qiskit / IonStack 钩子，**不**锁单一硬件。  
4. **MD / ML 长板**（相对「纯 InQuanto 化学核」）：`md_bridge`、`QMEFDataset`、主动学习与势函数数据集管线。  
5. **双轨技术叙事可对齐**：`qpe_qec_demo`、近端 VQE/ADAPT/激发态模块与工程记忆里的路线图一致，避免只做 NISQ 或只做容错之一。  
6. **HTTP 机读「非云超越钉扎」**：`GET /v1/meta/capability-surface` 的 **`open_stack_differentiators`**（`open_stack_differentiators_v1`）；与 [公开 parity 矩阵](/parity/public-matrix) §0 一致。

**对应「竞争产品」的交付物形态**（目标态，非即日全部完成）：

- Python 包 `qchem-stack`：`chem` → `quantum` + `protocols` → `backends` / `mitigation` → `jobs`；YAML 编排；可选云作业类比（SQLite + `JobHandle`）。  
- 文档：parity 矩阵、工程记忆、技术文档、本文路线图——支撑**立项/论文/合作方尽调**。

---

## 4. 我们**不**应作为对标的方面（避免目标错位）

- 与 **Quantinuum 商业云 + H 系列** 的 **1:1 产品替代**（无 Nexus、无 HQC、无真机 SLA）。  
- 追求与 **Qermit 商业运行时、inquanto-cutensornet、InQuanto 闭源 driver 目录** 的 **1:1** 替代（本仓库已提供 **开放栈可对表类比**：`qermit_analog`+`qermit_runtime`、`tensornet` stub+引擎钩子、PySCF 上 **ddCOSMO/PBC（含 k 网）** 等，见 [不排期项_转排期与实现说明.md](/parity/backlog-to-schedule) / [parity 矩阵](/parity/public-matrix)——**仍非** 产品与闭源等价）。  
- 以「**又做一套 InQuanto**」为 KPI——会陷入闭源与硬件护城河；应把 KPI 放在**开放可审计 + 领域扩展（MD/ML）+ 方法论文级**。

---

## 5. 分阶段工程优化目标（直接指导 `qchem_qml_md` 迭代）

下表将「竞争焦点」落为**仓库内**可执行项，并与现有 **partial** 行对齐。优先级 **P0** 短期可交卷，**P1** 中程，**P2** 结构增强。

| 阶段 | 竞争焦点 | 工程动作 | 主要模块/文档 |
|------|----------|----------|---------------|
| **P0** | 判据与可复现**叙事闭合** | 完善 `export_parity_criteria_table` 与 `repro` 在 CI 的固定例；任何 pipeline 大改时更新 [parity 矩阵](/parity/public-matrix) | `scripts/`、`orchestration/`、§2 工程记忆 |
| **P0** | Protocol **采样语义** 与 InQuanto「run→evaluate」可对照 | 默认文档强调 `_counts` 语义；`run_sampled` 路径在基准 YAML 中可一键开 | `protocols/protocol.py`、README |
| **P1** | **嵌入-first 接口** 强化 | 扩展 `DMETContext` / `projection` 与 pipeline 写出「自洽轮数、经典参考档」到 `repro`（竞品论文可证伪项） | `chem/embedding/`、`orchestration/pipeline.py` |
| **P1** | 激发态 **三算法** 与 Methods 同构 | QSE 过渡 Pauli 日程、VQD 三通道 shots 在 YAML 与 `resource_summary` 中**统一汇总**；SCEOM 小体系稠密参考路径 | `quantum/excited.py`、`qse_transition.py`、`sceom.py` |
| **P1** | 缓解**可报告** | PMSV：从存根到「stabilizer 列表 + 有效 shots + stderr 尺度」的完整机读块（可仍仿真） | `mitigation/pmsv.py`、protocol |
| **P2** | **QPE/容错** 与 NISQ **同一配置树** 可切换 | 在 `configs/` 增加「长线示范」样例，指向 `qpe_qec_demo/`，与工程记忆双轨说明一致 | `qpe_qec_demo/`、文档 |
| **P2** | 多后端**设备真 shot**（可选） | `PauliAveragingProtocol` 的 `run_qiskit_shots_pauli_protocol` + `backends/qiskit_pauli_shots.py`：Aer/IBM 等经 Qiskit `Backend.run` 的 `get_counts` 与 `resource_rows` 对齐；`HamiltonianExpectationExecutor` 仍用于非 shot 路径的精确期望 | [技术文档_设备比特串与Qiskit采样路径.md](/reference/qiskit-shot-counts) |
| **持续** | **MD/ML** 与化学核**契约稳定** | `md_bridge` schema、QMEF 与上游 `repro` 字段一致 | `md_bridge/` |

**已落地（工程执行）**：P0 已加 `export_parity_criteria_table` 扩展字段、CI 中 **parity 导出 + `--sampled` + `run_qpe_track_demo`**；P0 `run_sampled` 见 `configs/example_h2_sampled.yaml`；P1 已加 **`EmbeddingSpec` + `repro`、PMSV YAML + `pmsv_report`、`excited_shot_accounting`**；P2 已加 **`scripts/run_qpe_track_demo.py` + `configs/qpe_dual_track_demo.yaml`**、`pauli_measurement_ledger`；P2 已加 **Qiskit 比特串 Pauli 路径**（`run_qiskit_shots_pauli_protocol`、`configs/example_h2_qiskit_shots.yaml`、见 [技术文档_设备比特串与Qiskit采样路径.md](/reference/qiskit-shot-counts)）；持续项已加 **`QMFrame.repro_config_sha256_prefix`**。**另（开放栈可对表）**：`nexus_analog`/`nexus_cloud` 侧车、`qermit_*`、`tensornet` stub（矩阵 **`n/a`**）、PBC+k 点/ddCOSMO、JW **UCCSD Trotter**、Schmidt **bath 侧车**与 ONIOM **玩具层**、最小 **CASSCF 审计** 等已进主包与矩阵，见 [README](/tutorial/quickstart)、[工程记忆](/concept/engineering-memory-quantinuum) 与仓库 `docs/竞争定位…` §6「仍需推进」。**仍为后续**：Quantinuum 专有云真机一键编排、主 pipeline 内 QPE 与 FT **资源级**深度合流、产品级 ONIOM/QM-MM。

---

## 6. 与现有「工程记忆 / parity」的衔接

- 详细差距与实现顺序见 [工程记忆_Quantinuum对标与数据流技术文档.md](/concept/engineering-memory-quantinuum)（激发态、Protocol `run`、shots、ADAPT 元数据等）。  
- 公开能力覆盖见 [inquanto_public_parity_matrix.md](/parity/public-matrix)。  
- **能力差距 + 排期**（与 InQuanto 公开栈逐项对照、含 `pauli_protocol_expectation_path`）：[与InQuanto能力差距与实施计划.md](/parity/gap-implementation-plan)。  
- **本文**负责：**战略一句话 + P0–P2 表**；**工程记忆**负责：**模块级**细节与机读字段。

**维护约定**：当 parity 中某行从 `partial` 收束为更「可发表」时，**同时**更新本文 §5 对应行与工程记忆 §9 路线图，避免三份文档分歧。

---

## 7. 一句话收束

**对 Quantinuum 的合适合竞争态**不是「再做一个 InQuanto」，而是做一个 **在开放与可证伪上更强、在 MD/ML 与多硬件上更灵活、在近端+容错叙事上可并列** 的量子化学编排品——`qchem_stack` 的优化应**优先**砸在 **P0/P1 的判据、嵌入、激发态与机读资源摘要**，再铺 **P2 设备与 QPE 深化**。
