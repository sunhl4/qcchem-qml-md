---
title: 配置示例目录
description: configs/ 下 105 个 YAML 的分组索引（97 ExperimentConfig + 8 MdValidationLoopConfig）。
---

# 配置示例目录

仓库 [`configs/`](https://github.com/sunhl4/qcchem-qml-md/tree/main/configs) 当前含 **105** 个 YAML：**97** 个 `ExperimentConfig`、**8** 个 `MdValidationLoopConfig`。完整分组索引见 [`configs/README.md`](https://github.com/sunhl4/qcchem-qml-md/blob/main/configs/README.md)。

## 入门三件套

1. `example_h2.yaml` — 默认 pipeline
2. `example_h2_precomputed_bundle.yaml` — 无 PySCF
3. `tutorial_chain_h2.yaml` — 教程链

## 模板

复制 [`configs/_template.yaml`](https://github.com/yaozheng/qchem-stack/blob/main/configs/_template.yaml) 并按注释修改字段。

## 完整列表（自动生成）

见 [configs-catalog-body](./configs-catalog-body.md)（由 `python scripts/generate_configs_catalog.py` 同步）。

## Parity 门控

```bash
python scripts/check_parity_export_sample.py
```
