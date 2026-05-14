# 切换 Backend 并对比结果

本教程帮助你在同一配置骨架下切换执行后端，并做可复现对比。

## 目标

- 在同一实验设定下对比两个后端
- 输出可追溯的对比结果
- 避免“配置变了导致不可比”的常见陷阱

## 前置条件

- 已跑通 `configs/example_h2.yaml`
- 至少准备两份仅后端不同的配置（例如 statevector / qiskit shots）

## 对比步骤

1. 固定同一 `experiment_yaml`
2. 分别设置不同 `backend.provider`
3. 比较 `run_summary` 与资源指标

建议每次只改 `backend` 相关块，其他参数保持不变。

## 对比维度

- 能量估计与方差
- 运行时间与队列行为
- 资源行（深度、2Q 门、shots）

## 最小执行示例

```bash
python scripts/smoke_pipeline.py --config configs/example_h2.yaml
python scripts/smoke_pipeline.py --config configs/example_h2_qiskit_shots.yaml
```

然后对比两次输出中的 `run_summary` 核心键。

## 注意

- 后端差异会导致方差与时延分布不同
- 做对比时尽量固定随机种子和 shots 预算

## 验证清单

- 两次运行都成功结束
- 对比报告中明确标注了配置与后端版本
- 至少包含一项数值指标 + 一项资源指标

## 下一步

- [ZNE 与 Qiskit 复现路径](./zne-qiskit-repro)
- [P3 执行与分析](../guide/execution-and-analysis)
