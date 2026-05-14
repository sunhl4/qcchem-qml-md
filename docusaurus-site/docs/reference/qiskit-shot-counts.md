# 设备比特串与 Qiskit 采样路径

本文说明 `get_counts` 到 Pauli 期望估计的工程路径，以及它与其他能量路径的关系。

## 适用场景

- 你要从精确期望切换到 shots 路径
- 你要解释 Qiskit 采样结果与方差变化
- 你要把采样来源写进可审计输出

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

## 输出检查

- `expectation_source`：确认来源是 shots 路径
- `measurement_histogram_rows`：确认测量直方图已记录
- `run_summary`：确认关键摘要可用于跨运行对比

## 注意事项

- 不要与 `run_sampled_pauli_protocol` 同时开启
- shots 不足会导致方差增大
- 生产环境建议显式记录后端与 transpile 配置

## 排障建议

- **结果波动大**：提高 shots 或增加重复试验次数
- **路径未生效**：检查 `provider` 与 `run_qiskit_shots_pauli_protocol` 是否同时设置
- **指标不一致**：确认比较时使用相同随机种子和预算

## 关联页面

- [ZNE 与 Qiskit 复现路径](/tutorial/zne-qiskit-repro)
- [切换 Backend 并对比结果](/tutorial/switch-backend-compare)
