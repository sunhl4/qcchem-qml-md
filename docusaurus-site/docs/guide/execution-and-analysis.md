# P3 执行与分析（Execution and analysis）

P3 处理“怎么执行”和“怎么解释结果”：后端、采样、缓解与结果摘要都在这一层。

## 你在 P3 主要做什么

- 后端抽象（statevector/qiskit/扩展后端）
- 作业执行与状态跟踪
- repro 与 run summary 导出

## 常见工程决策

- 先用 statevector 验证流程，再切 shots/真实采样路径
- 先保证字段稳定，再做性能优化
- 每次后端切换都保留可比对的基准样例

## 工程建议

- 统一 trace id/request id 贯穿 API 与日志
- 先保证结果 schema 稳定，再优化性能
- 将时间线和状态机行为纳入回归测试

## 继续阅读

- [P4 作业与可复现](./jobs-and-reproducibility)
- [云与作业概览](../cloud/overview)
