# repro 关键字段速览

`repro` 是工程可复现与审计的核心对象。  
这页帮助你快速识别最重要字段，并给出归档建议。

## 目标

- 看懂 `repro` 的高频字段
- 知道哪些字段用于在线读，哪些用于离线归档
- 建立最小校验规则

## 前置条件

- 你已经拿到一次 run 的 `repro`（可通过 [HTTP 异步教程](./async-run-via-http) 获取）

## 核心字段分组

| 字段 | 用途 | 建议 |
|---|---|---|
| `run_context` | 追踪链路信息（trace/request 等） | 在线问题定位必留 |
| `pipeline_profile` | 阶段耗时与总耗时 | 做性能回归时必留 |
| `run_summary` | 对外结果摘要 | 给上游系统优先读取 |
| `parity_snapshot` | 契约快照 | 验收与对齐场景保留 |

## 最小读取示例（Python）

```python
repro = ...  # 从 API 或文件读取的字典
print(repro.get("run_context", {}).keys())
print(repro.get("pipeline_profile", {}).keys())
print(repro.get("run_summary", {}).keys())
```

## 最小校验清单

- 是否存在 `run_context`
- 是否存在 `run_summary`
- `pipeline_profile` 是否包含阶段耗时
- 验收流程中是否包含 `parity_snapshot`

## 归档建议

1. 在线系统读取 `summary`，避免一次性拉取超大对象  
2. 离线归档保存完整 `repro`（用于复盘与审计）  
3. 大对象拆分存储，避免单条记录过大  
4. 给关键字段加 schema 版本校验，降低升级风险

## 下一步

- [切换 Backend 并对比结果](./switch-backend-compare)
- [HTTP API 与作业队列](../reference/http-api-sqlite-jobs)

## 验证命令

```bash
python scripts/check_parity_export_sample.py
```

## 期望输出

- 退出码 `0`
- 导出 JSON 含 `resource_estimation_preview_v1` 等契约键
