---
title: Python SDK facade
description: Stable re-exports for integrators (`qchem_stack.sdk`).
---

# Python SDK facade

For library callers, prefer the thin stable surface:

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

Scenario picker (onboarding):

```python
print(list_scenarios_text())
print(len(SCENARIOS))
strict = repro_dict_for_strict_json(out["repro"])
```

CLI equivalents: `qchem-run --list-scenarios`, `qchem-run`, `qchem-export-parity` (see [CLI and scripts](./cli-and-scripts.md)).

Policy: [`api_stability_policy.md`](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/engineering/api_stability_policy.md).
