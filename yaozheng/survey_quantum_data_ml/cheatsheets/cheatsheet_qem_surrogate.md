<style>
@media print { .cheatsheet { page-break-after: always; } }
</style>

<div class="cheatsheet">

# 速查：QEM / 处理器代理 / VQE 加速

**路径**：1（一一对应标签）· **TRL**：4–5

## 何时选此路线
- 标签 = 能量/期望/无噪极限/最优 θ，经典可定义
- 量子调用极贵，需 **surrogate 纯经典 inference**
- VQE/QAOA 优化循环中大量中间 (θ, shots) 可复用

## 推荐 ML 栈
| 子任务 | 输入 → 输出 | 模型 |
|--------|------------|------|
| 处理器代理 | (circuit, params, noise ctx) → ⟨O⟩ | MLP / GNN / Set Transformer |
| ZNE 加速 | (x, O, λᵢ) → f(x,O,0) | S-ZNE surrogate |
| 噪声缓解 | noisy stats → mitigated | Noise-agnostic NN, NNAS, CITL-QMEM |
| VQE init | (H graph, ansatz) → θ₀ | Qracle GNN |
| VQE one-shot | 历史 (θ, E) → θ* | MLP / GPR |

## 必读文献
- Predictive Surrogates 2026（42 qubit, Nat. Commun.）
- S-ZNE 2025 · Noise-agnostic QEM 2025 · NNAS 2025
- Qracle 2025 · ML-VQE Optimiser 2025 · CITL-QMEM 2025

## 数据必存字段
`labels.energy_hartree` 或 `expectation_values` · 全 VQE 轨迹 (θ, E, shots) · `mitigation.applied` · `device_calibration_id`

## 常见坑
- 只存最终 E 不存中间步 → 丢失 ML-VQE 训练信号
- Surrogate 未覆盖 noise drift → 需 calibration-conditioned 或在线更新
- 标签来自未收敛 VQE → 加 convergence flag + uncertainty

## 验收指标
Surrogate MAE · quantum call reduction · mitigation overhead · transfer gap (device A→B)

**BibTeX 键**：`PredictiveSurrogates2026`, `SZNE2025`, `Qracle2025`, `NoiseAgnosticQEM2025`

</div>
