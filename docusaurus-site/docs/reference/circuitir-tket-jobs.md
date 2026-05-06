# CircuitIR、TKET 桥接与作业契约

本文覆盖三块工程接口：中间表示、可选 TKET 统计、异步作业句柄。

## CircuitIR 角色

- 统一表达量子线路结构
- 作为资源估计与编译桥接输入
- 作为审计层的可读中间产物

## TKET 桥接（可选）

- 安装 pytket 后可导出 `pytket_depth` 等指标
- 桥接统计与自研深度可能存在差异，需在报告中注明来源

## 作业契约

- 提交后返回 `job_id`
- 可选保留 `protocol_hash` 作为负载指纹
- 通过 status/summary/repro 接口分层读取结果

## 推荐实践

- 在 Methods 或报告里同时给出“自研资源行 + TKET 指标”
- 异步场景统一追踪 `job_id + trace_id`
