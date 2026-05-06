# 后端注册表

后端注册表用于统一管理模拟器、Qiskit 后端和未来扩展执行环境。

## 建议 schema

| 字段 | 说明 |
|------|------|
| `backend_id` | 后端唯一 ID |
| `provider` | 提供方（statevector/qiskit/custom） |
| `version` | 后端版本 |
| `capabilities` | 支持能力（shots、噪声、并发等） |
| `gateset` | 门集摘要 |

## 管理建议

- 把运行时配置与后端元数据分离
- 记录每次运行使用的 backend version
- 支持后端能力探针，避免运行时失败

## 相关

- [执行与分析](../guide/execution-and-analysis)
- [作业与日志](./jobs-and-logs)
