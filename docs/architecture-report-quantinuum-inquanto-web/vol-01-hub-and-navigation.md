# Vol.01 枢纽页、全局导航与外链策略

**读者**：前端 / 文档工程师 / 品牌与增长。  
**范围**：`https://docs.quantinuum.com/inquanto/` 根枢纽及全站导航 **模式**（非闭源控制台实现细节）。

---

## 1. 根枢纽三柱（已证实）

根页将产品能力收敛为三条 **并列叙事**，每条包含：

- **一句话价值**（解决什么问题）。
- **能力关键词**（drivers、post-HF、DMET、algorithms、protocols、composables、simulators、hardware、error reduction 等）。
- **深链 CTA** 指向 `manual/` 下具体 HTML（如 `computables/evaluating_w_protocols.html`、`errmit.html`）。

**设计意图**：新用户在 **30 秒内** 找到「我属于化学 / 算法 / 执行哪一类问题」，并跳入手册；老手可忽略三柱，直接用搜索或 API。

---

## 2. 全局导航元素（已证实 + 推断）

| 元素 | 出现位置 | 作用 |
|------|-----------|------|
| Nexus Portal | 顶栏 | 将 **文档读者** 导流到 **商业作业平台** |
| Product Updates | 顶栏 | 版本 / 变更公告入口 |
| Support / Contact | 页脚区 | 工单与售前支持 |
| Publications | 页脚 | 学术信任背书 |

**推断**：顶栏链接在 **全 Quantinuum 文档域** 可能共享（与 TKET、Nexus 文档统一壳层），利于 **单点登录与品牌一致**。

---

## 3. 用户角色分流（推断模型）

| 角色 | 典型入口 | 期望路径 |
|------|-----------|-----------|
| 量子化学研究者 | Chemical Specification → manual geometry / embedding | 深入 `manual/dmet`、教程 fragmentation |
| QC 算法开发者 | Program Construction → computables / protocols / algorithms | API `inquanto.protocols` |
| 平台集成方 | Execution → backends / mitigation + Nexus 教程 | `tutorials` backends、Nexus 文档 |
| 合规 / 采购 | misc license + 外部 Publications | 合同附录引用 |

自建 **模拟器云平台** 时，建议在枢纽增加第四柱或副导航：**「租户与作业」**，与 InQuanto 依赖 Nexus 外链的做法 **解耦**。

---

## 4. URL 与信息 scent（已证实）

- 手册与教程普遍为 **扁平 `.html` 文件**，路径即主题（如 `manual/protocols_overview.html`），利于 SEO 与分享。
- API 为 `api/inquanto/<module>.html`，类锚点为 `#inquanto.protocols.PauliAveraging` 形态（见 manifest 中类叶锚拼接逻辑）。

**对自建站启示**：保持 **稳定 slug**；版本切换若存在，应 **不破坏** 旧 URL 或提供重定向表。

---

## 5. 与本仓库 `docs-site` 对照

| InQuanto 模式 | 本仓库当前实现 | 差距 / 建议 |
|---------------|----------------|-------------|
| 三柱品牌枢纽 | 首页 Hero + 四柱 `PillarCard` | 可考虑在 `/product/` 增加 **与三柱映射的一屏图** |
| 顶栏 Nexus | 无（刻意不做） | 用 **「本地 runs API」** 文案替代 |
| 全站搜索 | VitePress Local Search | 已具备；可扩展 `minisearch` 字段权重 |
| 版本号在 title | `mirror-doc-tree.yaml` 版本字段 | 可在 `/mirror/` 页眉展示 `upstream_doc_version_seen` |

---

## 6. 本卷结论

InQuanto 枢纽 = **品牌三柱 + 商业导流 + 深链手册**。自建站若要 **优于** 对标：在 **不绑 Nexus** 前提下，用 **一页讲清「开源 + repro + 多后端」**，并把 **作业 / 租户** 纳入主导航，避免读者在「库文档」与「云控制台」之间来回跳转。

**下一卷**：[`vol-02-manual-hierarchy.md`](./vol-02-manual-hierarchy.md)。
