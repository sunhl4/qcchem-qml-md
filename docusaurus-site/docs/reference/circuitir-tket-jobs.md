# CircuitIR、TKET 桥接与作业契约

本文覆盖三块工程接口：中间表示、可选 TKET 统计、异步作业句柄。

## 适用场景

- 你要理解“线路如何在系统中被表示和传递”
- 你要比较自研资源行和 TKET 统计结果
- 你要在异步模式下保证作业可追溯

## CircuitIR 角色

- 统一表达量子线路结构
- 作为资源估计与编译桥接输入
- 作为审计层的可读中间产物

## TKET 桥接（可选）

- 安装 pytket 后可导出 `pytket_depth` 等指标
- 桥接统计与自研深度可能存在差异，需在报告中注明来源

## 作业字段与追踪

- `job_id`：异步任务主键
- `protocol_hash`：可选负载指纹，用于审计与复现映射
- `trace_id`：跨 API、worker、日志的统一追踪键

## 作业契约

- 提交后返回 `job_id`
- 可选保留 `protocol_hash` 作为负载指纹
- 通过 status/summary/repro 接口分层读取结果

## 验证清单

- 运行结果可追溯到具体 `job_id`
- 报告中明确资源指标来源（自研/TKET）
- 异步轮询与最终 `repro` 的任务标识一致

## 推荐实践

- 在 Methods 或报告里同时给出“自研资源行 + TKET 指标”
- 异步场景统一追踪 `job_id + trace_id`

## 关联页面

- [HTTP API 与作业队列](/reference/http-api-sqlite-jobs)
- [P3 执行与分析](/guide/execution-and-analysis)
