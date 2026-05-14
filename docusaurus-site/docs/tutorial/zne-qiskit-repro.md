# ZNE 与 Qiskit 复现路径

本教程用于验证误差缓解（ZNE）与 Qiskit shots 路径的联动输出。

## 教程目标

- 运行 Qiskit shots 路径
- 启用 ZNE 相关配置
- 检查 repro 中的缓解与曲线字段

## 前置条件

- 已安装 Qiskit 相关依赖（通常来自 `pip install -e ".[all]"`）
- 可用配置：`configs/example_h2_zne_circuit_fold.yaml`

## 步骤 1：运行示例配置

```bash
python scripts/smoke_pipeline.py --config configs/example_h2_zne_circuit_fold.yaml
```

## 步骤 2：读取结果对象

优先检查 `run_summary`，再检查 `repro` 中的缓解相关键。

## 检查点

- `expectation_source` 是否为 shot 路径
- `mitigation` 相关块是否完整
- `parity_snapshot` 中是否保留对标所需键

## 常见问题

- **字段缺失**：先确认是否真的使用了 ZNE 配置文件
- **结果噪声大**：检查 shots 预算是否过低
- **性能慢**：先在小体系验证流程，再扩展规模

## 下一步

- [切换 Backend 并对比结果](./switch-backend-compare)
- [P3 执行与分析](../guide/execution-and-analysis)
