# Vol.11 节点 backlog 与 Wave 执行法

**读者**：文档站 owner、对标工程 owner。  
**定位**：把 **附录 C（人读、~2.1 万行）** 与 **机读 backlog（JSON）** 的分工写清，避免混用。

---

## 1. 双轨产物

| 产物 | 路径 | 作用 |
|------|------|------|
| 附录 C | `appendix-C-deep-node-architecture.generated.md` | 评审会 / 架构走读：每节点同构段落（兄弟、风险、验收）。 |
| 机读 backlog | `../inquanto-node-backlog.generated.json`（相对本目录为 `qchem_qml_md/docs/`） | CI、`jq` 过滤、与 `check:mirror` 同源的 **295 行任务包**。 |
| 索引表 | `../inquanto-node-backlog.generated.md` | 轻量目录；含 appendix 节点序号列。 |

再生成：`cd docs-site && npm run report:inquanto-backlog && npm run check:node-backlog`。

---

## 2. 创新字段（相对「照抄 InQuanto」）

- **`differentiator_focus`**：显式标 **mirror_audit / repro_contract / cloud_tenant / multi_backend / parity_evidence**，便于按 **自建模拟器云** 叙事排期，而非按厂商章节抄页。
- **`suggested_internal_routes`**：指向本站 `/mirror/`、`/cloud/`、`/parity/`、`/guide/` — 与 Vol.08 目标 IA 一致。
- **`platform_dimensions`**：结构化 §11，便于未来接 Dashboard 或 issue 模板。

---

## 3. Wave 与 DoD（摘要）

全表见 [Vol.08](./vol-08-target-qchem-docs-and-cloud.md) 与仓库 `docs/InQuanto_Y1_public_alignment_ledger.md` §3.5。**原则**：每 wave 有可度量 DoD（测试、parity 行、或 `/cloud/` 契约段落），不抄 HTML。

---

## 4. 返回

[`INDEX.md`](./INDEX.md) · 对拍 [Vol.10](./vol-10-official-sidebar-vs-manifest.md)。
