---
title: 模块手册总览
description: qchem_stack 模块地图枢纽：按包导航、管线阶段与深读入口。
---

# 模块手册总览

按 **`qchem_stack` 源码包** 组织：职责、调用、YAML 与验证。  
算法与后端选型请先看 [选型手册](/guide/)；按任务阅读见 [阅读路径](./reading-paths)。

---

## 1. 文献与角色

| 角色 | 说明 |
|------|------|
| 模块手册 | 包级工程契约（本目录） |
| 算法深读 | 论文 + 数学 + YAML（[quantum/algorithms](./quantum/algorithms/)） |
| 选型指南 | `/guide/*` 菜单与决策 |
| 阶段归属 | 仓库 `docs/engineering/pipeline_stage_ownership.md` |

实验配置统一：`schema_version: "2"`。

---

## 2. 理论：包依赖

```text
config ──► chem ──► quantum
              │         │
              ▼         ▼
         protocols ◄── backends
              │
              ▼
         orchestration ──► jobs / api / repro
              │
              ├── mitigation
              ├── md_bridge
              └── integrations / tensornet / contracts
```

概念管线（含 repro 收集与可选入队）：

```text
scf → pre_quantum → (repro) → variational → embedding_workflow
    → excited → protocol_finalize → [job_enqueue?]
```

---

## 3. 实现：枢纽用法

1. 用 [reading-paths](./reading-paths) 选 P1–P5。  
2. 改配置读 [config](./config)；跑通读 [orchestration](./orchestration)。  
3. 算法细节进 [quantum 枢纽](./quantum/) → [algorithms](./quantum/algorithms/)。  
4. 平台面：[jobs](./jobs) → [api-sdk](./api-sdk) → [repro](./repro) → [ops-light](./ops-light)。

SDK：

```python
from qchem_stack.sdk import run_pipeline_from_config, load_experiment_config
```

Worker：

```bash
python3 -m qchem_stack.jobs.worker --db jobs.sqlite
```

---

## 4. YAML / 契约速记

| 事实 | 值 |
|------|-----|
| 实验 schema | `"2"` |
| GQE | 顶层 `gqe:`，不是 `quantum.algorithm` |
| 缓解 runtime | `qermit_runtime` 为 **TOY/STUB** |
| Schema SoT | `contracts.schema_ids` |

---

## 5. Python 一键

```python
from qchem_stack.sdk import run_pipeline_from_config

out = run_pipeline_from_config("configs/example_h2.yaml")
print("repro" in out, sorted(out.keys())[:6])
```

---

## 6. 验证

```bash
python3 -c "from qchem_stack.sdk import load_experiment_config, run_pipeline_from_config; c=load_experiment_config('configs/example_h2.yaml'); assert c.schema_version=='2'; o=run_pipeline_from_config('configs/example_h2.yaml'); print('hub_ok', 'repro' in o)"
```

期望：`hub_ok True`。

---

## 7. 模块索引（调优入口）

| 模块 | 包 | 侧重 |
|------|-----|------|
| [config](./config) | `config` | YAML 契约、迁移、`resolve_pre_quantum_path` |
| [chem](./chem/) | `chem` | 平均场、映射、嵌入、哈密顿量 |
| [quantum](./quantum/) | `quantum` | VQE / ansatz / ADAPT / 激发态；**[算法深读](./quantum/algorithms/)** |
| [backends](./backends) | `backends` | 执行器与采样 |
| [protocols](./protocols) | `protocols` | 五阶段 Pauli + product_contract |
| [orchestration](./orchestration) | `orchestration` | `run_pipeline_*` |
| [mitigation](./mitigation) | `mitigation` | ZNE / PMSV / shadows（runtime TOY） |
| [md-bridge](./md-bridge) | `md_bridge` | QMEF / MD-ML |
| [jobs](./jobs) | `jobs` | SqliteJobStore + worker |
| [repro](./repro) | `repro` | 严格 JSON |
| [api-sdk](./api-sdk) | `api` + `sdk` | HTTP + facade |
| [integrations](./integrations) | `integrations` | GQE / TKET / Nexus / L3 |
| [contracts](./contracts) | `contracts` | schema ids SoT |
| [tensornet](./tensornet) | `tensornet` | dense + cutensornet stub |
| [reading-paths](./reading-paths) | — | P1–P5 学习路径 |
| [ops-light](./ops-light) | — | Day-2 冒烟与 worker |

每章结构：文献/角色 → 理论 → 实现 → YAML → Python → 验证 → 调优 → 相关。

---

## 8. 相关

- [按任务阅读](./reading-paths) · [Day-2 运维](./ops-light) · [quantum 枢纽](./quantum/)  
- [开始使用](/getting-started) · [配置目录](/reference/configs-catalog) · [Python SDK](/reference/python-sdk)
