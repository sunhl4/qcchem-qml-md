---
title: 配置示例目录
description: configs/ 下 YAML 分组索引（ExperimentConfig、MD loop、profiles、scenarios）。
---

# 配置示例目录

仓库 [`configs/`](https://github.com/sunhl4/qcchem-qml-md/tree/main/configs) 当前含 **118** 个顶层 YAML：**107** 个 `ExperimentConfig`、**11** 个 `MdValidationLoopConfig`；另有 **3** 个 `profiles/`、**8** 个 `scenarios/`（`qchem-run --list-scenarios`）。完整列表由脚本生成，勿手改 body。

## 入门三件套

1. `example_h2.yaml` — 默认 pipeline  
2. `example_h2_precomputed_bundle.yaml` — 无 PySCF  
3. `tutorial_chain_h2.yaml` — 教程链  

场景快捷入口：`configs/scenarios/minimal_vqe.yaml` 等。

## 模板

复制 [`configs/_template.yaml`](https://github.com/sunhl4/qcchem-qml-md/blob/main/configs/_template.yaml) 并按注释修改字段。

## 字段参考

按块查字段：[配置字段参考](./config-fields/)（molecule / scf / quantum / …）。

## 完整列表（自动生成）

见 [configs-catalog-body](./configs-catalog-body.md)（`python3 scripts/generate_configs_catalog.py`）。

哪些配置有教程：[配置 ↔ 教程矩阵](./tutorial-config-matrix)。

## Parity 门控

```bash
python3 scripts/check_parity_export_sample.py
```
