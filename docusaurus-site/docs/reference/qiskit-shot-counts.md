# 设备比特串与 Qiskit 采样路径

本文说明 `get_counts` 到 Pauli 期望估计的工程路径，以及它与其他能量路径的关系。

## 三条能量路径

1. 执行器精确期望（默认）
2. 状态向量采样模拟（sampled path）
3. Qiskit 比特串采样（`run_qiskit_shots_pauli_protocol`）

## 关键点

- Qiskit 路径按组执行测量线路并读取 `get_counts`
- 结果可写入 `measurement_histogram_rows`
- 同一协议下保留 `expectation_source` 便于审计

## 配置示例

```yaml
backend:
  provider: qiskit
  shots_per_circuit: 2048
quantum:
  use_pauli_protocol: true
  run_qiskit_shots_pauli_protocol: true
```

## 注意事项

- 不要与 `run_sampled_pauli_protocol` 同时开启
- shots 不足会导致方差增大
- 生产环境建议显式记录后端与 transpile 配置
