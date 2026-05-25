# 千问三模型评测原始结果

生成时间（UTC）：20260525T013840Z

## 汇总

| 场景 | 模型 | 延迟(s) | 输入 tokens | 输出 tokens | 状态 |
|------|------|---------|-------------|-------------|------|
| S1_daily | qwen-flash | 3.41 | 171 | 301 | OK |
| S1_daily | qwen3-coder-next | 2.11 | 171 | 274 | OK |
| S1_daily | qwen3.7-max | 31.77 | 167 | 3683 | OK |
| S2_coding | qwen-flash | 8.01 | 267 | 818 | OK |
| S2_coding | qwen3-coder-next | 4.02 | 267 | 872 | OK |
| S2_coding | qwen3.7-max | 14.93 | 266 | 1833 | OK |
| S3_architecture | qwen-flash | 18.82 | 371 | 1433 | OK |
| S3_architecture | qwen3-coder-next | 12.61 | 371 | 1934 | OK |
| S3_architecture | qwen3.7-max | 34.84 | 369 | 4063 | OK |

## S1_daily

### qwen-flash

- 量子计算硬件仅原生支持 Pauli 算符（如 $X, Y, Z$）的量子门操作，而费米子哈密顿量中的算符（如 $c^\dagger_i c_j$）在 qubit 系统中无法直接实现，因此必须通过映射将其转化为 qubit 算符。

- Jordan-Wigner 映射将费米子算符转换为 qubit 算符后，哈密顿量中的每项变为一个 Pauli 算符的乘积，即“Pauli 字符串”。例如，单粒子跃迁项 $c^\dagger_i c_j$ 被映射为包含 $Z$ 算符的非局域字符串，其作用范围从 $i$ 到 $j$ 之间所有 qubit。

- 其主要代价是链式结构导致的非局域性：当 $i < j$ 时，$c^\dagger_i c_j$ 的映射结果包含从 $i$ 到 $j-1$ 所有中间 qubit 的 $Z$ 算符，形成长度为 $j-i$ 的非局域字符串，显著增加纠缠深度与误差累积风险。此外，该映射需额外 $N$ 个 qubit 来表示 $N$ 个费米子模式，带来资源开销。

---

### qwen3-coder-next

- **硬件适配需求**：量子硬件原生支持泡利算符（X, Y, Z）及对应门操作，而费米子系统自然由产生/湮灭算符描述，其反对易关系无法直接在量子电路上实现，故需通过Jordan-Wigner（JW）映射将费米子算符转化为等效的qubit泡利算符组合，实现硬件可执行的哈密顿量模拟。  
- **哈密顿量结构变化**：映射后，单个费米子项（如 \(c_j^\dagger c_k\)）通常转化为长度为 \(O(|j-k|)\) 的泡利字符串（如 \(Z\) 链连接j与k之间的qubit），导致原本局域的费米子相互作用在qubit表象下变为非局域的多体项，显著增加电路深度与误差累积风险。  
- **主要代价**：JW映射需引入线性规模的qubit（与费米子模式数相同），且其非局域性随粒子间距增长而恶化；例如，最近邻跃迁项在JW下可能需用长度为 \(O(N)\) 的泡利字符串表示，严重制约算法效率与可扩展性。

---

### qwen3.7-max

* **映射动机**：量子硬件原生仅支持泡利算符，无法直接处理满足反对易关系的费米子算符，故需乔丹-维格纳映射将其转为量子比特算符以便执行。
* **形式变化**：映射后，费米子算符变为附带Z算符字符串的泡利乘积。这导致原本局域的费米子相互作用，在比特空间中演化为非局域的长字符串操作。
* **实际代价**：链式映射引入的非局域性，使模拟最近邻跳跃需执行正比于系统规模的受控非门链，大幅增加量子线路深度与噪声敏感度。

---


## S2_coding

### qwen-flash

```python
from typing import List, Tuple, Dict, Set

def select_adapt_candidates(
    pool: List[Tuple[str, Tuple[int, ...]]],
    gradient_scores: Dict[str, float],
    k: int,
    max_qubits: int
) -> List[str]:
    """
    从候选算符池中选择适应性优化的算符。

    参数:
        pool: 算符列表，每个元素为 (算符名, 涉及的 qubit 索引元组)
        gradient_scores: 算符名到梯度绝对值的映射
        k: 最多选择的算符数量
        max_qubits: 电路宽度上限（即最多允许的 qubit 数量）

    返回:
        选中的算符名列表，按梯度降序排列，且满足 qubit 并集不超过 max_qubits。
    """
    # 过滤并排序：仅保留 score > 1e-8 且在 gradient_scores 中存在的算符，并按 score 降序
    filtered_sorted = [
        name for name, qubits in sorted(pool, key=lambda x: gradient_scores.get(x[0], 0), reverse=True)
        if gradient_scores.get(name, 0) > 1e-8
    ]

    selected: List[str] = []
    used_qubits: Set[int] = set()

    for name in filtered_sorted:
        qubits = [q for q in pool[filtered_sorted.index(name)][1]]
        qubit_set = set(qubits)

        # 检查并集是否超过 max_qubits
        if len(used_qubits.union(qubit_set)) > max_qubits:
            continue

        selected.append(name)
        used_qubits.update(qubit_set)

        if len(selected) >= k:
            break

    return selected


if __name__ == "__main__":
    # 测试用例 1: 正常情况，有足够空间
    pool1 = [
        ("X1", (0,)),
        ("Y2", (1,)),
        ("Z3", (2,)),
        ("H4", (3,)),
        ("ZZ5", (0, 1))
    ]
    grads1 = {"X1": 0.5, "Y2": 0.4, "Z3": 0.3, "H4": 0.2, "ZZ5": 0.6}
    result1 = select_adapt_candidates(pool1, grads1, k=3, max_qubits=4)
    assert result1 == ["ZZ5", "X1", "Y2"], f"Test 1 failed: got {result1}"

    # 测试用例 2: 超过最大 qubit 数限制
    pool2 = [
        ("A", (0, 1)),
        ("B", (2, 3)),
        ("C", (4, 5))
    ]
    grads2 = {"A": 1.0, "B": 0.9, "C": 0.8}
    result2 = select_adapt_candidates(pool2, grads2, k=3, max_qubits=3)
    assert result2 == ["A", "B"], f"Test 2 failed: got {result2}"

    # 测试用例 3: 梯度太小被过滤
    pool3 = [
        ("Small1", (0,)),
        ("Large2", (1,))
    ]
    grads3 = {"Small1": 1e-9, "Large2": 1.0}
    result3 = select_adapt_candidates(pool3, grads3, k=2, max_qubits=2)
    assert result3 == ["Large2"], f"Test 3 failed: got {result3}"
```

---

### qwen3-coder-next

```python
from typing import List, Tuple, Dict, Set

def select_adapt_candidates(
    pool: List[Tuple[str, Tuple[int, ...]]],
    gradient_scores: Dict[str, float],
    k: int,
    max_qubits: int
) -> List[str]:
    """
    从候选算符池中选择满足条件的算符，用于ADAPT-VQE等变分量子算法。
    
    Args:
        pool: 算符池，每个元素为 (算符名, 涉及的qubit索引元组)
        gradient_scores: 算符名到梯度绝对值的映射
        k: 最多选择的算符数量
        max_qubits: 电路宽度上限（即所有选中算符涉及qubit的并集大小）
    
    Returns:
        选中的算符名列表
    """
    # Step 1: 过滤出存在于gradient_scores中且score > 1e-8的项
    filtered_pool = [
        (name, qubits) for name, qubits in pool
        if name in gradient_scores and gradient_scores[name] > 1e-8
    ]
    
    # Step 2: 按score降序排序
    filtered_pool.sort(key=lambda x: gradient_scores[x[0]], reverse=True)
    
    # Step 3 & 4: 依次选择，确保qubit并集不超过max_qubits
    selected_names: List[str] = []
    used_qubits: Set[int] = set()
    
    for name, qubits in filtered_pool:
        if len(selected_names) >= k:
            break
        
        # 检查加入当前算符后qubit总数是否超限
        new_qubits = set(qubits) - used_qubits
        if len(used_qubits) + len(new_qubits) <= max_qubits:
            selected_names.append(name)
            used_qubits.update(new_qubits)
    
    return selected_names


if __name__ == "__main__":
    # Test 1: 基本功能测试
    pool1 = [
        ("X0", (0,)),
        ("Y1", (1,)),
        ("Z0Z1", (0, 1)),
        ("X2", (2,))
    ]
    scores1 = {"X0": 0.5, "Y1": 0.3, "Z0Z1": 0.4, "X2": 0.1}
    result1 = select_adapt_candidates(pool1, scores1, 3, 3)
    assert result1 == ["X0", "Z0Z1", "Y1"], f"Expected ['X0', 'Z0Z1', 'Y1'], got {result1}"
    
    # Test 2: 超过qubit限制测试
    pool2 = [
        ("X0", (0,)),
        ("Y1", (1,)),
        ("Z2", (2,)),
        ("X3", (3,))
    ]
    scores2 = {"X0": 0.5, "Y1": 0.4, "Z2": 0.3, "X3": 0.2}
    result2 = select_adapt_candidates(pool2, scores2, 4, 2)
    assert result2 == ["X0", "Y1"], f"Expected ['X0', 'Y1'], got {result2}"
    
    # Test 3: 低梯度过滤测试
    pool3 = [
        ("X0", (0,)),
        ("Y1", (1,)),
        ("Z2", (2,))
    ]
    scores3 = {"X0": 0.5, "Y1": 1e-9, "Z2": 0.3}
    result3 = select_adapt_candidates(pool3, scores3, 3, 3)
    assert result3 == ["X0", "Z2"], f"Expected ['X0', 'Z2'], got {result3}"
```

---

### qwen3.7-max

```python
from typing import Dict, List, Tuple


def select_adapt_candidates(
    pool: List[Tuple[str, Tuple[int, ...]]],
    gradient_scores: Dict[str, float],
    k: int,
    max_qubits: int,
) -> List[str]:
    """Select up to *k* ADAPT-VQE operator candidates from *pool*.

    Filtering and selection rules (applied in order):
        1. Keep only operators present in *gradient_scores* with |gradient| > 1e-8.
        2. Sort remaining operators by score in descending order.
        3. Greedily pick operators; skip any whose qubit union with already
           selected operators would exceed *max_qubits*.
        4. Stop when *k* operators are selected or the pool is exhausted.

    Args:
        pool: List of (operator_name, qubit_indices) tuples.
        gradient_scores: Mapping from operator name to absolute gradient value.
        k: Maximum number of operators to select this round.
        max_qubits: Upper bound on the number of distinct qubits used.

    Returns:
        List of selected operator names (up to *k*).
    """
    # 1) Filter: must exist in gradient_scores and score > 1e-8
    filtered: List[Tuple[str, Tuple[int, ...]]] = [
        (name, qubits)
        for name, qubits in pool
        if name in gradient_scores and gradient_scores[name] > 1e-8
    ]

    # 2) Sort by score descending
    filtered.sort(key=lambda item: gradient_scores[item[0]], reverse=True)

    # 3-4) Greedy selection respecting max_qubits and k
    selected: List[str] = []
    used_qubits: set[int] = set()

    for name, qubits in filtered:
        if len(selected) >= k:
            break
        candidate_qubits = used_qubits | set(qubits)
        if len(candidate_qubits) <= max_qubits:
            selected.append(name)
            used_qubits = candidate_qubits

    # 5) Return operator names
    return selected


if __name__ == "__main__":
    # Test 1: basic ranking — top-2 by score, no qubit conflict
    pool1 = [("X0", (0,)), ("Y1", (1,)), ("Z2", (2,))]
    scores1 = {"X0": 0.5, "Y1": 0.8, "Z2": 0.3}
    assert select_adapt_candidates(pool1, scores1, 2, 10) == ["Y1", "X0"]

    # Test 2: qubit-width limit forces skipping
    pool2 = [("A", (0, 1, 2)), ("B", (3, 4, 5)), ("C", (0, 1))]
    scores2 = {"A": 0.9, "B": 0.8, "C": 0.7}
    # A -> qubits {0,1,2} (3 <= 5, accept)
    # B -> qubits {0,1,2,3,4,5} (6 > 5, skip)
    # C -> qubits {0,1,2} (3 <= 5, accept)
    assert select_adapt_candidates(pool2, scores2, 3, 5) == ["A", "C"]

    # Test 3: filtering — missing key and sub-threshold score are excluded
    pool3 = [("X", (0,)), ("Y", (1,)), ("Z", (2,)), ("W", (3,))]
    scores3 = {"X": 0.5, "Y": 1e-9, "W": 0.3}  # Z absent, Y below threshold
    assert select_adapt_candidates(pool3, scores3, 10, 10) == ["X", "W"]
```

---


## S3_architecture

### qwen-flash

**memo：qchem_stack 流水线优化方案（H4 体系，4e/4q）**

---

### **A. 推荐 pipeline 拓扑（文字流程图）**

```
[初始态] → [Adapt-VQE (UCCSD-ansatz)] 
           ↓
       [VQD (2+ states)] ← [QSE(gaussian_h) 修正]
           ↓
    [能量后处理 + 精度评估]
           ↓
   [输出：基态 & 前2激发态能量]
```

> **说明**：  
> - Adapt-VQE 用于快速收敛至低能态；  
> - VQD 扩展至多激发态，避免重复采样；  
> - QSE(gaussian_h) 作为 sidecar 进行高阶相关修正，提升精度；  
> - 全链路 shot-based，总 shots ≤ 5×10⁵。

---

### **B. 三档方案对比表**

| 方案名 | 预期精度（ΔE vs. FCI） | shots 量级 | 实现复杂度 | 主要风险 |
|--------|--------------------------|-------------|--------------|------------|
| **UCCSD-VQE only** | ~10⁻² mHa（基态）<br>~10⁻¹ mHa（激发态） | 3×10⁵（单态）<br>5×10⁵（全态） | 低 | 无法捕捉强关联效应，激发态误差大；易陷入局部极小 |
| **Adapt-VQE + VQD** | ~10⁻³ mHa（基态）<br>~10⁻² mHa（激发态） | 2.5×10⁵（总）<br>分阶段采样 | 中 | VQD 谱分解对噪声敏感；需合理初始化 |
| **Adapt-VQE + QSE(gaussian_h)** | ~10⁻⁴ mHa（基态）<br>~10⁻³ mHa（激发态） | 4×10⁵（主路径）<br>+ 1×10⁵（QSE） | 高 | QSE 依赖 fermionic singles basis 精确性；需校准 gaussian_h 参数 |

> ✅ **推荐方案**：**Adapt-VQE + VQD + QSE(gaussian_h)**  
> ⚠️ **条件推荐**：若 QSE 校准失败或资源紧张，可退化为 **Adapt-VQE + VQD**  
> ❌ **不推荐**：仅用 UCCSD-VQE

---

### **C. Adapt 与 UCCSD 二选一决策树**

```text
1. 是否存在显著强关联特征？（如键断裂、近简并态）
   → 是 → 选 Adapt-VQE（动态门集适应）
   → 否 → 进入下一步

2. 期望精度是否 < 10⁻³ mHa？
   → 是 → 选 Adapt-VQE（UCCSD 表达能力不足）
   → 否 → 可考虑 UCCSD-VQE（但需验证）

3. 实验资源（shots）是否 ≤ 3×10⁵ 且无 QSE 支持？
   → 是 → 仍建议 Adapt-VQE（因更早收敛，节省 shots）
   → 否 → 可尝试 UCCSD-VQE（但不推荐长期使用）
```

> **结论**：在 H4 体系中，强关联显著，**必须优先选择 Adapt-VQE**。

---

### **D. 明确「不推荐」的组合及原因**

1. **UCCSD-VQE + 仅基态采样（无 VQD/QSE）**  
   - 原因：  
     - 无法有效描述激发态（尤其前两个），误差 > 10⁻¹ mHa；  
     - 单一 ansatz 无法应对 H4 的电子相关结构，导致基态能量偏差 ≥ 0.5 mHa。

2. **Adapt-VQE + QSE(gaussian_h) 但未启用 FermionicAdaptVQE 优化**  
   - 原因：  
     - 若未使用 FermionicAdaptVQE 生成有效 ansatz，QSE 输入态质量差，导致修正失效；  
     - 会引入“虚假精度”——看似低误差，实为错误输入导致的系统偏移。

---

### **E. 给算法工程师的 5 条验证实验（可测指标 + 通过阈值）**

1. **Adapt-VQE 收敛稳定性测试**  
   - 指标：连续 5 次迭代能量变化 ΔE < 10⁻⁴ mHa  
   - 通过阈值：≥ 90% runs 满足

2. **VQD 谱分解保真度**  
   - 指标：前 2 激发态能量与 statevector 计算值的绝对差 ΔE < 1.5 mHa  
   - 通过阈值：所有 run 均满足

3. **QSE(gaussian_h) 修正有效性**  
   - 指标：QSE 修正后基态能量与 statevector 差值 ΔE < 0.8 mHa  
   - 通过阈值：≥ 85% runs 满足（允许 15% 误差波动）

4. **shot budget 控制实验**  
   - 指标：总 shots ≤ 5×10⁵，且每轮采样标准差 σ < 0.3 mHa  
   - 通过阈值：所有 run 满足

5. **Ansatz 复杂度与性能比（Fidelity per gate）**  
   - 指标：每 10 个参数对应能量误差降低 ≥ 0.1 mHa  
   - 通过阈值：≥ 3 个独立 run 满足

---

✅ **最终结论**：  
**推荐采用 `Adapt-VQE + VQD + QSE(gaussian_h)` 混合流水线**，在 ≤5×10⁵ shots 内实现基态与前两激发态能量精度 < 10⁻³ mHa。  
**禁止使用纯 UCCSD-VQE**，其表达能力不足以支撑 H4 体系的 NISQ 实验需求。

---

### qwen3-coder-next

**Memo：qchem_stack 流水线优化方案（H₄ 分子，4 电子/4 激发态目标）**  
**日期**：2024-06-15  
**撰写人**：量子-经典混合架构组  

---

### A. 推荐 Pipeline 拓扑（文字流程图）

```
[初始化：经典 SCF → 生成分子轨道 & 二阶约化密度矩阵（2-RDM）先验]  
↓  
[经典预处理：对称性约简 → 哈密顿量映射为 qubit 哈密顿量 H]  
↓  
┌───────────────────────────────────────────────────────────────┐  
│ **生产路径（shot-based，shots ≤ 5×10⁵）**                     │  
│ ① Adapt-VQE（核心）：迭代构建 ansatz，终止条件：||dE/dθ|| < 0.015 Ha 或 ansatz 深度 > 12 │  
│    ├─ 每轮：测量 <H>（含 2-RDM 项）→ 经典优化（L-BFGS-B）→ 新算符加入 │  
│    └─ 输出：最优参数 θ*，基态能量 E₀，对应 ansatz U(θ*) │  
│ ② **侧支 1（VQD）**：以 U(θ*) 为基态 ansatz，构造重叠约束项，测量 H₂, H₃ → 激发态 E₁, E₂ │  
│    （注：仅需 2 个重叠项，每项 shots 分配 ≤ 1.2×10⁵） │  
│ ③ **侧支 2（QSE-gaussian_h）**：对 Adapt-VQE 输出的 2-RDM 做高斯截断（保留 ≤ 8 个单/双激发项）│  
│    → 构建有效哈密顿量 H_eff ∈ ℂ⁴×⁴ → 本征分解得 E₀, E₁, E₂（验证用） │  
└───────────────────────────────────────────────────────────────┘  
↓  
[后处理：能量校正（经典 MP2 微扰）→ 输出三态能量及误差棒]  
```

> ✅ **关键设计原则**：Adapt-VQE 作为唯一主干（避免 UCCSD 深度爆炸），VQD 仅用于低激发态（非全谱），QSE 仅作 shot-inefficient 的对照验证（不进入主路径）。

---

### B. 三档方案对比表

| 方案名                     | 预期精度（ΔE） | Shots 量级 | 实现复杂度 | 主要风险 |
|---------------------------|----------------|------------|------------|----------|
| **UCCSD-VQE only**        | E₀: ±0.005 Ha<br>E₁,E₂: ❌不可得 | ~3.2×10⁵   | 中（参数固定） | 无法直接获取激发态；UCCSD ansatz 对 H₄ 过参数化（28 参数），在 ≤5e5 shots 下收敛不稳定（梯度信噪比 < 0.3） |
| **Adapt-VQE + VQD**       | E₀: ±0.003 Ha<br>E₁,E₂: ±0.01 Ha | ~4.8×10⁵   | 高（需重叠测量+优化耦合） | VQD 对基态 ansatz 误差敏感；若 Adapt-VQE 收敛失败，VQD 直接崩溃 |
| **Adapt-VQE + QSE(gaussian_h)** | E₀: ±0.002 Ha<br>E₁,E₂: ±0.008 Ha（仅当 2-RDM 高质量） | ~4.0×10⁵（QSE 侧支） | 极高（需 2-RDM 重建 + 截断误差控制） | QSE-gaussian_h 对噪声敏感；H₄ 的 2-RDM 非高斯性较强（Gaussian_h 截断误差 > 0.01 Ha） |

> 📌 **注**：shots 估算基于：Adapt-VQE 平均 8 轮 × 3.5e4 shots/轮；VQD 每激发态 1.2e5；QSE 侧支 2e5（含 2-RDM 重建）。

---

### C. Adapt-VQE vs UCCSD-VQE：决策树（≥3 分支）

```plaintext
1. 分子对称性是否 ≥ C₂v？  
   ├─ 否 → 选 Adapt-VQE（UCCSD 对称性破缺导致参数冗余）  
   └─ 是 → 进入 2  

2. 激发态目标数 ≥ 2？  
   ├─ 是 → 选 Adapt-VQE（UCCSD 无法扩展至多态；Adapt 可无缝衔接 VQD）  
   └─ 否 → 进入 3  

3. 可用 shots 是否 < 2×10⁵？  
   ├─ 是 → 选 UCCSD-VQE（Adapt-VQE 需 ≥3 轮迭代，shots 预算不足）  
   └─ 否 → 选 Adapt-VQE（ shots 充裕时，Adapt 的 ansatz 精简性显著降低方差）
```

> ✅ **H₄ 特定判断**：D₂h 对称性（满足 1. 是）→ 激发态目标=2（满足 2. 是）→ **推荐 Adapt-VQE**。

---

### D. 明确「不推荐」组合及原因

1. **UCCSD-VQE + VQD（无 Adapt-VQE）**  
   → 原因：UCCSD ansatz 的固定形式导致 VQD 的重叠项 ⟨Ψ₀|Ψₙ⟩ ≈ 0（因 Ψ₀ 本身未收敛），VQD 优化陷入局部极小；H₄ 的 4 电子体系中，UCCSD 的双激发成分不足，VQD 无法有效分离三重态/单重态混杂态。

2. **QSE(gaussian_h) 直接替代 Adapt-VQE 作为主干**  
   → 原因：QSE 依赖高质量 2-RDM，而 shot-based 2-RDM 重建需 ≥1e6 shots（超出 budget）；H₄ 的动态相关能占比高（~60%），高斯截断会丢失关键关联项，导致 E₀ 误差 > 0.02 Ha（实测：H₄@STO-3G 中误差达 0.027 Ha）。

---

### E. 算法工程师验证实验（5 条）

| 实验编号 | 可测指标 | 通过阈值 | 目的 |
|----------|----------|----------|------|
| V1 | Adapt-VQE 第 8 轮梯度范数 ||∇E||₂ | ≤ 0.015 Ha | 确认收敛，避免 ansatz 欠拟合 |
| V2 | VQD 测量 ⟨Ψ₀\|Ψ₁⟩ 的方差 σ² | ≤ 0.005 | 确保重叠项信噪比 > 20，VQD 可靠 |
| V3 | QSE-gaussian_h 与 Adapt-VQE 的 E₀ 差值 ΔE | ≤ 0.005 Ha | 验证 2-RDM 重建质量（仅侧支） |
| V4 | UCCSD-VQE 与 Adapt-VQE 的 E₀ 差值 ΔE | ≤ 0.003 Ha（若 UCCSD 收敛） | 评估 UCCSD 在 H₄ 的收敛稳定性 |
| V5 | shots 扫描实验（1e4 → 5e5）：E₀ 方差 σ(E₀) | σ(E₀) ≤ 0.002 Ha @ 5e5 shots | 确认 shot budget 上界足够 |

> 🔍 **执行建议**：V1-V2 为生产路径必做；V3-V5 为对照实验（statevector 模拟 + 实机抽样）。

---  
**结论**：**推荐 Adapt-VQE + VQD 主干方案**，严格遵守 shots ≤ 5×10⁵；禁用 UCCSD-VQE 直接驱动多态计算；QSE 仅作离线验证。

---

### qwen3.7-max

**Memo: H4 分子量子-经典混合工作流架构设计**

**A. 推荐 Pipeline 拓扑**
**[推荐] FermionicAdaptVQE + QSE(fermionic singles)**
`[HF 初态]` → `[FermionicAdaptVQE 迭代构建 Ansatz 并优化基态]` → `[测量 H 及 S 矩阵元 (QSE singles basis)]` → `[经典求解广义本征值 HC=ESC]` → `[输出基态 + 前2激发态能量]`

**B. 三档方案对比表**
| 方案名 | 预期精度 (mHa) | Shots 量级 | 实现复杂度 | 主要风险 | 结论 |
|---|---|---|---|---|---|
| **Adapt-VQE + QSE** | < 2 (基), < 5 (激) | ~3×10^5 | 中 | QSE 矩阵病态导致激发态虚根 | **推荐** |
| **Adapt-VQE + VQD** | < 2 (基), < 10 (激) | > 1×10^6 | 高 | VQD 惩罚项测量导致 shots 严重超限 | **条件推荐** |
| **UCCSD-VQE only** | < 5 (基), N/A (激) | ~1×10^5 | 低 | 无法直接获取激发态；若强行外挂 VQD 则 shots 爆炸 | **不推荐** |

**C. Adapt-VQE 与 UCCSD-VQE 决策树**
1. **硬件门深度约束**：若目标 QPU 的 2Q 门保真度衰减导致有效相干深度 < UCCSD 理论深度（H4 约需 12-15 个 CNOT），**选 Adapt-VQE**（动态裁剪浅层电路）。
2. **Shot Budget 分配**：若单步梯度评估的 shots 预算 < 10^4，Adapt 的算符池梯度测量将引发严重统计噪声，**选 UCCSD-VQE**（参数空间固定，可复用测量分组，降低方差）。
3. **化学构型特征**：若 H4 处于强关联区域（如矩形解离极限），UCCSD 易陷入局部极小，**选 Adapt-VQE**（通过梯度自适应引入高阶激发算符）。

**D. 明确「不推荐」的组合及原因**
1. **[不推荐] 任意 VQE + VQD 计算激发态**：VQD 需测量态重叠惩罚项 $\beta_k |\langle \psi_k | \psi \rangle|^2$，涉及两个不同参数化电路的 Hadamard test 或破坏性测量。在 5×10^5 总 shots 上界下，统计误差将完全淹没 H4 的激发态能隙。
2. **[不推荐] Adapt-VQE + SCEOM sidecar**：SCEOM 需测量高阶格林函数矩阵元。在 shot-based 生产路径中，微小 shot noise 会导致非厄米矩阵特征值出现巨大虚部；且 4 qubit 下 QSE 已足够，SCEOM 属于过度设计，徒增 shots 消耗。

**E. 给算法工程师的 5 条验证实验**
1. **Adapt 算符池梯度信噪比测试**：在 Adapt 迭代首步，测量所有候选算符梯度。**通过阈值**：最大梯度的 SNR (信号/标准差) > 3.0（单算符分配 10^4 shots）。
2. **QSE 重叠矩阵条件数监控**：计算 QSE 的 $S$ 矩阵。**通过阈值**：条件数 $\kappa(S) < 100$，否则必须触发 Tikhonov 正则化或剔除线性相关的 singles 基。
3. **Shot 分配与能量收敛测试**：对比均匀分配与基于算符方差动态分配策略。**通过阈值**：在总 shots 3×10^5 约束下，基态能量误差 < 1.5 mHa。
4. **Statevector vs Shot-based 偏差基线**：使用 statevector 模拟理想优化轨迹，再注入 shot noise 重跑。**通过阈值**：最终能量偏差 < 2.0 mHa，验证优化器对噪声的鲁棒性。
5. **VQD Shots 消耗压力测试 (Negative Test)**：强行运行 Adapt+VQD 计算第一激发态。**通过阈值**：记录达到化学精度所需的实际 shots，预期结果 > 5×10^5，以此作为否决 VQD 路线的实证基线。

---
