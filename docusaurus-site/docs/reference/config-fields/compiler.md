---
title: compiler 配置字段
description: optimization_level、native_twoq 与 compiler passes。
---

# `compiler` — 线路怎么编译

> **返回索引：** [配置字段](./) · 仓库 [说明_config模块技术参考手册.md](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/说明_config模块技术参考手册.md)

| 字段 | 默认 | 说明 |
|------|------|------|
| `optimization_level` | `1` | 优化等级 0–3 |
| `native_twoq` | `"CX"` | 原生双量子门 |
| `preoptimize_passes` | `[]` | 化学/ansatz 相关 pass |
| `compiler_passes` | `[]` | 目标后端 pass |

相关：[CircuitIR / tket](/reference/circuitir-tket-jobs)。
