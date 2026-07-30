---
title: 可复现性与 parity 契约
description: repro 字段、parity 导出、capability-surface 与用户侧验收方式。
---

# 可复现性与 parity 契约

:::tip 模块手册
[repro](/modules/repro) · [contracts](/modules/contracts) · [jobs](/modules/jobs) · [P4 作业](./jobs-and-reproducibility)
:::

开放栈的核心交付不是「对上某闭源截图」，而是 **可复现的结构化产物**：`repro`、parity 表、capability-surface。

## 三类产物

| 产物 | 产生方式 | 用途 |
|------|----------|------|
| **Pipeline `repro`** | `run_pipeline_sync` / HTTP `/repro` | 单次运行上下文、profile、run_summary |
| **Parity criteria table** | `export_parity_table` / `scripts/export_parity_criteria_table.py` | Methods 风格字段包（config-only 或带结果） |
| **Capability surface** | `GET /v1/meta/capability-surface` | 能力矩阵 + gaps（`capability_surface_v2`） |

SDK：

```python
from qchem_stack.sdk import (
    run_pipeline_from_config,
    export_parity_table,
    repro_json_dumps,
    workflow_preview_payload,
    load_experiment_config,
)

out = run_pipeline_from_config("configs/example_h2.yaml")
print(repro_json_dumps(out["repro"]))
print(export_parity_table("configs/example_h2.yaml").get("experiment_id"))
print(workflow_preview_payload(load_experiment_config("configs/example_h2.yaml")).get("schema"))
```

## `repro` 中常查键

| 键 / 路径 | 含义 |
|-----------|------|
| `run_context` | trace / client_request_id |
| `pipeline_profile` | 分阶段耗时（可选内存） |
| `run_summary` | 算法、阶段完成列表、池 ID 等 |
| `parity_snapshot`（若启用） | 与导出对齐的快照 |

字段速览教程：[读 repro 关键键](../tutorial/read-repro-keys)。契约导入路径：[parity contract import paths](../reference/parity-contract-import-paths)。

## 验收命令

```bash
python scripts/check_parity_export_sample.py
python scripts/smoke_pipeline.py
curl -s http://127.0.0.1:8000/v1/meta/capability-surface | head -c 400
```

## 边界

- 公共 parity 矩阵见仓库 [`docs/public_parity_matrix.md`](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/public_parity_matrix.md)；站点摘要：[parity gaps](../parity/gaps)。
- 不宣称与 InQuanto / Tangelo 二进制等价；对标的是 **公开契约面与可执行配置**。

## 相关

- [P4 作业与可复现](./jobs-and-reproducibility)
- [资源估计与 Methods 导出](./resource-estimation-methods)
- [Python SDK](../reference/python-sdk)
