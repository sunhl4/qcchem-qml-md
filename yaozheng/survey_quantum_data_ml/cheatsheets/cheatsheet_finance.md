<style>
@media print { .cheatsheet { page-break-after: always; } }
</style>

<div class="cheatsheet">

# 速查：金融 & 组合优化

**路径**：1（优化目标/收益可经典对照）· **TRL**：3

## 何时选此路线
- QUBO/Ising 映射：portfolio、风险约束、离散资产
- 标签 = 最优组合、期望收益、波动率、QUBO 能量
- 经典 solver 为 gold standard 对照

## 推荐 ML 栈
| 任务 | 量子侧 | 经典 ML 侧 |
|------|--------|-----------|
| Portfolio QUBO | QAOA / VQE / Quantum annealing | Hybrid solver + 参数 auto-tuning |
| 时序预测 | QLSTM / QSVR / hybrid QNN | 与 ANN/LSTM 架构匹配 benchmark |
| 风险/定价 | Quantum-enhanced Monte Carlo（长期） | 经典 MC + QML 子模块 pilot |

## 必读文献
- Portfolio RBI real-world 2025（Raiffeisen + D-Wave）
- Multi-discretization PO 2025 · Financial QML benchmark 2026
- CFA Institute quantum finance brief 2025

## 数据必存字段
`problem.parameters`（协方差、约束）· QUBO 最优解 · 经典 exact/hybrid baseline · 噪声 mitigation 记录

## 常见坑
- 10–20 资产外 NISQ 噪声主导 → 误差缓解 mandatory
- 无 classical baseline 的 "quantum win" 不可信
- 时序任务：Fellner 2026 显示 VQA 常不如经典 → niche regime 才投

## 验收指标
Return/risk vs exact · wall-clock · solution quality @ fixed qubit-hours · regime-specific gain (Financial 2026)

**BibTeX 键**：`PortfolioRBI2025`, `FinancialQMLBenchmark2026`

</div>
