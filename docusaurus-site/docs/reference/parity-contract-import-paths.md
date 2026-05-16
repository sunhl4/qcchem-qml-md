---
title: Parity 契约与 workflow-preview（稳定 import）
description: protocols/inquanto_contract 与 integrations/inquanto_workflow_preview 的 Python import、re-export 与字面量实现路径；与仓库根 CONTRIBUTING.md 同源。
---

# Parity 契约与 workflow-preview（稳定 import）

面向**维护者与集成方**：新增 `parity_snapshot` / `run_summary` / `repro` 顶层键、修改 `inquanto_gap_categories()`、或改动 `workflow-preview` / `computable_graph_v2` 时，应知道**从哪里 import**、**改哪个文件的字面量**。

本节与仓库根目录 **`CONTRIBUTING.md`**（章节 **Parity and workflow-preview (stable imports)**）**同源**；请以本地克隆内的文件为准。

## 规则（一句话）

**`protocols/`、`integrations/` 里是稳定 re-export；frozenset、gap 表、对象映射等字面量请在 `internal_reports/competitor/` 下编辑**（除非你刻意只做 façade  shim）。

## 映射表

| 稳定 Python import | `src/` re-export 文件 | 字面量实现（编辑注册表时改这里） |
|--------------------|-----------------------|----------------------------------|
| `qchem_stack.protocols.inquanto_contract` | `src/qchem_stack/protocols/inquanto_contract.py` | `src/qchem_stack/internal_reports/competitor/inquanto_contract.py` |
| `qchem_stack.integrations.inquanto_workflow_preview` | `src/qchem_stack/integrations/inquanto_workflow_preview.py` | `src/qchem_stack/internal_reports/competitor/inquanto_workflow_preview.py` |

### 适配层（产品 HTTP / pipeline）

`POST /v1/meta/workflow-preview` 等与预览相关的组装还可经 **`src/qchem_stack/integrations/workflow_preview.py`** 暴露（内部仍引用 competitor 模块）。

## 快速自检（本地）

在**仓库根**、已 `pip install -e ".[dev]"`（或等价环境）前提下：

```bash
./scripts/venv-run python -c "from qchem_stack.protocols.inquanto_contract import PARITY_SNAPSHOT_DOCUMENTED_KEYS; print(len(PARITY_SNAPSHOT_DOCUMENTED_KEYS))"
./scripts/venv-run python -c "from qchem_stack.integrations.inquanto_workflow_preview import computable_graph_v2; print('callable', callable(computable_graph_v2))"
```

若没有 `./scripts/venv-run`，可将 `./scripts/venv-run` 换成你的解释器路径，保证能 `import qchem_stack`。

## 关联阅读

- [DMET 与 parity_snapshot](/reference/dmet-parity-snapshot)：嵌入场景下快照键语义  
- [命令行与脚本](/reference/cli-and-scripts)：`export_parity_criteria_table`、`check_parity_export_sample`  
- [工程架构](/concept/engineering-architecture)：分层与契约边界  

母稿深度学习路线（仓库内 Markdown）：**`docs/学习路线图_框架理论到源码阅读顺序.md`**。
