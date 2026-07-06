<style>
@media print { .cheatsheet { page-break-after: always; } }
</style>

<div class="cheatsheet">

# 速查：量子多体 & 相分类

**路径**：2（原生测量）→ 可选 1 微调 · **TRL**：4–5

## 何时选此路线
- 有 randomized Pauli / Clifford / shadow 测量数据
- 目标：相分类、基态性质、关联函数、纠缠熵
- 经典 full tomography 不可行

## 推荐 ML 栈
| 任务 | 模型 | 量子数据 |
|------|------|---------|
| 性质预测 | GPT / Set Transformer | shadow vectors |
| 相分类 | QSVM / SSL4Q / PCA+无监督 | shadow spin configs |
| 大系统 | GLQK（局域 kernel） | 子系统 shadow |
| 少标签 | LLM4QPE / FNQS 预训练 → fine-tune | 跨 Hamiltonian 预训练 |

## 必读文献（2024–2026）
- Cho & Kim 2024 — IBM 127q 实验 + ML（Nat. Commun.）
- ShadowGPT 2024 · LLM4QPE 2024 · FNQS 2025
- SSL4Q 2024 · GLQK 2025 · Robust shallow shadows 2025
- UDA imperfect quantum data 2026

## 数据必存字段
`measurement.protocol=shadow|random_pauli` · `raw_outcomes` 或 `shadow_vectors` · `problem.parameters`（J, h, …）

## 常见坑
- Global fidelity kernel 大 qubit 指数集中 → 用 GLQK / local shadow
- sim→hardware 漂移 → UDA 或 robust shallow shadows
- 仅 Z 基测量 → 可能丢失 sign structure → 多基（X 关联）

## 验收指标
Phase accuracy/F1 · shadow sample complexity · few-shot Δ vs 无预训练 · sim vs hw gap

**BibTeX 键**：`Cho2024ExpMLQuantumData`, `ShadowGPT2024`, `LLM4QPE2024`, `GLQK2025`

</div>
