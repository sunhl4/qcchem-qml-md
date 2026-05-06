---
title: InQuanto 模块复现骨架
description: 公开站顶层与 Manual 一级分支 ↔ 本站镜像路由与工程文档 — 可编辑母版，非厂商正文转载
---

# InQuanto 公开站模块 → 本站复现骨架

本文是 **信息架构母版**：左侧沿用 Quantinuum **公开** InQuanto 文档站的 **模块名与 URL 规律**（便于对照与后续改写），中间是本站已生成的 **镜像树入口**（结构与 `docs-site/scripts/inquanto-tree.yaml` 一致），右侧是 **qchem-stack 实现侧** 推荐阅读入口（你可随工程迭代改链接与说明）。

- 公开站根：`https://docs.quantinuum.com/inquanto/`（外链，非本站内容）  
- 机读真源：`docs-site/scripts/inquanto-tree.yaml`（版本见其中 `site_meta.inquanto_version_seen`）  
- 镜像生成：`npm run scaffold:mirror`  

**说明**：镜像页正文多为占位/审计摘要；**产品说明书**仍以 [产品功能](/product/features)、[四柱指南](/guide/) 与 [Reference](/reference/cli-and-scripts) 为准。

---

## 1. 顶层模块（与公开站导航同级）

| 公开站模块 | 公开路径规律 | 本站镜像（ZH） | 本站镜像（EN） | 工程文档入口（可改） |
|------------|----------------|----------------|------------------|------------------------|
| Introduction | `introduction/*.html` | [/mirror/introduction/](/mirror/introduction/) | [/en/mirror/introduction/](/en/mirror/introduction/) | [快速上手](/tutorial/quickstart) · [产品功能](/product/features) |
| Manual | `manual/**` | [/mirror/manual/](/mirror/manual/) | [/en/mirror/manual/](/en/mirror/manual/) | [指南总览](/guide/) · [原理与阅读](/guide/principles-and-reading) |
| Tutorials | `tutorials/**` | [/mirror/tutorials/](/mirror/tutorials/) | [/en/mirror/tutorials/](/en/mirror/tutorials/) | [教程目录](/tutorial/quickstart)（可扩展系列页） |
| API reference | `api/inquanto/**` | [/mirror/api/](/mirror/api/) | [/en/mirror/api/](/en/mirror/api/) | [HTTP API](/reference/http-api-sqlite-jobs) · [CircuitIR / TKET](/reference/circuitir-tket-jobs) |
| Extensions | `extensions/**` | [/mirror/extensions/](/mirror/extensions/) | [/en/mirror/extensions/](/en/mirror/extensions/) | [Reference](/reference/cli-and-scripts) · 源码 `pyproject` extras |
| Misc | `misc/**` | [/mirror/misc/](/mirror/misc/) | [/en/mirror/misc/](/en/mirror/misc/) | [安全与数据](/meta/security-and-data) · [站点地图](/meta/ia-mapping) |

---

## 2. Manual 一级分支（manifest 键序）

与 `vol-02-manual-hierarchy` 及 `inquanto-tree.yaml` 中 `manual.children` **键顺序** 对齐；**镜像索引** 为审计入口，**实现叙事** 以四柱与 Reference 为主。

| manifest 键 | 公开标题（中） | 镜像（ZH） | 建议工程侧（可改） |
|-------------|----------------|------------|---------------------|
| `howto` | 如何使用 | [/mirror/manual/howto/](/mirror/manual/howto/) | [快速上手](/tutorial/quickstart) · [工作流与 YAML](/tutorial/workflow-overview) |
| `geometry` | 几何 | [/mirror/manual/geometry/](/mirror/manual/geometry/) | [P1 指南](/guide/chemistry-and-embedding/) |
| `express` | Express 数据集 | [/mirror/manual/express/](/mirror/manual/express/) | [产品功能](/product/features)（配置与示例） |
| `symmetry` | 对称性 | [/mirror/manual/symmetry/](/mirror/manual/symmetry/) | [P1](/guide/chemistry-and-embedding/) · [P2](/guide/algorithms-and-protocols/) |
| `spaces_operators` | 空间 / 算符 | [/mirror/manual/spaces_operators/](/mirror/manual/spaces_operators/) | [P2](/guide/algorithms-and-protocols/) · [CircuitIR](/reference/circuitir-tket-jobs) |
| `ansatze` | Ansatze | [/mirror/manual/ansatze/](/mirror/manual/ansatze/) | [P2](/guide/algorithms-and-protocols/) |
| `minimizers` | 极小化器 | [/mirror/manual/minimizers/](/mirror/manual/minimizers/) | [P2](/guide/algorithms-and-protocols/) |
| `computables` | Computables | [/mirror/manual/computables/](/mirror/manual/computables/) | [P2](/guide/algorithms-and-protocols/) · [概念](/concept/engineering-architecture) |
| `protocols` | Protocols（五阶段） | [/mirror/manual/protocols/](/mirror/manual/protocols/) | [P2](/guide/algorithms-and-protocols/) · [缓解映射](/concept/mitigation-mapping) |
| `algorithms` | Algorithms | [/mirror/manual/algorithms/](/mirror/manual/algorithms/) | [P2](/guide/algorithms-and-protocols/) |
| `embedding` | 嵌入与 DMET | [/mirror/manual/embedding/](/mirror/manual/embedding/) | [P1](/guide/chemistry-and-embedding/) · [DMET · parity_snapshot](/reference/dmet-parity-snapshot) |
| `noise_mitigation` | 噪声缓解 | [/mirror/manual/noise_mitigation/](/mirror/manual/noise_mitigation/) | [P3](/guide/execution-and-analysis/) · [缓解映射](/concept/mitigation-mapping) |

---

## 3. Tutorials 分组（manifest）

| 分组（manifest） | 镜像（ZH） | 建议工程侧（可改） |
|------------------|------------|---------------------|
| `core` | [/mirror/tutorials/](/mirror/tutorials/) 下 core 子树 | [快速上手](/tutorial/quickstart) |
| `backends` | 同上 backends | [P3](/guide/execution-and-analysis/) · [切换 backend](/tutorial/switch-backend-compare) |
| `case_study_fe4n2` | 案例节点 | [案例 H₂ 家族](/tutorial/case-study-h2-family)（可换为 Fe4N2 系列） |
| `fragmentation` | fragmentation 子树 | [P1](/guide/chemistry-and-embedding/) · DMET 相关 Reference |

---

## 4. 维护约定

1. **改实现**：只改上表「建议工程侧」列链接与文案；**不必**改镜像 URL（由 manifest 驱动）。  
2. **改公开树结构**：编辑 `inquanto-tree.yaml` 后 `npm run scaffold:mirror`，再在此页 **同步增减行**（本页为人工母版）。  
3. **可选自动化**：若希望本表由脚本从 YAML 生成，可另加 `scripts/sync-inquanto-scaffold.mjs`（当前先保持 Markdown 易改）。

另见：[IA slug 映射](/meta/ia-mapping) · [安全与数据](/meta/security-and-data)。
