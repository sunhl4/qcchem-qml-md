# Jobs / HTTP API 错误映射复核（D49）

**契约母稿**：[`技术文档_HTTP_API与SQLite作业队列及可观测性契约.md`](技术文档_HTTP_API与SQLite作业队列及可观测性契约.md)。

| 来源 | HTTP | 说明 |
|------|------|------|
| `yaml.YAMLError` / 非 mapping | 400 | `experiment_yaml` 解析失败 |
| `ExperimentConfig` `ValidationError` | 422 | 字段校验失败 |
| 未知 `job_id` / SQLite 无行 | 404 | `GET /v1/runs/{id}` 族 |
| SQLite 路径不可用 | 503 | `GET /health/ready`（就绪探针） |

**网关建议**：将 `qchem_stack.exceptions` 中类型映射到结构化 JSON（见 `ENGINEERING_ARCHITECTURE.md` §3），避免前端字符串匹配 traceback。
