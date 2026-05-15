---
title: 路线图
description: P0–P2 工程节拍与里程碑索引
---

# 路线图

本页把工程叙事 **压缩成一页目录**；细则见 **[P2 详细实施计划](/concept/p2-detailed-plan)**。

## 节拍总览（概念）

标签 **P0 / P1 / P2** 用于内部工程节拍；**除非项目另有钉扎**，否则不强行绑日历季度。

```mermaid
flowchart TB
  subgraph P0["P0 — 判据与复现闭合"]
    a[parity_snapshot / repro]
    b[export_parity_criteria_table · CI]
  end
  subgraph Y1["Y1 Q3（文档命名）"]
    l[L3 小体系数值基准]
  end
  subgraph P1["P1 — 嵌入 · 激发态 · 缓解报告"]
    c[EmbeddingSpec / DMET 钩子]
    d[激发态 shots 汇总一致性]
    e[PMSV 报告块]
  end
  subgraph P2["P2 — 长线轨道与设备采样"]
    f[同一配置树下 QPE / FT 示范]
    g[Qiskit 比特串 Pauli 路径]
  end
  P0 --> Y1
  P0 --> P1
  P1 --> P2
```

## 延伸阅读索引

| 主题 | 页面 |
|------|------|
| 路线图 P2（全文） | [P2 详细实施计划](/concept/p2-detailed-plan) |
| 工程架构 | [工程分层架构](/concept/engineering-architecture) |
| API 与作业 | [HTTP API · SQLite 作业](/reference/http-api-sqlite-jobs) |

## 返回产品与上手

- [产品功能](/product/features) · [定位与路线](/product/) · [15 分钟上手](/tutorial/quickstart) · [指南总览](/guide/)
