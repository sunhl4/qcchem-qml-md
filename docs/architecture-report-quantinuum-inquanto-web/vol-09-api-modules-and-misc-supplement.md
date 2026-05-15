# Vol.09 补遗 — `api/` 模块面与 `misc/`（manifest 聚合索引）

**读者**：库维护者、API 文档负责人。  
**真源**：[`mirror-doc-tree.yaml`](../../docs-site/scripts/mirror-doc-tree.yaml) 中 `api:` 与 `misc:` 子树（本卷把 Vol.02 未逐条展开的 **API 模块级** 与 **杂项** 做聚合说明）。**与 Sphinx 侧栏的逐项对拍**见 [Vol.10](./vol-10-official-sidebar-vs-manifest.md)。

---

## 1. 为什么需要本补遗卷

Vol.02 聚焦 **Manual** 叙事主线；InQuanto 公开站同等重要的是 **`api/inquanto/*` 模块页 + 类叶海**。manifest 将 **每个公开类** 拆为独立 mirror 节点，附录 C 对每个节点给出 **架构拆解** — 本卷从 **模块聚合** 视角再归纳一遍，避免读者只在附录里「见树不见林」。

---

## 2. API 顶层：`api/inquanto/` 下的模块族

以下顺序与 manifest `api.children` **键顺序** 一致（含 **API 总览页** 与 **experiments / geometries / embeddings** 等侧栏显式链）。

### 2.0 API 门面页（`api/inquanto_api_intro.html`、`api/inquanto-ext_api_intro.html`）

- **职责**：总览 InQuanto 与 Extensions 的 **API 文档地图**；链向各 `api/inquanto/*.html` 与 `api/extensions/*_api.html`。
- **我们映射**：自有站以 **Reference** 区首页 + `parity` 机读契约替代「双总览」重复堆字即可。

### 2.1 `inquanto.algorithms`（`api/algorithms.html`）

- **职责**：`Algorithm*` 族 — VQE、ADAPT、激发态、QPE、时间演化等 **高层循环对象**。
- **与 Manual 关系**：`manual/algorithms_overview.html` 与各 `algorithms_*.html` 解释语义；API 页给 **构造参数、run/build 钩子、返回值**。
- **类叶密度**：含多条 `placeholder` / `partial` QPE 与 McLachlan 变体 — 反映 **双轨（NISQ vs 谱/动力学）** 产品故事。
- **我们映射**：`qchem_stack.quantum.algorithms`；parity 以 **激发态 shots 汇总、ADAPT 元数据** 为高风险区。

### 2.2 `inquanto.ansatzes`（`api/ansatz.html`）

- **职责**：从 **电路 ansatz** 到 **FermionSpace 上 UCC 家族、多组态、化学感知** 变体。
- **与 Manual 关系**：`manual/ansatzae_overview.html`、`manual/ansatze/ucc_family.html`、`hea.html`。
- **占位特征**：大量 `FermionSpaceAnsatz*` 与 `MultiConfiguration*` 仍为 **placeholder** — 公开 API 面宽于 **默认开源实现** 是预期现象。
- **我们策略**：HEA / 部分 UCC 已 `shipped`；其余在 mirror 保留占位 + 里程碑，不在营销中宣称等价。

### 2.3 `inquanto.computables`（`api/computables.html`）

- **职责**：**表达式树 / 延迟求值** — `ExpectationValue*`、导数、重叠、`ComputableTuple/List`、QSE/SCEOM 矩阵块等。
- **与 Manual 关系**：`manual/computables_overview.html` 与 `atomic` / `composite` / `primitives` / `evaluating_w_protocols`。
- **架构要点**：Computable 与 Protocol **正交** — 前者定义「算什么」，后者定义「怎么测与怎么编译运行」。
- **我们映射**：`qchem_stack.protocols.computable`；HTTP `computable-preview` 应对齐 **v2 abstract** 字段。

### 2.4 `inquanto.operators`（`api/operators.html`）

- **职责**：Fermion / Qubit 算符容器、积分算子、RDM、FCIDUMP、对称性算符等。
- **与 Manual 关系**：`manual/spaces.html` 中费米子 / 量子比特算符章节。
- **shipped 核心**：`FermionOperator`、`QubitOperator` 系列 — 几乎所有量子化学工作流的中枢数据结构。

### 2.5 `inquanto.spaces` / `inquanto.states` / `inquanto.mappings`

- **spaces**：`FermionSpace` 及周期 / 超胞占位。
- **states**：`FermionState`、`QubitState`。
- **mappings**：**JW 已 shipped**；BK、parity mapping 多为 placeholder — 与 parity 矩阵中 **映射可选性** 一致。
- **跨切点**：三者与 **qubit encoding** 一节强绑定，是 **化学 → 量子比特** 的枢纽。

### 2.6 `inquanto.minimizers`

- **职责**：SciPy、NFT、Rotosolve、SPSA、SGD 等 **经典外层优化器** 封装。
- **与 Manual**：`manual/minimizers.html`；与 **AlgorithmVQE** 组合使用。

### 2.7 `inquanto.symmetry`（API 与 Manual 双节点）

- Manual `manual/symmetry.html` 与 API `api/inquanto/symmetry.html` 在 manifest 均为 **placeholder** — **对称性在公开故事中出现但实现面仍扩张**。

### 2.8 `inquanto.core`

- **职责**：横切 **核心类型与工具**（具体类未在本报告展开 — 见附录 C 若 manifest 补全子类）。
- **IA 注意**：`core` 常被 **低估文档化**；却是 **版本升级破坏性变更** 高频区。

### 2.9 `inquanto.embeddings`（`api/inquanto/embeddings.html`）

- **与 Manual `embedding` 章节对读**：公开模块名为 **`inquanto.embeddings`**（HTML 为 `embeddings.html`，**非** `embedding.html`）；API 侧重 **类与构造函数**，Manual 侧重 **DMET/投影/NEVPT2 叙事**。

### 2.10 `inquanto.experiments`（`api/inquanto/experiments.html`）

- **职责**：与 **Knowledge Articles** 配套的演示型子域（如 QEC+QPE 长文对应的 `experiment_qec_qpe.html`）。
- **我们策略**：manifest 以 **占位 + 里程碑** 标能力边界；不在开源栈暗示已等价复现纠错演示全链。

### 2.11 `inquanto.express`

- **职责**：`load_h5`、`run_vqe` 等 **快速路径**；与 quickstart **强绑定**。
- **Note**：quickstart 已说明 `run_vqe` **非生产** — API 文档应重复此警告（厂商已做）。

### 2.12 `inquanto.geometries`（`api/inquanto/geometry.html`）

- **职责**：几何对象与 **Manual / Geometry** 的 API 侧符号；与 `manual/geometry.html` 互链。

### 2.13 `inquanto.protocols`（最大协议面）

- **职责**：`PauliAveraging`、`SparseStatevectorProtocol`、QPE 系、overlap、mitigation（`PMSV`/`SPAM`/`CombinedMitigation`）等。
- **与 Manual**：五阶段叙事 **必须** 与此页互链。
- **n/a 示例**：`IterativePhaseEstimationQuantinuum` — **硬件/厂商路径** 在开源栈标 `not-applicable` 合理。

### 2.14 `inquanto.extensions.*`（API 子域）

| manifest 键 | 说明 |
|---------------|------|
| `extensions_pyscf` | 最大驱动 / DMET / FMO 类面；与 **化学规格** 主叙事重合度最高。 |
| `extensions_cutensornet` | GPU 张量网络协议；与 **执行成本** 叙事相关。 |
| `extensions_nexus` | 云作业；我们 **n/a** 以本地 jobs API 文档替代。 |
| `extensions_phayes` | 贝叶斯 QPE；占位至 2027 里程碑。 |
| `extensions_nglview` | 可视化 n/a — 由上层应用自选 nglview。 |

---

## 3. `misc/` — 合规、支持与学术背书

| 子节点（manifest 键） | 公开意图 | 我们站对应动作 |
|------------------------|-----------|----------------|
| `release_notes` | `misc/changelog.html` 发行说明 | 以 **CHANGELOG / releases** 与 API 破坏性变更加锁；可对读厂商 changelog 但不复制其正文。 |
| `bibliography` | 可引用文献列表 | 维护 `docs/` 内 **公开论文与白皮书** 索引；不与闭源内部报告混淆。 |
| `contact_docs` | `misc/contact.html` 文档内支持页 | 标 `not-applicable`：我们使用 **issue/discussion**，不镜像厂商工单 UX。 |
| `how_to_cite` | `misc/cite.html` 引用格式 | 提供 **BibTeX / CITATION.cff** 与论文引用指引。 |
| `license` | 法律文本 | 仓库 `LICENSE` + **第三方 NOTICES** 与 parity 中 **依赖声明** 对齐。 |
| `opensource_attribution` | `misc/opensource.html` | 与 **SBOM / NOTICES** 同源维护，避免与 `license` 重复冲突。 |
| `contact` | 外链 `quantinuum.com/contact/docs` | README / footer 链到 **自有渠道**；保留本节点用于 **parity 对照**。 |

---

## 4. 与附录 C 的协同用法

1. **模块级决策**（本卷 §2）→ 定路线图优先级。  
2. **类级审计**（附录 C 每节点）→ 定实现与文档 PR 粒度。  
3. **TSV**（附录 B）→ 导入表格做 **筛选：placeholder ∩ P1** 等。

---

## 5. 本卷结论

`api/` 与 `misc/` 在 InQuanto 公开站中占据 **「符号真值 + 合规入口」**；Manual 占据 **「可教叙事」**。三者 **闭环** 才构成完整产品文档 — 本卷补齐 Vol.02 未展开的模块视角，与 **附录 C（规则生成、行数随节点数变化）** 及 [Vol.10](./vol-10-official-sidebar-vs-manifest.md) 共同支撑 **可审计** 拆解。

**返回**：[`INDEX.md`](./INDEX.md)。
