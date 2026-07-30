# `quantum` — 量子计算阶段怎么配

> **返回索引：** [说明_config模块技术参考手册.md](说明_config模块技术参考手册.md#8-各-section-简介)

**源码：** `quantum.py`, `quantum_specs.py`  
**详细说明：** [说明_quantum配置.md](说明_quantum配置.md)

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
| `iqcc` | iQCC / iQCC+PT | `max_steps`, `top_k`, `enable_pt`, `pool_mode`, `coeff_atol`, `denom_cutoff` |
| `pauli` | Pauli 协议 | `use_protocol`, `grouping`, `run_sampled` |
| `excited.*` | 激发态（VQD/QSE/SCEOM） | `after_variational`, 各方法参数 |
| `demos.*` | QPE/VQS 演示 sidecar | |
| `tensornet` | Tensor network stub | |
| `graph` | workflow preview 图边 | |

**谁在用：** 变分阶段、激发态阶段、Pauli 协议与收尾、复现字段导出。
