---
title: Generative Quantum Eigensolver（选型）
description: 何时用 GQE / 何时不用；深读见 modules 算法手册。
---

# Generative Quantum Eigensolver（选型）

:::tip 模块手册（唯一深读）
原理、数学、YAML 全字段与调用见 **[GQE 算法深读](/modules/quantum/algorithms/gqe)**。本页只做选型，不重复公式。
:::

GQE 是顶层 `gqe:` **侧车**（`integrations.gqe`），**不是** `quantum.algorithm`。依赖：`pip install "qchem-stack[gqe]"`。

## 何时用

| 场景 | 适合？ |
|------|--------|
| 对照 Nakaji GPT-QE 数值（H₂ / LiH / …） | 是 |
| 离散 token 序列探索 ansatz 组合 | 是 |
| 标准连续变分 HEA / UCCSD | 否 → [VQE](/modules/quantum/algorithms/vqe-hea) |
| 硬件 shots / 噪声实验 | 默认否（statevector oracle） |

## 何时不用

- 只要基态烟雾：用 `quantum.algorithm: vqe`
- 未装 JAX/optax：先装 `[gqe]` 或改走 VQE
- 需要 `quantum.algorithm` 注册表 ID：GQE 不在其中

## 代表配置

- `configs/example_h2_gqe_gpt.yaml` · `example_h2_gqe_plan_b.yaml`
- `example_h2_gqe_prefill.yaml` · `example_h2_gqe_condition.yaml`

教程：[GQE 变体](/tutorial/gqe-variants) · [Nakaji H₂](/tutorial/gqe-nakaji-h2)。

## 相关

[P2 程序构建](./program-construction) · [integrations](/modules/integrations) · [算符池](/modules/quantum/algorithms/operator-pools)
