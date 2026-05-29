---
sidebar_position: 1
title: 教程索引
description: 三条上手路径 — VQE 管线、HTTP 异步作业、DMET / projection 嵌入。
---

# 教程索引：三条上手路径

根据你的目标选择一条路径；每条路径都链接到可运行教程、代表 YAML 与（可选）Jupyter notebook。

## 路径 1：VQE 与变分算法

适合：先跑通 H₂ 端到端，再扩展到 UCCSD / ADAPT / IQEB。

| 步骤 | 入口 |
|------|------|
| 15 分钟最小管线 | [快速上手](./quickstart) — `configs/example_h2.yaml` |
| H₂ 配置族与算法对照 | [案例：H2 家族](./case-study-h2-family) |
| UCCSD / Trotter 导出 | [UCCSD Trotter 导出](./uccsd-trotter-export) |
| Notebook  walkthrough | 仓库 `notebooks/h2_vqe_walkthrough.ipynb`、`uccsd_walkthrough.ipynb`、`adapt_walkthrough.ipynb` |

**验证命令**：

```bash
python scripts/smoke_pipeline.py
python scripts/smoke_pipeline.py --iqeb
```

## 路径 2：HTTP 异步工作流

适合：需要作业队列、轮询状态与 `repro` 摘要的工程集成。

| 步骤 | 入口 |
|------|------|
| 提交 / 轮询 / 取结果 | [通过 HTTP 异步运行](./async-run-via-http) |
| 作业与可复现契约 | [P4 作业与可复现](../guide/jobs-and-reproducibility) |
| HTTP API 参考 | [HTTP API 与 SQLite 作业](../reference/http-api-sqlite-jobs) |

**验证命令**：

```bash
pip install -e ".[api]"
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

## 路径 3：DMET / projection 嵌入

适合：活性空间、片段嵌入与 pre-quantum handoff 的维护者与研究者。

| 步骤 | 入口 |
|------|------|
| Projection 配置语义 | [Projection 嵌入深入](./projection-embedding-deep-dive) — `configs/example_h2_projection_trace.yaml` |
| DMET parity 快照 | [DMET parity 快照](../reference/dmet-parity-snapshot) |
| 化学与嵌入主线 | [P1 化学与嵌入](../guide/chemistry-and-embedding) |
| Notebook walkthrough | 仓库 `notebooks/dmet_projection_walkthrough.ipynb` |

**验证命令**：

```bash
python scripts/smoke_pipeline.py --projection-trace
```

---

**维护**：新增 `configs/*.yaml` 或教程页时，同步检查本页三条路径的链接与代表配置是否仍准确。产品边界见 [未承诺项](../product/non-goals)。
