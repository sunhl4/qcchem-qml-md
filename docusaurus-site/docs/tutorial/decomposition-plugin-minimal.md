---
title: 分解插件（embedding.plugin）
description: "用 embedding.mode: plugin 接入外部分片哈密顿量；玩具 JSON 最小用法与验证。"
sidebar_position: 48
---

# 分解插件（embedding.plugin）

:::tip 相关手册
[嵌入总览](/modules/chem/embedding) · [embedding 配置字段](/reference/config-fields/embedding) · [P1 化学与嵌入](/guide/chemistry-and-embedding)
:::

当你已经有一份「分片后的量子比特哈密顿量」（例如外部分解代码写出的 Pauli 项），不必走完整的 DMET / 投影路径，可以用 **`embedding.mode: plugin`** 把它注入管线。

本页教你：**怎么开这个接口、玩具示例怎么跑、结果里看什么。**

## 决策块

| | |
|--|--|
| **何时用** | 已有外部分解 / 分片结果，要以 JSON 形式接入 `qchem-stack` 跑 VQE / 导出 `repro` |
| **何时不用** | 第一次学嵌入 → 用 [DMET](./dmet-self-consistent) 或 [投影](./projection-embedding-deep-dive)；需要内置 Schmidt 自洽 → `mode: dmet` |
| **互斥 / 注意** | `mode: plugin` 会**替换**分子活性空间建哈密顿量；当前内置插件名仅 `uniform_fragment_guess`；玩具 JSON **不是**生产分解产品 |
| **链教程 + 深读** | 本页 · [嵌入总览](/modules/chem/embedding) · [配置字段 · plugin](/reference/config-fields/embedding) |

## 接口怎么用

在实验 YAML 里设置：

```yaml
embedding:
  mode: plugin
  plugin:
    name: uniform_fragment_guess   # 目前支持的内置名
    json_path: configs/decomposition_plugin_toy_integrals.json
```

| 字段 | 含义 |
|------|------|
| `embedding.mode` | 设为 `plugin`，走插件建哈密顿量分支 |
| `plugin.name` | 插件实现名（内置：`uniform_fragment_guess`） |
| `plugin.json_path` | 分片载荷 JSON（相对配置或仓库根） |

JSON 最小形状（玩具 schema `decomposition_plugin_toy_v1`）：

```json
{
  "schema": "decomposition_plugin_toy_v1",
  "primary_fragment_id": "f0",
  "fragments": {
    "f0": {
      "n_qubits": 2,
      "fermion_qubit_mapping": "jordan_wigner",
      "pauli_coefficients": [
        { "label": "II", "coeff": -0.55 },
        { "label": "ZI", "coeff": -0.2 },
        { "label": "ZZ", "coeff": 0.08 }
      ]
    }
  }
}
```

管线会读取 **主分片**（`primary_fragment_id`）上的 Pauli 项，构造 `QubitHamiltonian`，再进入后续变分 / 导出。详细嵌套键见仓库 [`docs/说明_embedding配置.md`](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/说明_embedding配置.md)。

## 代表配置

| 文件 | 作用 |
|------|------|
| `configs/example_decomposition_plugin_toy.yaml` | 完整实验 YAML（已打开 `mode: plugin`） |
| `configs/decomposition_plugin_toy_integrals.json` | 玩具分片 Pauli 载荷 |

## 前置

```bash
pip install -e ".[chem]"
```

在仓库根目录执行下面的命令。

## 验证命令

**1. 确认配置与插件字段可加载**

```bash
python3 -c "
from qchem_stack.config import load_experiment_config
c = load_experiment_config('configs/example_decomposition_plugin_toy.yaml')
print(c.experiment_id)
print(c.embedding.mode)
print(c.embedding.plugin.name)
print(c.embedding.plugin.json_path)
"
```

**2. 跑通插件路径的端到端测试**

```bash
python -m pytest tests/chem/test_decomposition_plugin_pipeline.py -q --no-cov
```

**3.（可选）导出 parity 表，检查插件相关字段**

```bash
python scripts/export_parity_criteria_table.py configs/example_decomposition_plugin_toy.yaml
```

在输出 / `run_summary` 中可关注与分解插件相关的键（如 `decomposition_plugin`、`decomposition_plugin_schema`）。

## 期望输出

- 步骤 1：退出码 `0`；打印 `decomp_plugin_toy_001`、`plugin`、`uniform_fragment_guess` 与 JSON 路径
- 步骤 2：pytest 通过
- 步骤 3（若运行）：进程退出码 `0`

## 下一步

- 真实嵌入路径：[DMET 自洽](./dmet-self-consistent) · [Projection 深读](./projection-embedding-deep-dive)
- 字段字典：[embedding 配置字段](/reference/config-fields/embedding)
- 案例互链：[H₂ 家族](./case-study-h2-family)
