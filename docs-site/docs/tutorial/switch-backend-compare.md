---
title: 同一份 YAML 切换 backend 做对比
description: 只改 backend 块，对比 statevector、Qiskit shots 等路径差异
---

## 思路

在固定 `molecule`、`scf`、`active_space`、`quantum` 的前提下，只调整 **`backend`**（及该后端所需的子键，如 Qiskit 的 shots），可以**隔离**「执行面」对结果形态（精确能量 vs 采样、资源摘要字段）的影响。

## 建议对照组

1. **`configs/example_h2.yaml`** — `statevector`（或默认无采样路径），作为基线。  
2. **`configs/example_h2_qiskit_shots.yaml`** — 同一化学与量子叙事下走 **Qiskit shots / 比特串**（需安装 quantum 相关 extra）。  
3. **`configs/example_h2_sampled.yaml`** — 与基线对比 **Pauli 采样协议**路径（若与你的实验相关）。

## 操作提示

- 合并差异时优先 diff **`backend`** 与 **`quantum`** 中与采样相关的段落，避免无意改动 `molecule`。  
- 跑完后对比 **`repro`** 中的 `pipeline_profile` 与（若有）**资源摘要**字段。  
- 安装与 CLI 入口见 [命令行与脚本](/reference/cli-and-scripts)、[15 分钟上手](/tutorial/quickstart)。

更细的合法取值与白名单以 Reference 与 Pydantic 模型为准。
