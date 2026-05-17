---
title: Product contracts 与 workflow-preview（稳定 import）
description: qchem_stack.protocols.product_contract 与 qchem_stack.integrations.workflow_preview — 能力与 gaps、导出常量、YAML-only 预览；与仓库根 CONTRIBUTING.md「Product contracts」节同源。
---

# Product contracts 与 workflow-preview（稳定 import）

面向**维护者与控制台集成方**：调整 capability gaps、parity 风格导出稳定键、或 workflow / computable 预览时，应知道从哪里 import、改哪个文件的字面量。

本节与仓库根目录 **[CONTRIBUTING.md](https://github.com/sunhl4/qcchem-qml-md/blob/main/CONTRIBUTING.md)**（章节 **Product contracts and workflow-preview**）**对齐**。

## 规则（一句话）

**产品机读常量**写在 **`qchem_stack.protocols.product_contract`**。**Workflow / DAG 预览**写在 **`qchem_stack.integrations.workflow_preview`**。

## Python 关注点

| 话题 | Module / symbol | 备注 |
|------|-----------------|------|
| Gap 行 + anchors | `product_gap_categories()`, `product_gap_anchor_index_v1()`, `validate_product_gap_categories()` | `GET /v1/meta/parity-gaps`、`GET /v1/meta/capability-surface` |
| Capability 名称 → 模块 | `PRODUCT_CAPABILITY_MAP` / `product_capability_map_for_docs()` | `capability_surface_v2.capability_map` |
| Export 常量 | `PARITY_EXPORT_V3_STABLE_KEYS` | `scripts/check_parity_export_sample.py`、`tests/test_export_parity_golden.py` |
| 预览载荷 | `workflow_preview_payload`, `computable_graph_v2`, `protocol_stages_preview_v1`, `slim_product_summary_from_pipeline_result` | FastAPI **`POST /v1/meta/workflow-preview`**、`GET /v1/runs/{id}/summary` |

## 自检（本地）

在**仓库根**、已 `pip install -e ".[dev]"`（或等价环境）前提下：

```bash
./scripts/venv-run python -c "from qchem_stack.protocols.product_contract import product_gap_categories, PARITY_EXPORT_V3_STABLE_KEYS; print(len(product_gap_categories()), len(PARITY_EXPORT_V3_STABLE_KEYS))"
./scripts/venv-run python -c "from qchem_stack.integrations.workflow_preview import computable_graph_v2; print(callable(computable_graph_v2))"
```

## Pre-quantum YAML 组合矩阵

允许/禁止的 `scf.driver` × `embedding.mode` × 活性空间策略组合见仓库根目录 **`docs/pre_quantum_yaml_matrix.md`**（与 `config/_experiment_validation.py` 同源）。

Config-only parity 导出稳定键包含 **`pre_quantum_semantics_from_config`**（`PARITY_EXPORT_V3_STABLE_KEYS`）：无需跑 pipeline 即可在 Methods/parity 表中声明 `hamiltonian_branch` 与 `post_variational_embedding_audit_only`。离线样例：`configs/example_h2_precomputed_bundle.yaml`。

## 关联阅读

- [DMET 与 parity_snapshot](../reference/dmet-parity-snapshot)（语义表；快照键列表以源码与导出脚本为准）  
- [命令行与脚本](../reference/cli-and-scripts)：export / check parity sample  
- [工程架构](../concept/engineering-architecture)：分层与边界  

母稿：**`docs/学习路线图_框架理论到源码阅读顺序.md`**（仓库）
