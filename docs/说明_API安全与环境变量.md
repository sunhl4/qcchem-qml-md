# HTTP API 安全与环境变量

本文档说明 `qchem_stack.api` 在生产部署时可用的认证、限流、CORS 与 Protocol 序列化相关环境变量。

## 启动 API

```bash
./scripts/venv-run uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

默认绑定 `127.0.0.1`；对外暴露前请置于反向代理之后并启用下方认证。

## 环境变量一览

| 变量 | 默认值 | 作用 |
|------|--------|------|
| `QCHEM_STACK_API_KEY` | （未设置） | 设置后启用 Bearer 认证；除 `/health`、`/health/ready` 外所有路由需 `Authorization: Bearer <key>` |
| `QCHEM_STACK_DISABLE_RATE_LIMIT` | `1`（pytest conftest） | 设为 `1`/`true`/`yes` 时关闭路由 `@rate_limit`（**模块 import 时生效**） |
| `QCHEM_STACK_CORS_ORIGINS` | `http://127.0.0.1:3000,http://127.0.0.1:8000` | 逗号分隔的允许 Origin 列表 |
| `QCHEM_STACK_CORS_CREDENTIALS` | （未设置） | 设为 `1`/`true`/`yes` 且 origins **不含** `*` 时允许携带 Cookie |
| `QCHEM_PROTOCOL_HMAC_KEY` | 内置默认值 | Protocol job blob 的 HMAC 签名密钥；**生产必须覆盖** |
| `QCHEM_JOB_DB` | 系统 temp 目录下 `qchem_api_jobs.sqlite` | 默认 job SQLite 路径（`/health/ready` 探测用） |

## 认证（`QCHEM_STACK_API_KEY`）

- **未设置**：不挂载 `AuthenticationMiddleware`，本地开发可直接访问（日志会警告）。
- **已设置（生产推荐）**：请求须带 `Authorization: Bearer <QCHEM_STACK_API_KEY>`；缺少头返回 **401**，错误 token 返回 **403**。
- 回归：`tests/api/test_api_auth_middleware.py`（reload app 后验证 Bearer）。
- `/health` 与 `/health/ready` 始终匿名可访问（K8s probe）。

## 速率限制

| 路由 | 限额 |
|------|------|
| `POST /v1/runs` | 10 / 分钟 |
| `GET /v1/runs` | 60 / 分钟 |
| `GET /v1/runs/{job_id}/*` | 120 / 分钟 |
| `POST /v1/meta/*`、`POST /v1/ml-md/*` | 30 / 分钟 |

超限返回 **429**。全量 pytest 默认通过 `tests/conftest.py` 设置 `QCHEM_STACK_DISABLE_RATE_LIMIT=1`；429 行为见 `tests/api/test_api_rate_limiting.py`。

## CORS

- 默认 `allow_origins=["*"]` 且 **`allow_credentials=False`**（避免浏览器拒绝 `*` + credentials 组合）。
- 需要 Cookie 时：显式设置 `QCHEM_STACK_CORS_ORIGINS=https://app.example.com` 并 `QCHEM_STACK_CORS_CREDENTIALS=1`。

## Protocol 序列化（`QCHEM_PROTOCOL_HMAC_KEY`）

`PauliAveragingProtocol.dumps()` / job enqueue 默认使用 **HMAC 签名的 pickle**（32 字节签名 + payload）。

- 设置 `QCHEM_PROTOCOL_BLOB_V2=1` 时改为 **HMAC 签名的 JSON**（`protocol_blob_version: 2`）；读路径双兼容，见 [protocol_serialization_v2_rfc.md](engineering/protocol_serialization_v2_rfc.md)。
- 生产环境务必设置强随机 `QCHEM_PROTOCOL_HMAC_KEY`。
- HMAC 提供**完整性**校验，**不能**将 pickle 视为安全反序列化边界；密钥泄露仍可能导致 RCE。
- **向后兼容**：`secure_loads` 仍可读取升级前的无签名 legacy pickle（会发出 `DeprecationWarning`）；新写入一律带 HMAC。
- **类型门控**：`secure_loads_protocol` 仅反序列化为 `PauliAveragingProtocol`；非 allowlist 类型会触发 `TypeError`。

## 请求体大小（YAML / JSON）

`POST /v1/runs` 与相关 meta 路由在解析前限制原始 body 为 **512 KiB**；超限返回 **413 Payload Too Large**（见 `qchem_stack.api.deps`）。

## 生产检查清单

1. 设置 `QCHEM_STACK_API_KEY` 与 `QCHEM_PROTOCOL_HMAC_KEY`。
2. 确认 `QCHEM_STACK_DISABLE_RATE_LIMIT` **未**设置（或设为 `0`）。
3. 反向代理 TLS 终止；API 仅监听内网或 localhost。
4. 按需配置 `QCHEM_STACK_CORS_ORIGINS`（勿在生产使用 `*` 若需 credentials）。
