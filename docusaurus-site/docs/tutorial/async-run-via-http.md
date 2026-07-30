# HTTP 异步运行教程

本教程演示如何通过 HTTP 提交异步任务，并在任务完成后获取 `summary` 与 `repro`。

## 目标

- 提交一个异步 run
- 轮询状态直到结束
- 拉取结果摘要和可复现对象

## 前置条件

1. 在仓库根目录安装 API 依赖：`pip install -e ".[api]"`
2. 本地有可用配置文件（例如 `configs/example_h2.yaml`）

## 步骤 1：启动服务

```bash
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

另开一个终端执行后续命令。

## 步骤 2：提交异步任务

`POST /v1/runs` 需要的是完整 `experiment_yaml` 文本。下面示例直接把文件内容注入请求体：

```bash
curl -sS -X POST "http://127.0.0.1:8000/v1/runs" \
  -H "Content-Type: application/json" \
  -H "X-Trace-ID: demo-async-001" \
  -d "$(python - <<'PY'
import json
from pathlib import Path
payload = {"experiment_yaml": Path("configs/example_h2.yaml").read_text(), "sync": False}
print(json.dumps(payload))
PY
)"
```

返回里记录 `job_id`，下文用 `$RUN_ID` 表示。

## 步骤 3：轮询任务状态

```bash
curl -sS "http://127.0.0.1:8000/v1/runs/$RUN_ID/status"
```

建议每 1-2 秒轮询一次，直到状态进入终态（如 `DONE` / `FAILED`）。

## 步骤 4：读取摘要与复现对象

```bash
curl -sS "http://127.0.0.1:8000/v1/runs/$RUN_ID/summary"
curl -sS "http://127.0.0.1:8000/v1/runs/$RUN_ID/repro"
```

## 验证清单

- `status` 能从排队/运行推进到终态
- `summary` 可读，包含关键结果摘要
- `repro` 可读，包含 `run_context`、`pipeline_profile`、`run_summary`

## 常见问题

- **404**：`RUN_ID` 不存在或拼写错误
- **409**：任务未完成就请求 `repro`
- **422**：`experiment_yaml` 不合法或配置无法通过校验

## 下一步

- [repro 关键字段速览](./read-repro-keys)
- [命令行与脚本](../reference/cli-and-scripts)
- [HTTP API 与作业队列](../reference/http-api-sqlite-jobs)

## 验证命令

```bash
curl -sS "http://127.0.0.1:8000/v1/meta/product-surface" | head -c 200
```

## 期望输出

- API 返回 JSON（需先 `uvicorn qchem_stack.api.app:app`）
- 异步 run 终态为 `DONE` / `FAILED`
- `/repro` 含 `run_summary`
