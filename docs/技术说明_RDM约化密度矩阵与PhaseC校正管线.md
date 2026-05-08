# RDM（约化密度矩阵）技术说明与 Phase C 校正管线

本文档说明 **Reduced Density Matrix（RDM，约化密度矩阵）** 的定义、常用推导骨架、与能量的关系，以及在「量子测量 + 经典高阶校正」链路中的主要作用；并与仓库路线图中 **Phase C（中长期）：RDM 驱动的高阶混合后处理** 对齐。

---

## 1. Phase C 路线图摘要（原文要点）

**Phase C（中长期）：RDM 驱动的高阶混合后处理**

1. 定义 `RDMBundle` 公共类型（1/2/3/4-RDM、来源、轨道基信息）。
2. 引入 NEVPT2/AC0 风格的校正插件接口（先做占位与数据流，后做数值细化）。
3. 在 parity 报告中新增「RDM correction readiness」维度。

**收益**：形成与 InQuanto 思路接近的「量子测量 + 经典高阶校正」能力链。

---

## 2. RDM 是什么（简明版，行内公式用 `$...$`）

在量子化学和量子–经典混合计算里，**RDM** 指 **约化密度矩阵**：用密度算符 $\hat{\rho}$ 描述体系状态，再对不需要的自由度求迹，只保留与**电子结构 / 活性空间 / 测量可观测量**相关的信息。

- **1-RDM** $\gamma_{pq}$：单粒子信息（占据、自然轨道等），常写为 $\langle a^\dagger_p a_q \rangle$。
- **2-RDM** $\Gamma_{pqrs}$：双粒子关联，$\langle a^\dagger_p a^\dagger_q a_s a_r \rangle$，对能量贡献最直接。
- **3-RDM / 4-RDM**：更高阶的产生–湮灭算符期望值；完整 CI 理论上需要，实际多在多参考微扰（如 **NEVPT2**）或特定近似中部分使用或近似。

**来源**可以是：全 CI / CASSCF / FCI 波函数，或来自 **VQE / 量子设备** 通过测量重构的（近似）RDM。

**NEVPT2 / AC0** 一类做法：在已有参考（例如 CAS 波函数或 RDM）上，用经典多体理论做能量或性质的微扰/收缩校正；接口需要 **1/2-RDM（必要时更高阶）** 以及**轨道与活性空间定义**，因此 `RDMBundle`（阶数、来源、轨道基）是数据契约。

**与 parity**：「RDM correction readiness」报告的是：**数据是否齐备、约定是否一致、能否可靠接入校正插件**。

---

## 3. 量子态与密度算符

### 3.1 纯态与混态

- **纯态** $|\Psi\rangle$（已归一化）：可观测量 $\hat{O}$ 的期望值为 $\langle \hat{O} \rangle = \langle \Psi | \hat{O} | \Psi \rangle$。
- **混态**（统计系综）：用密度算符表示，
  $$
  \hat{\rho} = \sum_k p_k |\Psi_k\rangle\langle \Psi_k|, \quad p_k \ge 0,\ \sum_k p_k = 1,
  $$
  期望值为 $\langle \hat{O} \rangle = \mathrm{Tr}(\hat{\rho}\,\hat{O})$。

电子结构里常用 **Fermion** 体系：$\hat{\rho}$ 在选定的单粒子基（自旋轨道或空间轨道）下可引出各级 RDM。

### 3.2 从 Full Density 到「约化」

记 $N$ 电子波函数 $|\Psi\rangle$ 依赖于 $N$ 个电子坐标（或等价地在 Fock 空间中的占据构型）。**完整的** $N$-粒子信息等价于 $|\Psi\rangle\langle\Psi|$（纯态）或相应 $\hat{\rho}$。

**$p$-粒子 RDM** 的思想：只保留「任意 $p$ 个电子（或 $p$ 个产生/湮灭指标）」上的边际分布，数学上通过对 **其余** 粒子自由度求 **部分迹（partial trace）** 得到。在二次量子化语言里，等价于用产生、湮灭算符的正规序期望值来打包这些信息。

---

## 4. 二次量子化下的 RDM 定义（推导骨架）

### 4.1 单粒子基与产生/湮灭算符

选定一组正交自旋轨道 $\{\phi_p\}$，对应产生算符 $a^\dagger_p$、湮灭算符 $a_p$，满足反对易关系：
$$
\{a_p, a^\dagger_q\} = \delta_{pq}, \quad \{a_p, a_q\} = 0.
$$

### 4.2 $p$-粒子 RDM（以期望值定义）

在状态 $\hat{\rho}$ 下，定义（正规序下常见的 **RDM 元素** 约定；具体文献中对 **指标顺序** 可能有转置或符号约定差异，工程上必须在 `RDMBundle` 里**固定一种并文档化**）：

- **1-RDM**（单粒子密度矩阵元素）
  $$
  \gamma_{qp} \equiv \langle a^\dagger_p a_q \rangle = \mathrm{Tr}(\hat{\rho}\, a^\dagger_p a_q).
  $$
  矩阵形式 $\boldsymbol{\gamma}$ 为 Hermitian：$\gamma_{pq} = \gamma_{qp}^*$。

- **2-RDM**
  $$
  \Gamma_{rspq} \equiv \langle a^\dagger_p a^\dagger_q a_s a_r \rangle.
  $$
  （注意：不同教材对下标顺序写法不同；实现时需与积分 $\langle pq|rs\rangle$ 的约定配套。）

- **3-RDM、4-RDM** 类似地写为更高阶的 $\langle a^\dagger a^\dagger a^\dagger a a a\rangle$ 型期望值。

### 4.3 与「部分迹」的联系（概念式）

若把 Hilbert 空间写成 $\mathcal{H} = \mathcal{H}_A \otimes \mathcal{H}_B$，约化密度矩阵 $\hat{\rho}_A = \mathrm{Tr}_B(\hat{\rho})$。在费米子 Fock 空间中，「只对部分模式求迹」与上述产生湮灭期望值定义在适当规范下一致。详细构造属于多体物理标准内容；**对软件接口而言**，关键是：**RDM 是一组或多组张量，与轨道指标与排列约定一一对应**。

---

## 5. 能量与可观测量：RDM 的「主要作用」之一

### 5.1 二次量子化哈密顿量（分子电子结构典型形式）

在固定核、给定单电子积分 $h_{pq}$ 与双电子积分 $\langle pq|rs\rangle$（具体对称性与反对称化约定依程序而定）下，电子哈密顿量常写为：
$$
\hat{H} = \sum_{pq} h_{pq}\, a^\dagger_p a_q + \frac{1}{2}\sum_{pqrs} \langle pq|rs\rangle\, a^\dagger_p a^\dagger_q a_s a_r + E_{\mathrm{nuc}}.
$$

### 5.2 能量仅依赖 1-RDM 与 2-RDM

对任意 $\hat{\rho}$，
$$
E = \langle \hat{H} \rangle = \sum_{pq} h_{pq}\, \gamma_{qp} + \frac{1}{2}\sum_{pqrs} \langle pq|rs\rangle\, \Gamma_{rspq} + E_{\mathrm{nuc}}.
$$

因此：

- **在给定积分与轨道基下，电子能量由 $\boldsymbol{\gamma}$ 与 $\boldsymbol{\Gamma}$ 完全决定**（这是 RDM 在方法学上的核心事实之一）。
- 更高阶 RDM **不直接**出现在上述「标准两体哈密顿量」的能量公式里，但在 **多参考微扰、不完全收缩、或含更高体相互作用的模型** 中会进入。

### 5.3 自然轨道与占据

对 $\boldsymbol{\gamma}$ 做对角化得到 **自然轨道** 与 **占据数** $n_i \in [0,1]$（费米子），用于理解关联、截断活性空间、以及诊断量子/经典混合结果的合理性。

---

## 6. N-可表示性与近似 RDM

并非任意张量 $\boldsymbol{\gamma}, \boldsymbol{\Gamma}, \ldots$ 都对应某个物理 $\hat{\rho}$。**N-representability（N-可表示性）** 问题刻画「哪些 RDM 来自真实的 $N$-费米子密度算符」。实际计算中：

- **来自精确波函数**（如 FCI）的 RDM 满足完整约束集（难以全部施加）。
- **来自近似方法或有限样本量子测量**的 RDM 往往 **仅近似**满足；下游校正（NEVPT2 等）对参考质量敏感。

这对 Phase C 的含义是：`RDMBundle` 除数值外，还应能携带 **不确定性 / 对称性残差 / 与 N-representability 相关的检验摘要**，以支撑 parity 的 readiness 评分。

---

## 7. 与「量子测量 + 经典高阶校正」的结合

1. **量子侧**：通过 Pauli 分解与采样估计期望值，可重构（近似）低阶 RDM 元素或等价可观测量。
2. **经典侧**：NEVPT2、AC0 等将参考（CASSCF/FCI/噪声 VQE 等）与积分结合，给出 **相关能校正** 或改进的性质。
3. **工程接口**：`RDMBundle` 统一 **1/2/（3/4）-RDM**、**来源**（FCI / PySCF / 设备估计）、**轨道与积分约定**；插件先占位打通数据流，再细化数值与误差模型。
4. **parity**：「RDM correction readiness」可维度化为：是否具备 $\boldsymbol{\gamma},\boldsymbol{\Gamma}$、指标约定是否与哈密顿量一致、是否有关键对称性（Hermiticity、置换）、是否记录粒子数 $N$ 与活性空间维度等。

---

## 8. 符号与实现提醒（给 `RDMBundle` 设计用）

- **积分与 RDM 的指标顺序**必须一致，否则能量重组会错。
- **自旋形式**：空间轨道 vs 自旋轨道会使 $\gamma,\Gamma$ 维数与块结构不同。
- **反对称双电子积分 $[pq\|rs]$ 与化学记号 $\langle pq|rs\rangle$** 在代码中需单一来源的约定（可与仓库内 `integral_convention` 一类模块对齐）。

---

## 9. 参考文献方向（非穷尽）

- RDM 与能量公式：标准量子化学教材中「密度矩阵形式」「二次量子化」章节。
- N-representability：多体量子化学与量子信息交叉文献。
- NEVPT2 / 多参考微扰：与 CASSCF/CASCI 参考及各级 RDM 使用方式相关的方法论文。

---

*文档版本：与 Phase C 规划对齐的概念与推导骨架；具体数值模块与 parity 字段以代码与 parity 导出 schema 为准。*
