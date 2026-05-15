# 模拟器云（契约骨架）

自建多租户模拟器云的**契约叙事**：租户、后端注册、作业与日志。**不**复制 Nexus 控制台或厂商 OAuth。

- **不对齐**：`qnexus`、商业 OAuth、真机配额 — 见 [契约矩阵](/product/roadmap) `n/a` / `not-applicable`。
- **对齐的工程面**：SQLite + FastAPI 作业、`workspace_label`、可观测请求 ID — 见子页与 [HTTP API](/reference/http-api-sqlite-jobs)。

## 子页

- [租户与配额](./tenant-and-quotas)
- [后端注册表](./backend-registry)
- [作业与日志](./jobs-and-logs)

## 相关

- [HTTP API · SQLite 作业](/reference/http-api-sqlite-jobs)
- [P4 作业与可复现](/guide/jobs-and-reproducibility/)
- [公开契约矩阵](/product/roadmap)
