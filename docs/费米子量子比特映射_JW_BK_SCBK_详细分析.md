# 费米子–量子比特映射（JW / BK / SCBK）：详细分析与工程笔记

本文从**原理、资源统计、取舍与本仓实现**四个层面整理「映射」话题，供组会稿以外的深入阅读；与 [`组会汇报_qchem_stack_Tangelo工程细节.md`](组会汇报_qchem_stack_Tangelo工程细节.md) 中的提要相互引用。

---

## 1. 问题背景

二次量子化哈密顿量作用在**费米子 Fock 空间**；量子计算机操作的是**量子比特**与 Pauli 算符。必须选定一种 **fermion-to-qubit mapping**，把产生/湮灭算符的代数关系（特别是反对易与占据数约束）编码到比特算符上，才能定义 `QubitHamiltonian`、测量协议与变分线路。

---

## 2. 三种映射在做什么（直觉版）

### 2.1 Jordan–Wigner（JW）

- 每个自旋轨道对应一个 qubit，**占据 = |1⟩，空 = |0⟩**（常见约定）。
- 优点：**直观**、与大量教材和文献公式一致，便于推导与调试。
- 代价：一般会产生**长串 Pauli 链**（非局域），在 naive 线路里 CNOT 深度与门数往往偏高；具体仍依赖哈密顿量项结构与编译。

### 2.2 Bravyi–Kitaev（BK）

- 仍用 **n 个 qubit** 表示 n 个自旋轨道，但用另一套二进制编码，使**占据数等算符更局域**。
- 优点：许多模型上 Pauli 权重更友好，有利于减少某些线路复杂度。
- 代价：编码不直观，手工推导易错；与部分「按 JW 写死」的化学线路约定不完全一致。

### 2.3 Symmetry-conserving Bravyi–Kitaev（SCBK，OpenFermion 实现）

- 在 BK 思路上，进一步利用**费米子对称性**（典型为粒子数宇称等），**从 2n 个自旋轨道对应的 2n 比特中消去两个比特自由度**，得到 **(2n − 2)** 个 qubit 的表示。
- 优点：在**对称性成立且栈全程一致支持**时，常同时减少**比特数**与协议下的**二比特门负载**。
- 代价：对称性**被破坏或难以利用**时优势不再；与部分 ansatz / 参考态实现假设需逐条核对（见 §5）。

---

## 3. 本仓 H₂（2e / 2o，sto-3g）实跑资源对比

### 3.1 如何复现（工程真值来源）

1. 配置基底：`configs/example_h2.yaml`（几何、活性空间与主汇报一致）。
2. 对每个映射各跑一次流水线并写出 JSON：

   ```bash
   PYTHONPATH=src python docs/assets/export_mapping_comparison_data.py
   ```

3. 输出：`docs/assets/data/mapping_comparison_h2_sto3g.json`（schema：`mapping_comparison_v1`）。

4. 柱状图：`docs/assets/mapping_comparison.png`，由 `docs/assets/generate_all_figures.py` 中的 `fig_mapping_comparison()` 读取上述 JSON 绘制。

### 3.2 指标含义（避免和「单线路 CNOT 深度」混淆）

- **`n_qubits`**：该次运行中协议/后端使用的逻辑比特数（SCBK 下为 2）。
- **`compiled_sum_twoq`（导出 JSON 字段名）**：对应 `resource_summary` 中的 **`sum_twoq`**，即 **Pauli 测量协议下各条已编译线路的二比特门个数之和**（对多条线路求和，不是单线路深度）。
- **`compiled_max_depth`**：各线路编译后深度的**最大值**（同上 JSON），与「总和」是不同维度。

### 3.3 当前导出数值（与 JSON 一致）

| 映射 | `mapping_key` | 量子比特数 | 二比特门总和 `sum_twoq` | 备注 |
|------|----------------|------------|-------------------------|------|
| Jordan–Wigner | `jordan_wigner` | 4 | 15 | 同一 pipeline、同一 `example_h2.yaml` 除映射外不变 |
| Bravyi–Kitaev | `bravyi_kitaev` | 4 | 9 | 同上 |
| Sym.-conserving BK | `symmetry_conserving_bravyi_kitaev` | **2** | **2** | 同上 |

若你本地重跑后数字有小幅变化，以**最新 JSON** 为准（依赖 OpenFermion、编译路径、协议分组等版本细节）。

---

## 4. 「既然 SCBK 比特少、门也少，为什么还要 JW / BK？」

SCBK 在**理想对称性 + 全栈一致**时往往更省，但不构成「永远只选 SCBK」的充分条件：

1. **对称性是否可用**  
   开壳层、外场、对称性破缺参考、或活性空间与对称性假设不一致时，SCBK 的简化前提可能不成立或实现上更绕。

2. **与 ansatz / 线路语义绑定**  
   许多化学 UCC 类线路在文献与实现上**按 JW 约定书写**；本仓对 **UCCSD Trotter 等路径在 BK/SCBK 上标为 `n/a` 或需换 ansatz** 的说明，见公开 parity 矩阵与 `docusaurus-site` 中 UCCSD/Trotter 相关页。即：**映射**与**变分线路**是两件独立决策，不能只看哈密顿量项数。

3. **「少比特」≠「实验总成本更低」**  
   信息压缩到更小子空间可能伴随**更强纠缠或更难制备的初态**；再加上硬件连通度、读出与校准，**2-qubit 方案未必**在真实芯片上优于 4-qubit 方案。

4. **教学、对齐与调试**  
   JW 最易与参考书、对照程序对齐；开发新功能时常先用 JW 锁定数值，再切 BK/SCBK 做资源对比。

**一句话**：SCBK 是**强工具**；JW/BK 仍是**通用默认、文献对齐与算法覆盖**所必需。

---

## 5. 本仓代码与配置入口（便于审计）

| 主题 | 路径 |
|------|------|
| 哈密顿量 + 映射 | `src/qchem_stack/chem/hamiltonian.py` |
| 映射注册与元数据 | `src/qchem_stack/chem/fermion_mapping_registry.py` |
| YAML 键 | `active_space.fermion_qubit_mapping`（如 `jordan_wigner` / `bravyi_kitaev` / `symmetry_conserving_bravyi_kitaev`） |
| 实跑导出脚本 | `docs/assets/export_mapping_comparison_data.py` |
| 作图 | `docs/assets/generate_all_figures.py` → `fig_mapping_comparison()` |
| 映射相关单测（接线） | `tests/chem/test_fermion_qubit_mapping.py`、端到端覆盖面见 `tests/orchestration/test_orchestration_pipeline.py`、`tests/backends/test_backend_capability_conformance.py` |

---

## 6. 小结

- **JW**：直观、文献对齐、算法实现假设最常见。  
- **BK**：常改善局域性，仍占满 n qubit（与 JW 同比特数）。  
- **SCBK**：在对称性可用且栈支持时，**同时削减比特数与协议下二比特门总和**（本仓 H₂ 小例子见 §3）。  
- 汇报场景只需强调「**可配置、可导出、与协议资源统计挂钩**」；细节与取舍以本文与 JSON 为准即可。
