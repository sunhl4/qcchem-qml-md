---
title: IA slug 映射
description: 四柱命名、URL 与仓库文档映射
---

# 文档站信息架构：四柱与 slug

本页给出文档站核心信息架构，聚焦产品能力、指南路径与接口文档。

## 四柱

| ID | 中文名 | URL slug | 站内路径 |
|----|--------|----------|----------|
| P1 | 化学与嵌入 | `chemistry-and-embedding` | `/guide/chemistry-and-embedding/` |
| P2 | 算法与协议 | `algorithms-and-protocols` | `/guide/algorithms-and-protocols/` |
| P3 | 执行与分析 | `execution-and-analysis` | `/guide/execution-and-analysis/` |
| P4 | 作业与可复现 | `jobs-and-reproducibility` | `/guide/jobs-and-reproducibility/` |

## 文档类型与前缀

| 类型 | 前缀 | 用途 |
|------|------|------|
| Concept | `/concept/` | 架构边界、工程原则 |
| Tutorial | `/tutorial/` | 可运行上手路径 |
| Reference | `/reference/` | CLI/HTTP/字段契约 |
| Product | `/product/` | 产品能力与路线图 |

## 关键落地页

- `/product/features`：产品功能
- `/product/`：定位与路线
- `/product/roadmap`：路线图
- `/guide/`：指南入口
- `/reference/http-api-sqlite-jobs`：HTTP 作业接口

## 维护建议

- 新增页面优先挂到四柱路径下，避免分散入口。
- 新增路由后同步更新 `docs/.vitepress/config.ts` 导航与侧边栏。
- 概念页保持边界与术语稳定，教程页保持可执行与可验证。
