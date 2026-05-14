---
title: 与 InQuanto 能力差距与实施计划（站内入口）
description: 差距收敛计划与附录锚点的站内摘要；完整正文以仓库 docs 母稿为准。
keywords:
  - InQuanto
  - gap plan
  - parity
  - roadmap
---

# 与 InQuanto 能力差距与实施计划

本页是 **站内导航摘要**。完整维护稿（**附录 A–F**、**§7 L3**、**附录 D B→J**、SLA 模板等全文与 Markdown 锚点）以仓库根单一真源为准：

**→ [与 InQuanto（公开资料）能力差距与实施计划 — 完整正文](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/与InQuanto能力差距与实施计划.md)**

克隆仓库后也可在本地打开 **`docs/与InQuanto能力差距与实施计划.md`**，便于全文检索与评审。

## 与本站其它页的关系

| 页面 | 角色 |
|------|------|
| [公开契约覆盖矩阵](./public-matrix) | 能力 × 覆盖状态（`yes` / `partial` / …） |
| [对标框架](./competitor-benchmark) | 方法论与三柱映射 |
| [路线图](../product/roadmap) | 发布时间线与优先级 |

## 近期机读闸门（摘要）

- **L3（可选）**：`integrations.l3_algorithm_benchmark.L3_PYTEST_YAMLS` 为代表门禁集（当前 **7**：含基线 H2 VQE + ADAPT/IQEB/激发；`QCHEM_RUN_L3=1` + `pytest -m l3`）；论文式汇总：`scripts/l3_algorithm_benchmark_report.py`。**非**闭源 wheel 数值等价。
- **Psi4 浅路径（parity export）**：样例 `configs/example_h2_psi4_rhf_sto3g.yaml`；`registered_solvers` / `solver_capabilities_snapshot`；见统一经典接口文档（仓库 `docs/统一经典化学接口_ChemIntegralSolver与下游无关性.md`）。
- **HTTP**：`GET /v1/meta/capability-surface` 与 `protocols/inquanto_contract` 注册键同源；变更需跑 `tests/test_api_runs.py::test_capability_surface_matches_inquanto_contract`。

## 相关

- [公开契约覆盖矩阵](./public-matrix)
- [竞争定位与路线图](../concept/competitive-positioning)
- [HTTP API 与 SQLite 作业](../reference/http-api-sqlite-jobs)
