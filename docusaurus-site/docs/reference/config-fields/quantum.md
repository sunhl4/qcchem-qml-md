---
title: quantum 配置字段
description: algorithm、variational/vqe/adapt/iqeb/pauli 与激发态子块。
---

# `quantum` — 量子计算阶段怎么配

> **返回索引：** [配置字段](./) · 仓库 [说明_config模块技术参考手册.md](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/说明_config模块技术参考手册.md)

**源码：** `quantum.py`, `quantum_specs.py`  
**详细说明：** [说明_quantum配置.md](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/说明_quantum配置.md)

## 顶层

| 字段 | 默认 | 说明 |
|------|------|------|
| `algorithm` | `"vqe"` | 内置算法 id 或 factory 标签 |
| `algorithm_factory` | `None` | 自定义 runner，格式 `module:callable` |

## 主要子块

| 子块 | 干什么 | 常见字段 |
|------|--------|----------|
| `variational` | 选 ansatz | `ansatz`, `uccsd_trotter_steps` |
| `vqe` | VQE 超参 | `depth`, `maxiter`, `optimizer_method` |
| `adapt` | ADAPT | `max_iter`, `pool_id` |
| `iqeb` | IQEB | `pool_id`, `n_grads`, `max_rounds` |
| `pauli` | Pauli 协议 | `use_protocol`, `grouping`, `run_sampled` |
| `excited.*` | 激发态（VQD/QSE/SCEOM） | `after_variational`, 各方法参数 |
| `demos.*` | QPE/VQS 演示 sidecar | |
| `tensornet` | Tensor network stub | |
| `graph` | workflow preview 图边 | |

**谁在用：** 变分阶段、激发态阶段、Pauli 协议与收尾、复现字段导出。

相关：[量子模块](/modules/quantum/) · [算法索引](/modules/quantum/algorithms/) · [FAQ：采样互斥](/faq/)。
