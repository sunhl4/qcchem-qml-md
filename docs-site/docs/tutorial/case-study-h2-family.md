---
title: 案例：H₂ 家族上链式改 quantum 与 backend
description: 从单份基线 YAML 出发，对齐 vol-03 式「改一处、看全局」的练习顺序
---

本页是**阅读顺序建议**，不是单一可执行脚本；权威键名与合法取值仍以仓库 YAML 与 [工作流与 YAML 概览](/tutorial/workflow-overview) 为准。

## 基线

从 **`configs/example_h2.yaml`** 出发：记清顶层块（`molecule`、`scf`、`active_space`、`quantum`、`backend`、`compiler` / `mitigation` / `embedding`）在你本地跑出 **基线能量与 repro**。

## 链式变体（建议顺序）

1. **只改 `backend`**：对照 [同一份 YAML 切换 backend](/tutorial/switch-backend-compare) 中的示例文件，观察 `repro` 与资源摘要差异。  
2. **在固定 backend 下改 `quantum.algorithm` 叙事**（若你使用 VQE / ADAPT 等变体）：每次只改一类算法开关，保留分子与 SCF 不变。  
3. **激发 / QPE 烟测**：用 `example_h2_excited_smoke.yaml`、`example_h2_qpe_track.yaml` 等同族文件，理解「多阶段」在 `pipeline_profile` 中的体现。  
4. **链式教程 YAML**：打开 **`configs/tutorial_inquanto_chain_h2.yaml`**，对照 [工作流与 YAML 概览](/tutorial/workflow-overview) 里对「多步实验」的叙事。  
5. **分解插件玩具**：**`configs/example_decomposition_plugin_toy.yaml`**（`embedding.mode: plugin`）与矩阵 §3「分解插件」行及 [公开 Parity 矩阵](/product/roadmap) 对照。

## 收束

把每次运行的 **`experiment_id` / `random_seed`** 与 **`repro`** 片段存档，便于与 CI 或 [Parity](/product/roadmap) 导出对齐（若你负责验收）。
