# Vol.03 Tutorials 与案例研究 — 叙事节奏与受众

**读者**：开发者体验（DX）、培训材料设计者。  
**真源**：[`mirror-doc-tree.yaml`](../../docs-site/scripts/mirror-doc-tree.yaml) `tutorials:` 子树；`tutorial_overview` 抓取 **超时** — 结构以 manifest 为准。

---

## 1. Tutorials 在 Diátaxis 中的角色

Tutorials 属于 **「教程」型内容**：假设读者 **按顺序执行** 代码单元或脚本步骤，目标为 **可运行工件**（曲线图、能量表、作业 ID）。与 Manual 的 **解释性** 相比，Tutorials **允许重复** Manual 中的公式与图示，以降低认知负荷。

---

## 2. 二级分类（manifest）

| 分组 | manifest 键 | 意图 |
|------|---------------|------|
| Core | `core` | VQE / VQD / 可视化入门 |
| Backends | `backends` | 模拟器、编译、异步、shots、Nexus、硬件提交 |
| Case study | `case_study_fe4n2` | 工业级多步骤案例（Fe4N2） |
| Fragmentation | `fragmentation` | DMET / 投影 / NEVPT2 / WFT-in-DFT |

---

## 3. 代表性教程节点与依赖

| 教程 | 依赖前置知识 | 与 Manual 重叠点 |
|------|--------------|------------------|
| `InQ_tut_VQE` | quickstart | algorithms VQE、express |
| `InQ_tut_backends` | protocols compile/run | TKET backend 文档 |
| `InQ_tut_qiskit_shots` | Pauli averaging | protocols expval、shots 语义 |
| `InQ_tut_async` | launch/retrieve | protocols 异步 API |
| `InQ_tut_dmet` | manual dmet | embedding、fragmentation |
| `InQ_tut_fe4n2_*` | 大体系活性空间 | case study 多集叙事 |

---

## 4. 案例研究（Fe4N2）模式（推断）

多 HTML 文件拆分 **同一化学体系** 的不同阶段（CASSCF → ADAPT → 噪声硬件），类似 **迷你系列剧**：

- **优势**：读者可 **分次完成**，符合长任务注意力曲线。
- **对自建站启示**：对「模拟器云上的长作业」，可采用 **同一 `experiment_id` 多篇运行手记** 或 **流水线阶段页**。

---

## 5. Nexus / 硬件类教程（manifest 标注 n/a）

`InQ_tut_nexus`、`InQ_tut_helios` 等在 parity 口径为 **not-applicable**。文档站仍保留 **vendor 官方教程** 以服務商业用户；**自建开源站** 应改为：

- **本地 SQLite + FastAPI** 教程；或
- **通用 Qiskit Runtime / Braket** 占位（若未来支持）。

---

## 6. 与本仓库对照

| 维度 | InQuanto tutorials | `docs-site` |
|------|-------------------|-------------|
| 笔记本 HTML | 多页 | 当前以 `/tutorial/quickstart` 为主 — **可扩展系列** |
| 异步作业 | 有 | `jobs`、`/reference/http-api-sqlite-jobs` 可对齐 `InQ_tut_async` |
| Nexus | 有 | 显式 n/a + `launch-retrieve-nexus-analog` concept |

---

## 7. 本卷结论

Tutorials = **可执行复现路径** + **可选商业后端分支**。自建站要超越对标：为 **每条公开 YAML 配方** 提供 **一键 `repro` 导出** 与 **CI smoke** 链接（你们已在工程路线中部分落地）。

**下一卷**：[`vol-04-extensions-packaging.md`](./vol-04-extensions-packaging.md)。
