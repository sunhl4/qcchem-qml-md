# 二次量子化读表：Fock 态与费米哈密顿量（对接 InQuanto-PySCF 叙事）

教程或调试输出里常把电子体系写成 **福克态（占据数）+ 费米子哈密顿量（产生/湮灭算符串）**。本文把这类表格按块拆开，便于对照 [InQuanto-PySCF 量子问题对照](./inquanto-pyscf-problem-analog.md) 与 `qchem_stack` 的 ``get_restricted_active_space_quantum_problem`` 输出。

---

## 1. 轨道标签怎么读

- `0a`, `0b`, `1a`, `1b` 表示 **4 个自旋轨道**。
  - 数字 `0`, `1`：**空间轨道**编号（如 0 成键、1 反键）。
  - 后缀 `a` / `b`：自旋 **α** / **β**。

表头或算符里若写作 `F0`…`F3`，通常与自旋轨道索引一一对应，例如：

| 算符 | 自旋轨道 |
|------|----------|
| `F0` | `0a` |
| `F1` | `0b` |
| `F2` | `1a` |
| `F3` | `1b` |

- `Fi^`：**产生算符** \(a_i^\dagger\)（在该自旋轨道上放一个电子）。
- `Fi`：**湮灭算符** \(a_i\)（从该轨道取走一个电子）。

具体字符串与程序的 **轨道排序约定**绑定；若以 OpenFermion / 本仓库的 ``integral_convention`` 为准，读表前先确认索引顺序是否与积分一致。

---

## 2. Fock state：占有数向量

示例：

```
Fock state:
 0 0a         :  1    
 1 0b         :  1    
 2 1a         :  0    
 3 1b         :  0    
```

含义：

- 每个自旋轨道一行：**占据数** 0 或 1（费米子 Pauli 排斥）。
- 上例共 **2 个电子**：都占据空间轨道 `0`，且 α、β 各一 → **闭壳层单重态**。
- 这是典型的 **HF 参考态**；极小基 **H₂ / STO‑3G** 常出现 **4 自旋轨道、2 电子** 的完全相同模式。

与本仓库：`RestrictedActiveSpaceQuantumProblem` 中的 **HF / 占据信息**最终会参与构造 ``hartree_fock_state_jw``（Jordan–Wigner 之后的比特串振幅）；Fock 表是经典侧“占轨图”的直译。

---

## 3. Hamiltonian 表：标准二次量子化形式

表格在实现上就是

\[
\hat{H} = h_0 + \sum_{p,q} h_{pq}\, a_p^\dagger a_q + \frac{1}{2}\sum_{p,q,r,s} g_{pqrs}\, a_p^\dagger a_q^\dagger a_s a_r
\]

的一行一项展开：**系数 × 算符串**（二体项的 **1/2** 有的程序并入系数，有的单独写进公式，读数时注意文档说明）。

### 3.1 常数行（无算符）

例如单独一列系数、**Term 为空**：对应 \(h_0\)（常含 **核排斥** 与正规序/能量零点带来的常数偏移），不含产生湮灭算符。

### 3.2 单体项：`Fp^ Fq`

- **`Fp^ Fp`**：在位占据数算符 \(n_p = a_p^\dagger a_p\)，系数即该轨道的有效单粒子矩阵元（动能 + 核吸引 + 平均场等折叠后的结果，视哈密顿定义而定）。
- 若 **`Fp^ Fq`** 且 \(p \neq q\)：**单粒子耦合**（在非基表象下）。

自旋限制的体系里，对称的 **\(h_{pq}\)** 往往在 `0a`/`0b`、`1a`/`1b` 上显示相同数值，这是在提示 **自旋对称** 仍存在。

### 3.3 双体项：四个 `F…`

形如 **`Fp^ Fq^ Fr Fs`** 的排序，在量子化学里常对应 **chemist notation** 下的双电子积分经 Wick 定理/normal ordering 后在费米算符基的展开。**不要**仅从字符串目测 `(pq|rs)` —— 要与具体软件（PySCF、OpenFermion、InQuanto 导出格式）确认 **克罗内克顺序**与 **Hermitian/symmetry 打包**。

直觉上可分两族（教学用，非替代码）：

- **“同对湮灭再同对产生”**（如 `F1^ F0^ F0 F1`）：常对应 **直接库仑型**贡献，在闭壳层参考下对能量与激发分析都很重。
- **指标更“交叉”的四算符串**：往往联系 **交换**或 **双激发 / 双空穴过程**；在 FCI、CC、量子模拟里决定相关能。

若发现与教科书 `(pr|qs)` 脚标对不上，优先查该程序的 **OpenFermion `InteractionOperator` 约定**（本仓库对齐 Tangelo / ``qchem_stack.chem.integral_convention``）。

---

## 4. 整张图对应什么分子？

当出现 **4 自旋轨道、2 电子、闭壳占据最低空间轨道** 时：

- **化学图像**：两座 H 的极小基组合成一个成键、一个反键；基态主要在成键轨道上填一对 opposite spin。
- **计算图像**：常用于教学或 smoke test 的 **H₂ STO‑3G** FCI/QC 链路。

哈密顿表里同时出现常量、对角单体、整块双体系数，就是从 **整数（或 DF）哈密顿量**到 **第二次量子化** 的标准输出——后续 **Jordan–Wigner / Bravyi–Kitaev** 仅改变 **qubit 表象**，不改变 **费米代数**这层含义。

---

## 5. 与 `qchem_stack` / InQuanto 教程的衔接

| 你在输出里看到的 | 在开源镜像里常对应 |
|------------------|-------------------|
| Fock-style 占据 | HF Occupation → ``hartree_fock_state_jw`` 之前的信息；或 CAS 活性电子排布 |
| 费米哈密顿表格 | ``InteractionOperator`` 或 ``df()``/`df_mo_integrals()` 展平视角 |
| 自旋轨道数 | \(2\times\) 活性 **空间** 轨道数（RHF/RKS 限制性路径） |

入口仍见：[InQuanto-PySCF 叙事对照](./inquanto-pyscf-problem-analog.md) 第一节（``get_restricted_active_space_quantum_problem``）。

---

## 6. 速查小结

| 符号 / 区块 | 含义 |
|-------------|------|
| Fock state | 各自旋轨道的占据数列表；定下参考行列式。 |
| `Fi^`, `Fi` | 产生、湮灭算符。 |
| 常数系数行 | \(h_0\)（含核排斥等）。 |
| `Fp^ Fq` | 单体（含在位占据）。 |
| 四算符串 | 双 electron 相互作用在费米子算符基的项。 |

若你能提供 **确切程序名与版本**（如 PySCF + OpenFermion、Quantinuum 教程某单元的 `display`/`df`），可把某一行的 **克罗内克脚标与本仓库 ``integral_convention``** 做逐行对齐；上述内容刻意保持 **表象无关**的阅读框架。
