# H₂ 键长扫描 + 预训练 + 在线学习结果分析（job 6759）

## 结论摘要

1. **流水线完整跑通**：Phase A 扫描 16 点 → Phase B 预训练 120 epoch → Phase C 20 轮 OL。
2. **校验误差明显下降**：max|ΔE| 从第 1 轮 **0.309 Ha** 降到最好 **0.069 Ha**（第 18 轮），约降到 1/4；末轮 **0.083 Ha**。
3. **未达收敛阈值** `0.0005` Ha（差约两个数量级）。
4. **训练集膨胀伴随风险**：最终 56 帧中有 **13** 个键长 ≥5 Bohr 的解离/非物理构型（来自 MD 校验帧被并入），会污染后续拟合。

## 关键数字

| 指标 | 值 |
|------|-----|
| 墙钟 | 9h05m（30 核 / 120G） |
| 预训练帧 / 最终帧 | 17 / 56 |
| 预训练末 E-MAE | 8.012 Ha |
| 预训练末 F-RMSE | 2.848 |
| max\|ΔE\| r1 → best → r20 | 0.309 → 0.069 → 0.083 |
| mean\|ΔE\| r1 → best → r20 | 0.225 → 0.059 → 0.082 |

## 图

- `figures/h2_bondscan_ol_6759_overview.png`
- `figures/h2_bondscan_ol_6759_train_parity.png`

## 改进建议

- 过滤 MD 解离帧（键长上限，如 <3 Bohr）再并入训练集
- 预训练启用 `energy_normalization: subtract_mean`，加长 epoch / 加密扫描
- 适当放宽或分阶段设置 `energy_tolerance_hartree`（先 0.05 → 0.01 → 5e-4）
