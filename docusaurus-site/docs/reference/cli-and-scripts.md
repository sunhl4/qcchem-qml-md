---
title: 命令行与脚本
description: 安装后可用的控制台命令与仓库 scripts/ 常用入口。
---

# 命令行与脚本

本文聚焦日常高频命令。参数细节以仓库 `README.md`、`pyproject.toml` 与脚本 docstring 为准。

## 适用场景

- 本地跑 smoke、回归和导出
- 启 worker 处理异步作业
- 生成验收所需材料

## 安装

在仓库根目录执行：

```bash
pip install -e ".[dev]"
```

可选：`pip install -e ".[all]"`、`pip install -e ".[api]"`。

## 包入口命令

| 命令 | 作用 |
|------|------|
| `qchem-jobs-worker` | 轮询 SQLite 作业库，消费 `QUEUED` 作业 |
| `qchem-pipeline-worker` | 与 `qchem-jobs-worker` 等价入口 |

典型用法：

```bash
qchem-jobs-worker --db ./jobs.sqlite --sleep 0.5
```

常见参数：`--db`、`--sleep`、`--max-retries`。

## 本地 HTTP 服务

```bash
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

契约说明见 [HTTP API 与作业队列](/reference/http-api-sqlite-jobs)。

## 仓库脚本（`scripts/`）

| 脚本 | 说明 |
|------|------|
| `python scripts/smoke_pipeline.py` | 本地/CI 烟测入口 |
| `python scripts/export_parity_criteria_table.py <config.yaml>` | 导出 parity 判据表 |
| `python scripts/check_parity_export_sample.py` | 校验导出样例 |
| `python scripts/check_solver_adapter_contract.py [config.yaml]` | 检查 solver 适配合同 |
| `python scripts/create_solver_adapter_scaffold.py <backend_id>` | 生成新后端适配骨架 |
| `python scripts/demo_mock_external_backend.py` | 运行 mock 外部后端演示 |
| `python scripts/run_qpe_track_demo.py` | QPE 演示轨 |
| `python scripts/resource_estimation_demo.py` | 资源估计演示 |

## Solver 注册表（`scf.driver`）

- **内置**：`pyscf`、`psi4` 在首次访问 solver registry 时注册。
- **外部插件**：`pyproject.toml` 中 `[project.entry-points."qchem_stack.chem_solvers"]`；说明见仓库 `docs/solver_entrypoint_plugin_安装与发布指南.md`，示例 `examples/solver_plugin_entrypoint_demo/`。
- **排障**：`registered_solvers_detail()`、`set_entrypoint_conflict_policy("warn"|"strict")`。完整步骤见站内 [后端适配快速接入](/guide/backend-adapter-quickstart)（与 VitePress 母稿 `docs-site/docs/guide/chemistry-and-embedding/backend-adapter-quickstart.md` 对齐）。

## 推荐执行顺序（维护者）

1. `smoke_pipeline.py` 保证基本可运行  
2. `check_parity_export_sample.py` 保证导出样例稳定  
3. `export_parity_criteria_table.py` 产出对齐材料  

## 常见问题

- **命令找不到**：确认已在激活环境内安装 `-e`
- **worker 没消费**：检查 `--db` 路径和 API 提交使用的数据库是否一致
- **导出失败**：先确认对应配置能单独跑通

## 另见

- [快速上手](/tutorial/quickstart)
- [后端适配快速接入](/guide/backend-adapter-quickstart)
- [P4 作业与可复现](/guide/jobs-and-reproducibility)
- [HTTP API 与作业队列](/reference/http-api-sqlite-jobs)
