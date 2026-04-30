# Vol.05 API 参考 — 组织模式与与手册的三角链接

**读者**：库维护者、IDE 用户体验设计者。  
**证据**：抓取 [`api/inquanto/protocols.html`](https://docs.quantinuum.com/inquanto/api/inquanto/protocols.html) 返回 **大体积** HTML（>360KB），符合 **全符号展开** 的 Sphinx 风格 API 页；`api/index.html` 根路径 **404** — 入口可能为 `api/inquanto/` 目录索引或其它路由（**待证实**，附录 B 仍给出完整 URL）。

---

## 1. URL 模式（已证实）

- 模块页：`api/inquanto/<module>.html`（如 `protocols.html`、`algorithms.html`）。
- 类锚点：`#inquanto.protocols.PauliAveraging` 形式（manifest 生成类叶链接时使用）。

---

## 2. 模块 — 类 — 方法 三层（推断）

标准 Sphinx Autosummary / automodule 模式：

1. **模块页**顶部：模块 docstring、子模块列表、`__all__` 概要。
2. **类**：构造函数参数、方法表、`See Also`。
3. **方法**：签名、`Parameters` / `Returns`、**Examples** 代码块。

**与 Manual 的互链**：类页底部或正文侧栏常出现 **「User guide」** 链回 `manual/protocols_overview.html` 等 — 形成 **API ↔ Manual** 回路。

---

## 3. 大页性能与可读性（推断）

`protocols` 单页极大 — **推断** 为单 HTML 聚合多类，利于 **Ctrl+F** 与 SEO，但 **移动端与弱网** 体验一般。

**对自建站启示**：VitePress + vitepress-plugin 可按 **类拆 route**（你们 mirror 已拆类叶）— **可视为优于单页巨石 HTML** 的架构选择。

---

## 4. manifest 中 `classes:` 块

[`inquanto-tree.yaml`](../../docs-site/scripts/inquanto-tree.yaml) 在 `api.*.classes` 下列出 **算法 / 协议** 等级别的公开类；本站 `scaffold-mirror.mjs` 为每个类叶生成 **独立 mirror URL** — 这是对 Sphinx 默认「单页多锚」的 **信息架构增强**（利于分享与状态徽章）。

---

## 5. 本卷结论

InQuanto API 文档 = **符号真值 + 与手册强耦合**。自建站应在 **Reference** 区保持 **HTTP 契约、YAML schema、parity 键** 等 **机读参考**，与 **Mirror 类叶** 互补而非重复堆字。

**补充（按 `api/inquanto/` 子模块族拆解）**：[`vol-09-api-modules-and-misc-supplement.md`](./vol-09-api-modules-and-misc-supplement.md) · **侧栏 ↔ manifest 对拍**：[`vol-10-official-sidebar-vs-manifest.md`](./vol-10-official-sidebar-vs-manifest.md)。

**下一卷**：[`vol-06-content-types-and-diataxis.md`](./vol-06-content-types-and-diataxis.md)。
