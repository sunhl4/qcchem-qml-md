---
title: 配置示例目录
description: configs/ 下 77 个 YAML 的分组索引。
---

# 配置示例目录

完整分组索引见仓库 [`configs/README.md`](https://github.com/yaozheng/qchem-stack/blob/main/configs/README.md)。

## 入门三件套

1. `example_h2.yaml` — 默认 pipeline
2. `example_h2_precomputed_bundle.yaml` — 无 PySCF
3. `tutorial_chain_h2.yaml` — 教程链

## 模板

复制 [`configs/_template.yaml`](https://github.com/yaozheng/qchem-stack/blob/main/configs/_template.yaml) 并按注释修改字段。

## Parity 门控

```bash
python scripts/check_parity_export_sample.py
```
