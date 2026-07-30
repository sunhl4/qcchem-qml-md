---
title: OpenAPI
description: FastAPI OpenAPI 快照、Swagger UI 与契约版本。
---

# OpenAPI

安装 API extra 后本地启动：

```bash
pip install "qchem-stack[api]"
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

| 入口 | URL |
|------|-----|
| Swagger UI | `http://127.0.0.1:8000/docs` |
| ReDoc | `http://127.0.0.1:8000/redoc` |
| OpenAPI JSON | `http://127.0.0.1:8000/openapi.json` |

自 **1.0.0** 起，`/v1/*` JSON 响应含 `api_contract_version: "1.0"`。

## CI 快照

仓库检入 `docs/generated/openapi_snapshot.json`：

```bash
python3 scripts/generate_openapi_snapshot.py
```

站内路由表与请求示例见 [HTTP API 与作业](./http-api-sqlite-jobs)。生产环境变量见同页「鉴权、CORS 与限流」。

完整工程长文（仓库）：[`docs/技术文档_HTTP_API与SQLite作业队列及可观测性契约.md`](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/技术文档_HTTP_API与SQLite作业队列及可观测性契约.md)。

English：[`docs/QUICKSTART_HTTP_API_en.md`](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/QUICKSTART_HTTP_API_en.md)。
