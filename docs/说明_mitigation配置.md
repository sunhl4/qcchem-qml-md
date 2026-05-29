# Mitigation 配置（`mitigation` 节）

YAML 路径与 Pydantic 模型 `MitigationSpec` 一致（`schema_version: "2"` 实验）。

## 顶层块

| 字段 | 说明 |
|------|------|
| `pmsv_enabled` | 启用 PMSV shot 过滤（方差膨胀报告，非完整 readout tomography） |
| `zne_enabled` | 启用 ZNE stub 曲线（`zne_scales` 传入 Pauli 协议） |
| `zne_scales` | 噪声缩放因子列表，如 `[1.0, 2.0, 3.0]` |
| `spam_calibration` | SPAM 校准 toy 块（可选） |
| `classical_shadows_stub` | 经典 shadows 占位导出 |
| `qermit_analog` | Qermit 风格 DAG 报告（非商业 Qermit 运行时） |

## 示例

```yaml
mitigation:
  pmsv_enabled: false
  zne_enabled: true
  zne_scales: [1.0, 2.0, 3.0]
```

## 与 Pauli 协议的关系

- ZNE / PMSV 在 `protocol_finalize` 阶段挂到 `PauliAveragingProtocol`。
- `repro.parity_snapshot` 记录 `zne_enabled`、`mitigation_zne_scales` 等键。
- 语义说明：[`mitigation_PMSV_ZNE_Qermit_mapping.md`](mitigation_PMSV_ZNE_Qermit_mapping.md)

## 校验

跨节规则见 `config/_experiment_validation.py`（例如 ZNE scales 非空当 `zne_enabled: true`）。
