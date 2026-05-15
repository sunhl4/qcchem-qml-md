# Vol.06 内容类型与 Diátaxis 映射

**读者**：信息架构师、技术写作规范制定者。

---

## 1. Diátaxis 四象限回顾

| 象限 | 读者问题 | InQuanto 典型载体 |
|------|-----------|-------------------|
| Tutorial | 带我一步步做出结果 | `introduction/quickstart`、`tutorials/InQ_tut_*` |
| How-to guide | 我要完成某具体任务 | `manual/howto`、Protocols 五阶段操作段 |
| Explanation | 为什么这样设计 | Manual 概念章节（spaces、embedding 理论） |
| Reference | 精确符号与字段 | `api/inquanto/*`、Express 数据说明 |

InQuanto **混合** 在同一 HTML 中（尤其 Manual）— **非严格 Diátaxis 纯净实现**，但 **对读者友好**（减少跳转）。

---

## 2. 将 manifest 的 `diataxis` 字段映射到四象限

[`mirror-doc-tree.yaml`](../../docs-site/scripts/mirror-doc-tree.yaml) 使用 `concept | tutorial | reference | parity`：

| manifest 值 | 推荐对应 Diátaxis | 说明 |
|---------------|-------------------|------|
| `tutorial` | Tutorial | 教程区 |
| `concept` | Explanation + 部分 How-to | Manual 主体 |
| `reference` | Reference | API、Express、minimizers |
| `parity` | Reference（契约）+ Explanation（边界） | 对标矩阵、签 off |

---

## 3. 本仓库 `docs-site` 推荐映射

| 本站路径前缀 | Diátaxis | 内容 |
|--------------|----------|------|
| `/tutorial/` | Tutorial | 可运行最短路径 |
| `/guide/` | How-to + 轻 Explanation | 四柱任务视图 |
| `/concept/` | Explanation | 架构、竞争、边界 |
| `/reference/` | Reference | HTTP、CircuitIR、DMET 契约 |
| `/parity/` | Reference + 治理 | 矩阵、签 off、路线图 |
| `/mirror/` | Reference（索引） | 公开树节点 + 状态 |
| `/product/` | Explanation（产品） | 价值主张、差异化 |

---

## 4. 内容重复策略建议

| 策略 | 适用 |
|------|------|
| **DRY** | API 签名、HTTP 字段表 |
| **刻意重复** | Quick-start 与 Tutorial 第一段「环境准备」 |
| **链接代替重复** | Manual 概念 → Reference 表 |

---

## 5. 本卷结论

InQuanto 文档站 **实用主义混合 Diátaxis**；自建站可用 **更干净的分区** 作为差异化 — 以 **四柱 + Product + Parity** 强制分流，降低「在手册里找 API 默认值」的摩擦。

**下一卷**：[`vol-07-ux-search-seo-i18n.md`](./vol-07-ux-search-seo-i18n.md)。
