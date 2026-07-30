---
title: 教程验证块模板
description: 所有可运行教程页必须包含的「验证命令 / 期望输出」约定（AEO + CI）。
---

# 教程验证块模板

每个可运行教程页（`docusaurus-site/docs/tutorial/*.md`，索引页除外）**必须**包含下列两节，供人类与检索/CI 抽取。

## 验证命令

用**一条**可复制的主命令（bash 或 python）。优先仓库根目录可执行路径。

````markdown
## 验证命令

```bash
python scripts/smoke_pipeline.py --config configs/example_h2.yaml
```
````

## 期望输出

用条目列出可判定的成功条件（退出码、关键 JSON 键、HTTP 状态等）。避免模糊形容词。

````markdown
## 期望输出

- 进程退出码 `0`
- 结果含 `pre_quantum_input.hamiltonian_fingerprint`
- （可选）对照 `scripts/check_parity_export_sample.py` 抽样通过
````

## CI

```bash
python scripts/check_tutorial_verify_blocks.py
# 缺省时补默认 stub：
python scripts/check_tutorial_verify_blocks.py --write-stub
```

索引页豁免：`tutorial/index.md`、`tutorial/tutorial-index-three-paths.md`。
