---
title: P4 作业与可复现
description: SQLite 作业、HTTP 异步、repro / parity 契约与运维决策指南。
---

# P4 作业与可复现

:::tip 模块手册
[jobs](/modules/jobs) · [repro](/modules/repro) · [api-sdk](/modules/api-sdk) · [HTTP API](/reference/http-api-sqlite-jobs)
:::

P4 把单次计算变成 **可追踪、可回放、可审计** 的工程运行：作业队列、HTTP、worker、结构化 `repro`。

## 决策总表

| 决策 | 选项 | 默认建议 | 何时不要 |
|------|------|----------|----------|
| 运行方式 | 进程内 sync / 异步 job | 调试可用 sync；服务化用 async | 在 CI 里依赖未启动的 worker |
| 存储 | SQLite 本地 DB | 开源默认 | 当作多区域商业多租户存储 |
| 验收 | parity / repro 导出 | 发版前跑抽样脚本 | 只看能量数字不看 fingerprint |
| SDK vs HTTP | Python SDK / REST | 脚本用 SDK；跨语言用 HTTP | 混用两套 ID 而不记录 `job_id` |

## 典型流程

1. `POST /v1/runs`（`sync: false`）→ 获得 `job_id`
2. `qchem-jobs-worker --db …` 消费队列（或进程内 process）
3. `GET …/status` 直到终态
4. `GET …/summary` 与 `GET …/repro`

同步调试：`sync: true`（API 已标 Deprecation，优先异步）。CLI：`qchem-run`、`qchem-jobs-worker`。

## 何时不要用（边界）

- 不要把「云文档里的租户配额」当成当前开源实现已强制执行（见 [cloud/overview](../cloud/overview) 警告）。
- 不要在无 `trace_id` / `job_id` 的情况下排查「偶发失败」。
- 不要修改已归档 run 的 YAML 却声称同一 `repro` 可复现。
- 不要跳过 `check_parity_export_sample.py` 直接宣称 Methods 表对齐。

## 本柱子页与参考

| 主题 | 页面 |
|------|------|
| Parity / repro 契约 | [parity-repro-contract](./parity-repro-contract) |
| HTTP API | [http-api-sqlite-jobs](../reference/http-api-sqlite-jobs) |
| CLI | [cli-and-scripts](../reference/cli-and-scripts) |
| Python SDK | [python-sdk](../reference/python-sdk) · [api-sdk 模块](/modules/api-sdk) |
| 教程：异步 HTTP | [async-run-via-http](../tutorial/async-run-via-http) |
| 读 repro 键 | [read-repro-keys](../tutorial/read-repro-keys) |
| 云与作业 | [cloud/overview](../cloud/overview) |

## 作业状态机（运维视角）

| 状态 | 含义 | 操作者动作 |
|------|------|------------|
| `QUEUED` | 已入队 | 确认 worker 在跑 |
| `RUNNING` | 执行中 | 看日志 / `trace_id` |
| `DONE` | 成功终态 | 拉 summary / repro |
| `FAILED` | 失败终态 | 读错误分类；决定是否重试 |

细节见 [jobs-and-logs](../cloud/jobs-and-logs)。

## repro / parity 最小集合

发版或论文 Methods 前至少确认：

- `hamiltonian_fingerprint`（或等价 pre_quantum 键）
- `pipeline_profile` / 算法与后端 YAML 回显
- 若启用：`parity_integrations.*` 对应导出块
- `run_context.trace_id` 可贯通日志

深读：[parity-repro-contract](./parity-repro-contract)。

## 源码锚点

| 关注点 | 模块 |
|--------|------|
| 作业存储 | `jobs.store`、`jobs.worker` |
| 管线入队 | `jobs.pipeline_jobs` |
| HTTP | `api.routers.runs` |
| repro 组装 | `orchestration.repro_metadata`、`repro.*` |
| SDK | `qchem_stack.sdk` |

## 代表配置与脚本

| 意图 | 入口 |
|------|------|
| 最小场景 | `configs/scenarios/minimal_vqe.yaml` · `qchem-run --scenario minimal_vqe` |
| 全量 H₂ | `configs/example_h2.yaml` |
| Parity 抽样 | `python3 scripts/check_parity_export_sample.py` |
| Pipeline 烟测 | `python3 scripts/smoke_pipeline.py` |

## 验证命令

```bash
python3 -c "
from qchem_stack.config import load_experiment_config
from qchem_stack.sdk import workflow_preview_payload
cfg = load_experiment_config('configs/example_h2.yaml')
p = workflow_preview_payload(cfg)
print(sorted(p.keys())[:8])
"
```

期望：打印 preview 顶层键片段（含 workflow / capability 相关键）。

SDK 加载：

```bash
python3 -c "
from qchem_stack.config import load_experiment_config
c = load_experiment_config('configs/example_h2.yaml')
print(c.schema_version, c.experiment_id)
"
```

期望：`2` 与非空 `experiment_id`。

## 运维建议

- 文档化 `FAILED` 分类与重试；监控队列积压。
- 发布前跑 `check_parity_export_sample.py` 与 `smoke_pipeline.py`。
- 保留 `run_context.trace_id` 贯通日志与 HTTP 头。
- 本地 FastAPI + SQLite 是开源主路径；商业 IAM / 配额见云文档警告框。

## 相关教程

- [HTTP 异步运行](../tutorial/async-run-via-http)
- [读懂 repro 关键字段](../tutorial/read-repro-keys)

## 下一步

- [parity / repro 契约](./parity-repro-contract)
- [云与运维概览](../cloud/overview)
- [部署检查清单](../release/deployment-checklist)
