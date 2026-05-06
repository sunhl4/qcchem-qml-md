# ZNE 与 Qiskit 复现路径

本教程用于验证误差缓解与 Qiskit 采样路径的联动输出。

## 教程目标

- 运行 Qiskit shots 路径
- 启用 ZNE 相关配置
- 检查 repro 中的缓解与曲线字段

## 检查点

- `expectation_source` 是否为 shot 路径
- `mitigation` 相关块是否完整
- `parity_snapshot` 中是否保留对标所需键
