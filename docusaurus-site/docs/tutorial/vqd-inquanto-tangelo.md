---
title: VQD / deflation（InQuanto 叙事 × Tangelo deflation）
description: 变分量子紧缩与 SandboxAQ Tangelo deflation_circuits 对照；本栈 YAML 与 meta 契约。
keywords:
  - VQD
  - deflation
  - InQuanto
  - Tangelo
  - excited states
---

# VQD 与跨栈对照（InQuanto × Tangelo）

本页说明 **`qchem_stack` 中 VQD（紧缩激发）** 与两套公开生态的关系：

- **Quantinuum InQuanto**：手册 [AlgorithmVQD](https://docs.quantinuum.com/inquanto/manual/algorithms/algorithms_vqd.html) 将能量、重叠平方、权重表达为多个 `Computable`，并由若干 **Protocol** 分别估计。
- **SandboxAQ Tangelo**：在 [`VQESolver`](https://github.com/sandbox-quantum/Tangelo/blob/main/tangelo/algorithms/variational/vqe_solver.py) / [`SA_VQESolver`](https://github.com/sandbox-quantum/Tangelo/blob/main/tangelo/algorithms/variational/sa_vqe_solver.py) 上提供 **`deflation_circuits`** + **`deflation_coeff`**，在能量估计里叠加与前序电路的重叠惩罚（示例笔记本 [excited_states.ipynb](https://github.com/sandbox-quantum/Tangelo-Examples/blob/main/examples/chemistry/excited_states.ipynb)）。

## 本栈实现（工程真值）

- **算法核**：Higgott 等 *Quantum* **3**, 156 (2019) 的标量目标  
  \(E(\theta)+\lambda \sum_i |\langle\psi_i|\psi(\theta)\rangle|^{2p}\)（`overlap_exponent` 控制幂次）。
- **优化模型**：**单次**经典标量最小化（`COBYLA` / `L-BFGS-B` / `Nelder-Mead` 可选），**不是** InQuanto 那套「三套独立优化器」；`three_protocol` 块用于 **报告 + 可选 Pauli / swap-test 预算**。
- **Tangelo 类比**：`out["vqd"]["meta"]["tangelo_deflation_analogy_v1"]` 将 YAML 中的 `vqd_penalty_weight` / `vqd_penalty_weights` 与 Tangelo 的 `deflation_coeff` 叙事对齐，并声明本栈在 **态向量空间** 上累加重叠，而非 Tangelo 默认的 **电路层 inverse+模拟** 路径。

## YAML 入口

- **HEA 变分后 VQD**（历史默认）：`variational_ansatz: hea`，`vqd_after_variational: true`（见 `configs/example_h2_excited_smoke.yaml`）。
- **UCCSD 变分后 VQD**（同簇参数化上的 deflation）：`variational_ansatz: uccsd` + 同上；仓库样例 **`configs/example_h2_vqd_uccsd.yaml`**。

常用键：

| 键 | 含义 |
|----|------|
| `vqd_n_states` | 基态 + 激发层数（总能量条数） |
| `vqd_penalty_weight` | 标量 λ（当未设 `vqd_penalty_weights`） |
| `vqd_penalty_weights` | 每层紧缩的 λ 列表，长度 `vqd_n_states - 1` |
| `vqd_init_strategy` | `legacy`（与 2026 前行为一致）、`reuse_ground_perturb`、`previous_layer_perturb`、`random_uniform` |
| `vqd_optimizer_method` | `COBYLA` / `L-BFGS-B` / `Nelder-Mead` |
| `vqd_max_overlap_warn` | 若与已解态平方重叠和超过阈值，在 `meta.vqd_warnings` 中记录（`null` 关闭） |

## 机读出口

- 运行结果：`out["vqd"]["meta"]` 含 `tangelo_deflation_analogy_v1`、`inquanto_vqd_semantics_v1`、`vqd_variety_yaml`（`hea` / `uccsd`）。
- 复现摘要：`repro.run_summary` 会镜像部分 YAML 与 `vqd_warnings_present` 等（见 `RUN_SUMMARY_DOCUMENTED_KEYS`）。

## 相关

- 公开矩阵行：`AlgorithmVQD`（`docusaurus-site/docs/parity/public-matrix`）
- 代码：``src/qchem_stack/quantum/algorithms/excited.py``（`VQD`）
