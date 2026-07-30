---
title: 文档版本策略
description: 文档站与软件包版本如何对齐（stable / next）。
---

# 文档版本策略

## 当前状态

Docusaurus 站跟踪仓库 **main**（GitHub Pages），与 PyPI 包版本通过产品 [Changelog](/changelog/) 与仓库 [`CHANGELOG.md`](https://github.com/sunhl4/qcchem-qml-md/blob/main/CHANGELOG.md) 对齐。

尚未启用 `@docusaurus/plugin-content-docs` 的多版本目录（`versioned_docs/`）。原因：单维护者优先保证 main 契约正确；多版本会显著增加同步成本。

## 推荐阅读方式

| 你使用的软件 | 读哪里 |
|--------------|--------|
| 最新 PyPI（如 1.1.x） | 本站 + Changelog 对应小节 |
| 可编辑源码 / main | 本站即真相；注意 Unreleased |
| 旧环境复现 | 锁定 git tag / 包版本，对照当时 CHANGELOG |

## 未来（可选）

当需要长期支持多 major 时：

1. `npm run docusaurus docs:version x.y.z`  
2. 保留 `current` = next、`versioned_docs/version-x.y.z` = stable  
3. Navbar 增加 version dropdown  

在此之前，以 **CHANGELOG + schema_ids / api_contract_version** 作为契约版本真相。
