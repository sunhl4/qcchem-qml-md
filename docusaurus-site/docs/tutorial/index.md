---
sidebar_position: 1
title: 教程
description: 工程上手与科学目标路径；含配置↔教程矩阵入口。
---

# 教程

工程上手与科学目标路径的统一入口。配置是否有对应教程见 [配置↔教程矩阵](/reference/tutorial-config-matrix)。

---

## 工程上手

| 路径 | 入口 | 命令 / 脚本 |
|------|------|-------------|
| **Quickstart** | [快速上手](./quickstart) | `qchem-run --scenario minimal_vqe` · `scripts/smoke_pipeline.py` |
| **Async HTTP** | [HTTP 异步运行](./async-run-via-http) | `pip install -e ".[api]"` · uvicorn |
| **Parity / repro** | [读取 repro 键](./read-repro-keys) | `export_parity_table` · `check_parity_export_sample.py` |

延伸：[切换后端](./switch-backend-compare) · [分解插件](./decomposition-plugin-minimal)。

---

## 科学目标路径

### 1. VQE 与变分

| 步骤 | 入口 |
|------|------|
| 15 分钟最小管线 | [快速上手](./quickstart) |
| H₂ 配置族 | [案例：H2 家族](./case-study-h2-family) |
| UCCSD / Trotter | [UCCSD Trotter](./uccsd-trotter-export) |
| ADAPT | [ADAPT pool 烟测](./adapt-pool-smoke) |
| GQE | [GQE 变体](./gqe-variants) · [Nakaji H₂](./gqe-nakaji-h2) |
| QPE | [QPE track](./qpe-track) |

```bash
python3 scripts/smoke_pipeline.py
```

### 2. HTTP 异步

| 步骤 | 入口 |
|------|------|
| 提交 / 轮询 | [HTTP 异步](./async-run-via-http) |
| 契约 | [P4 作业](/guide/jobs-and-reproducibility) · [HTTP API](/reference/http-api-sqlite-jobs) |

### 3. 嵌入 / 活性空间

| 步骤 | 入口 |
|------|------|
| Projection | [Projection 深入](./projection-embedding-deep-dive) |
| DMET | [DMET 自洽](./dmet-self-consistent) |
| ONIOM | [ONIOM 烟测](./oniom-smoke) |
| CASSCF / AVAS | [CASSCF audit](./casscf-audit-workflow) |
| 选型 | [P1 化学与嵌入](/guide/chemistry-and-embedding) |

```bash
python3 scripts/smoke_pipeline.py --projection-trace
```

### 其它

- [ZNE](./zne-qiskit-repro) · [MD/ML](./md-ml-active-learning) · [workflow](./workflow) · [verify 模板](./verify-block-template)

---

**维护**：新增教程时更新本页与矩阵脚本。边界见 [未承诺项](/product/non-goals) · [能力 SLA](/product/capability-sla)。
