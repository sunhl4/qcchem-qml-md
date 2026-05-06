# repro 关键字段速览

`repro` 是可复现和审计核心结构，建议在自动化链路中长期保留。

## 常看字段

- `run_context`：trace/request 追踪信息
- `pipeline_profile`：阶段耗时
- `parity_snapshot`：对标与契约快照
- `run_summary`：关键结果摘要

## 使用建议

- 上游只读 `summary`，下游归档 `repro`
- 对关键字段做 schema 版本校验
- 对大型对象拆分保存，避免一次性超大记录
