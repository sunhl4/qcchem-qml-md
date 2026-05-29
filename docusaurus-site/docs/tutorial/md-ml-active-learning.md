---
title: MD/ML 主动学习闭环
description: QMEF 数据集、QML-FF 与 JAX-MD 在线学习桥接。
---

# MD/ML 主动学习闭环

**权威文档**：仓库 [`docs/qmlff_md_integration_说明.md`](https://github.com/yaozheng/qchem-stack/blob/main/docs/qmlff_md_integration_说明.md)。

## 依赖

```bash
export QCHEM_REPO=/path/to/qchem_qml_md
export QMLFF_ROOT=/path/to/QML-FF
cd "$QCHEM_REPO" && pip install -e ".[dev]"
pip install -e "$QMLFF_ROOT"
pip install -e ".[qmlff]"   # jax-md
```

## 最小 loop

```python
from pathlib import Path
from qchem_stack.md_bridge import MdValidationLoopConfig, run_md_validation_loop

summary = run_md_validation_loop(
    "configs/example_h2_uqc_mock_md_ml.yaml",
    config=MdValidationLoopConfig.from_yaml("configs/example_h2_uqc_mock_qmlff_loop.yaml"),
    output_dir=Path("results/md_validation_test"),
)
```

## 相关配置

- [`configs/README.md`](https://github.com/yaozheng/qchem-stack/blob/main/configs/README.md) — MD/ML 与 UQC 示例索引
- [`docs/说明_md_ml_export配置.md`](https://github.com/yaozheng/qchem-stack/blob/main/docs/说明_md_ml_export配置.md)
