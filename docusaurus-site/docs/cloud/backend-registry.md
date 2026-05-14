# 后端注册表

后端注册表用于统一管理执行后端能力，避免“配置里写得过、运行时跑不过”。

## 目标

- 明确每个后端的能力边界
- 让 pipeline 在提交前就能做能力检查
- 让运行结果能追溯到具体后端版本

## 建议元数据字段

| 字段 | 说明 |
|---|---|
| `backend_id` | 后端唯一标识 |
| `provider` | 提供方（如 statevector / qiskit / custom） |
| `version` | 后端版本（用于可追溯） |
| `capabilities` | 能力标签（shots、noise、并发等） |
| `gateset` | 门集摘要（可选） |

## 管理建议

1. 把后端元数据与实验配置解耦  
2. 每次运行结果落地 `backend_id + version`  
3. 提交前做能力探针，避免运行时才失败  
4. 新后端接入时同时补文档与 smoke 用例

## 相关

- [执行与分析](../guide/execution-and-analysis)
- [作业与日志](./jobs-and-logs)
