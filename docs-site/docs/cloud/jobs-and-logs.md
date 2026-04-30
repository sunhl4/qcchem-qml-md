# 作业与日志

**状态**：占位骨架（Wave W0）。**目标**：把 **`GET/POST /v1/runs`**、异步 `launch`/`retrieve` 类比、**审计日志保留策略** 与 **PII** 边界写清 — 对齐节点 backlog 中 P4 与 `trace/request id` 检查项。

## 可观测

- 每个 run：`request_id` / `trace_id` 贯穿 API → worker → 导出 `repro`。
- 日志保留周期与脱敏规则在 **合规** 小节与 `/reference/` HTTP 契约交叉引用。

## 相关实现文档

- [HTTP API · SQLite 作业](/reference/http-api-sqlite-jobs)
- [CircuitIR · TKET · 作业契约](/reference/circuitir-tket-jobs)
