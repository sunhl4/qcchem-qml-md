---
title: Python SDK facade
description: 稳定集成面 qchem_stack.sdk：管线、parity、repro、场景。
---

# Python SDK facade

库调用方优先使用薄稳定面 `qchem_stack.sdk`。更完整的模块级说明见 [API 面](./api-surface)。

```python
from qchem_stack.sdk import (
    ExperimentConfig,
    SCENARIOS,
    export_parity_table,
    load_experiment_config,
    run_pipeline_from_config,
    run_pipeline_sync,
    repro_dict_for_strict_json,
    repro_json_dumps,
    workflow_preview_payload,
    list_scenarios_text,
)

out = run_pipeline_from_config("configs/example_h2.yaml")
print(repro_json_dumps(out["repro"]))

table = export_parity_table("configs/example_h2.yaml")
print(table.get("experiment_id"))

preview = workflow_preview_payload(load_experiment_config("configs/example_h2.yaml"))
print(preview.get("schema"))
```

场景选择（上手）：

```python
print(list_scenarios_text())
print(len(SCENARIOS))
strict = repro_dict_for_strict_json(out["repro"])
```

CLI：`qchem-run --list-scenarios`、`qchem-run`、`qchem-export-parity`（见 [CLI](./cli-and-scripts)）。

稳定性策略：[`api_stability_policy.md`](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/engineering/api_stability_policy.md)。

CI 用 `scripts/check_sdk_docs_sync.py` 保证本文出现的符号名与 `sdk.__all__` 同步。签名摘要见生成页 **[SDK API（生成）](./api-generated)**。完整 Sphinx autodoc 尚未默认发布；以本页 + [API 面](./api-surface) + 模块手册为准。
