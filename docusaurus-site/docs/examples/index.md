---
title: 示例
description: 可运行脚本、YAML 与 notebook 的任务索引。
---

# 示例

按任务索引可运行脚本与 YAML。正文与仓库 `examples/README.md` 同步（[完整列表](./gallery-body)）。

:::tip 怎么选
第一次用 → [15 分钟上手](../tutorial/quickstart)；改算法或后端 → [配置目录](../reference/configs-catalog)；配置是否有教程 → [教程矩阵](../reference/tutorial-config-matrix)。
:::

## 按主题

### 变分与算法

- [HEA / H₂ 基线](./gallery-body) — `example_h2.yaml`
- [ADAPT singles 池教程](../tutorial/adapt-pool-smoke) — `example_h2_adapt_singles_pool.yaml`
- [UCCSD Trotter](../tutorial/uccsd-trotter-export)
- [GQE 变体加载](../tutorial/gqe-variants) · [GQE Nakaji](../tutorial/gqe-nakaji-h2)

### 嵌入与经典化学

- [DMET 自洽](../tutorial/dmet-self-consistent) — `example_h4_dmet_self_consistent.yaml`
- [ONIOM 烟测](../tutorial/oniom-smoke) — `example_oniom_toy.yaml`
- [Projection 深读](../tutorial/projection-embedding-deep-dive)
- [CASSCF 审计](../tutorial/casscf-audit-workflow)

### 执行、缓解与 QPE

- [切换后端对比](../tutorial/switch-backend-compare)
- [ZNE Qiskit](../tutorial/zne-qiskit-repro)
- [QPE track](../tutorial/qpe-track) — `example_h2_qpe_track.yaml`

### 作业与 MD/ML

- [HTTP 异步](../tutorial/async-run-via-http)
- [读 repro 键](../tutorial/read-repro-keys)
- [MD/ML 主动学习](../tutorial/md-ml-active-learning)

## 快速烟测

```bash
python examples/run_all_smoke.py
```

## 仓库示例索引（自动生成）

完整列表见 **[gallery-body](./gallery-body)**（`python scripts/generate_examples_gallery.py`）。

## 相关入口

| 目标 | 链接 |
|------|------|
| 教程逐步做 | [教程](../tutorial/) |
| 配置↔教程矩阵 | [tutorial-config-matrix](../reference/tutorial-config-matrix) |
| 手册选型 | [指南总览](../guide/) |
| Python SDK | [SDK facade](../reference/python-sdk) |
| 配置 YAML | [configs catalog](../reference/configs-catalog) |
