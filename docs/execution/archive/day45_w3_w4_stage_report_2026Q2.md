# Day 45 Stage Report: P2-W3 / P2-W4

范围：经典边界（W3）与缓解进阶块（W4）的工程化收敛。

## W3（AVAS/CASSCF 边界）

- 维持 `partial` 口径，不新增闭源等价宣称。
- driver / 审计叙事保持与差距文档、矩阵、测试入口一致。

## W4（缓解进阶）

- 运行摘要补强：
  - `mitigation_zne_mode_yaml`
  - `mitigation_zne_scales_yaml`
  - `protocol_zne_mode`
- 导出镜像可直接用于 Methods 表格与审计对照（`_mirror_run_summary`）。

## 验证

- ZNE 配置回归（`configs/example_h2_zne_circuit_fold.yaml`）验证 run_summary/export 联动。
- parity 抽样脚本覆盖保持通过。

## 结论

- W3/W4 完成“边界稳定 + 键名稳定 + 导出可读”的阶段目标。
