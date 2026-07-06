<style>
@media print { .cheatsheet { page-break-after: always; } }
</style>

<div class="cheatsheet">

# 速查：药物发现 / 量子化学 / 材料

**路径**：1 为主，生成任务 + 混合 · **TRL**：2–4

## 何时选此路线
- 标签：结合能、IP/EA、毒性、带隙、力（经典 DFT/CCSD 可参照）
- 量子提供 sample-efficient kernel 或 generative hit
- 材料：SQD 采样 + 经典对角化

## 推荐 ML 栈
| 场景 | 方法 |
|------|------|
| Hit 生成 | Hybrid quantum-classical generative（KRAS 2024） |
| 亲和力/毒性 | QSVM / VQR / hybrid ensemble（Q-CaDD 2026） |
| 大规模筛选 | QGNN + VQE ranking（QM9 类） |
| 能量/力场 | MLFF + 量子 labels；SQD + classical postprocess |
| 大体系 Hamiltonian | 纯经典 GNN（ICML 2025）— 路径 1 标签范式 |

## 必读文献
- KRAS inhibitors Nat. Biotech. 2024 · npj Drug Discovery review 2025
- Q-CaDD 2026 · QGNN-VQE EPJ D 2025 · SQD band gaps 2025
- Hamiltonian GNN ICML 2025 · ResT-dNN JCTC 2025

## 数据必存字段
分子标识/描述符 · `labels.energy_hartree` / `class_label` · `classical_reference.method` · active space / embedding 上下文

## 常见坑
- "Quantum advantage" 在 KRAS 2024 中作者明确未证
- 低数据 regime 才常报 QSVM/VQR 增益 → 报告 n_train 曲线
- 化学标签噪声（VQE 未收敛）污染 MLFF

## 验收指标
AUC/MAE vs classical · sample efficiency (n<500) · 实验验证 hit rate（如有）

**BibTeX 键**：`KRASQuantumDrug2024`, `QCaDD2026`, `SQDPeriodicMaterials2025`

</div>
