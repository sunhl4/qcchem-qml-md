# UCC 参数初始化与 Brillouin 定理：单激发梯度、优化器与本仓库注解

> **行文约定：**行内公式统一用 `$...$`；独立公式块用 `$$...$$`。

本文澄清：以 **闭壳 HF 行列式**（或其 Jordan–Wigner 计算基表示）为参考、在常规的 **粒子–空穴 UCC / UCCSD 型**参数化下，**单激发（singles）能量梯度在 HF 邻域为何常为零**；这对 **梯度法 / 拟牛顿优化**意味着什么；如何避免误区；**解析梯度与数值梯度在变分目标下的一般性成本与收敛差异**（§7）；以及如何对照本仓库 **`UCCSDVQE`** 的真实实现。

---

## 1. Brillouin 定理在变分图景里怎么说

对满足变分方程的 **RHF 单行列式** $| {\mathrm{HF}} \rangle$，**Brillouin 定理**给出（占轨 $i$，虚轨 $a$，自旋适配情形常见写法）

$$
\langle {\mathrm{HF}} | \, \hat{H} \, \hat{a}^\dagger_a \hat{a}_i \, | {\mathrm{HF}} \rangle = 0\,.
$$

在变分几何上：**HF 已对「单粒子混合」的一级能量变分封口**。若以 **反厄米单子激发生成元**

$$
\hat{A}_{ai} \equiv \hat{a}^\dagger_a \hat{a}_i - \mathrm{H.c.}
$$

做小角幺正轮换 $|\Psi(\theta)\rangle = \mathrm{e}^{\theta \hat{A}_{ai}} | {\mathrm{HF}} \rangle$，则

$$
\left. \frac{\mathrm{d} E}{\mathrm{d} \theta} \right|_{\theta=0} = 0\,.
$$

对 **所有** Brillouin 允许的 $(i\!\to\! a)$ **单激发**，在 HF 点上 **能量的首阶系数为零**。**二阶**一般非零：**能量对 $\theta^2$** 开始有曲率。因此人们常说：**HF 点对 singles 参数是「一阶钝」的自由度**，不是整条能量曲面恒为零。

---

## 2. 「梯度优化里 singles 动不了」指什么？

### 2.1 解析梯度

若你用 **参数的解析梯度**（parameter-shift / 伴随 / 分项 Pauli），在 **精确的 HF + 规范的 UCC 单激发语义**下，从零参考出发时 **singles 方向上的解析梯度常严格为零**。那么 **梯度下降**：这些坐标 **不产生一阶 descent 方向**。若优化器始终在「非常靠近 HF doubles 主导的 valley」且不引入破坏 Brillouin 的参考形变，则 **理论上 singles 可永远不被解析梯度驱使**。（与一般性 VQE 梯度讨论相较，见 §7。）

### 2.2 数值梯度与量子噪声

若优化器只靠 **能量的有限差分**近似梯度，或对能量做 **抽样估计**，则可能得到 **形式上非零的伪梯度**。这来自 **有限差分的截断偏置（步长 $\delta$）与统计噪声的叠加**，**不是推翻 Brillouin**，工程中 **非零振幅往往很小但持续存在**。  
**不要用「模拟器里 singles 有一点点动」反驳定理**——应先检查 **Jacobian 从哪里来**（§7.1）。

### 2.3 拟牛顿（BFGS / L‑BFGS‑B）

**零解析梯度方向**会令 **近似 Hessian 在这些方向上缺乏可靠曲率**，可能导致 **低效线搜索 / 误判收敛**。比「寄希望于优化器自我修复」更符合数学的做法是：**Freeze 冗余 singles 或减少参数向量维数**，避免 Hessian‑近似病态。

---

## 3. 「初值胡乱设会不会搞崩？」——必须把阶数和截断说清楚

| 论断 | 适用说法 |
|------|----------|
| **一阶不敏感** | 在 HF 附近，$\Delta E \sim O(\theta_{\mathrm{s}}^2)$ 对 singles 的典型情形成立：小扰动的 singles **不会让能量线性暴跌**。 |
| **有限大角的 singles** | **对应 occupied–virtual 混合（轨道幺正的一侧）**。在 **完备激发流形**中与重参冗余相关；但对 **截断 UCC/UCCSD**，大 singles 会与 **给定顺序下 doubles 的比特串生成元**产生 **非直观的耦合**，可导致 **Landscape 变坏**。**不建议用大随机 singles 开局**。 |

**可操作结论：**宁可 **singles 初始化全零**，或 **不显式放进 Ansatz（UCCD 思路）** / **Freeze singles**。

---

## 4. 常见工程策略（InQuanto / 通用 VQE）

1. **`θ_singles ≡ 0` 且 freeze**：删掉优化变量或等价 mask。  
2. **Ansatz = UCCD**：省掉 singles blocks。  
3. **自适应 / ADAPT**：从 pool 中选算符时仍可观察 **零梯度条目**跳过。  
4. **激发态或强简并**：换 **MCSCF / 多参考**或 **orbital‑optimized**，使 singles 的一级矩阵元不全为零时再开放 singles。

---

## 5. `qchem_stack`：**`UCCSDVQE` / `UCCSDTrotterVQE` 与上文的三点差异**

源码：`src/qchem_stack/quantum/algorithms/uccsd_vqe.py`（`UCCSDVQE` / `UCCSDTrotterVQE`）。

| 上文「教科书」图景 | **`UCCSDVQE.run`** 实际行为 |
|--------------------|-----------------------------|
| 常假定 **可对 singles 推导解析能量梯度并报给优化器** | `scipy.optimize.minimize(..., method="L-BFGS-B")` **不传 `jac`** → SciPy 对目标函数做 **有限差分近似梯度**（与 **parameter-shift** 对比见 **§7**）。故 **单次迭代子空间上「数学零梯度 singles」可被数值 Jacobian 搅动**，一般 **振幅极小**。 |
| 常假定 **从零初始化 singles** | `run()` 里 **`x0 ~ Uniform(-π, π)`（随 `seed`）** 对每个参数 **统一随机**——包含 singles：**初值字面未必为零**。若在零梯度方向上，**仍会很快显得「粘在初值邻域」。 |
| JW + 中段归一化 + 末端 **固定电子数子空间投影** | 离散化后与「纯 Gaussian 代数 Brillouin」**形式上略有差别**，但以 **闭环壳 HF 仍为经典驻点**，**定性结论不变**。 |

若要 **严格 Freeze singles**，须在 **上层**删减 `build_spin_uccsd_fermion_generators`（`src/qchem_stack/integrations/ucc_reference.py`）输出中的 singles 项，或对 `UCCSDVQE` 做 **参数 mask / doubles‑only** 补丁。当前默认 **不裁剪** OpenFermion 生成元列表。

入口配置：`quantum.variational_ansatz: uccsd`，`configs/example_h2_uccsd.yaml` / `*_trotter*.yaml`。

---

## 6. 易混点速查表

| 误读 | 正读 |
|------|------|
| 「Singles 永远不能改变能量。」 | 「**HF 点对 singles 的一级导数为零**」；大范围角 + 截断 Ansatz ⇒ **仍可改变**。 |
| 「BFGS 一定发散。」 | 常见是 **冗余维 + 低效**；首要办法 **删维 / Freeze**。 |
| 「本仓库 L‑BFGS 证明 doubles 就够。」 | **非证明**——只是 **实践经验 + 近似 FD Jacobian**；**严谨做法**仍为 **删减 singles 自由度**若你要论文级对齐 Brillouin 叙述。 |

---

## 7. 解析梯度与数值梯度：成本、噪声与收敛（VQE 一般性）

对变分能量 $E(\boldsymbol{\theta})=\langle\psi(\boldsymbol{\theta})|\hat H|\psi(\boldsymbol{\theta})\rangle$，**梯度质量**直接影响 **外层经典优化**的效率。下面把 textbook 层面的 **parameter-shift** 等与 **数值差分 Jacobian** 分开说明，并与 **§5 本仓库**的对照收口。

### 7.1 量子资源：别太急于宣称「倍数级更少电路」

对 **单列旋转型（Pauli‑generator）门参数**，标准 **parameter-shift** 对每个 $\theta_k$ 常写为 **偏移 $\pm\pi/2$ 的两次期望值**；**中心化有限差分**对每个坐标同样是 **两点**估计 $\partial_k E$。因而在 **粗略的「每梯度一轮、每坐标两次期望」账本**下，两类方法 **可先视为同阶**。真正拉开差距的典型来源是：

| 维度 | **解析（parameter-shift 等）** | **数值（有限差分近似 $\partial E$）** |
|------|----------------------------------|----------------------------------------|
| **偏置** | 对「可 shift 的单参数门」给出的导数公式与 **精确期望值模型**一致，**无 $\delta$ 截断误差** | $\delta$ 太大：高阶误差；$\delta$ 太小：噪声下 **有效信噪比崩坏**，常需 **多档 $\delta$ 扫描 / Richardson** → **隐性增费** |
| **统计误差** | 每个 shifted 电路仍须 **shots**；估计的是 **梯度真值的无偏采样**（在模型内） | 两个邻近点相减会 **放大散粒噪声**；再叠加上述偏置，**同等精度常需更多重复测量** |
| **高阶信息** | 同一框架下可系统构造 **Hessian / 高阶** 的测量分解（仍要付电路与 shots 成本，但 **结构清楚**） | 朴素 FD Hessian 往往倾向 **$O(p^2)$ 量级能量评估** 与 **更糟的噪声放大** |

**一句话：**优势更多体现在 **少试凑、无差分偏置、与拟牛顿 / 自然梯度等算法的数据结构兼容**，而不是简单记成「解析法永远少用一半电路」。

### 7.2 收敛与优化器：为什么「干净梯度」重要

1. **方向稳定性**：差分噪声会把最速下降方向写成 **锯齿状**，线搜索变差，**外层迭代膨胀**。解析公式把 **「从零期望值模型中抽出导数」** 与 **采样噪声** 分离，更易调 shots 与预处理。  
2. **零梯度与平坦方向（接 §2）**：对 Brillouin 导致的 **理论上严格的零梯度方向**，parameter-shift **期望值** 为零；数值梯度则几乎 **永远在噪声里飘着非零小量**。工程上轻则 **冗余维度上白走步长**，重则 **弄脏 L‑BFGS 累积的曲率近似**——这与 §4 的 freeze / mask 叙事一致：**知道「真零」比「看起来像噪声」更利于停准则与降维**。  
3. **高阶优化器**：BFGS、量子 Fisher / 自然梯度等把梯度 **送进矩阵更新与逆**。**信噪比差的梯度向量**在这些步骤里常被 **几何放大**，解析路线更利于 **可控的测量预算**。

以上仍须 **脚注式诚实**：「解析」消除的是 **$\delta\to 0$ 的建模偏差**，**并不**消灭 **有限 shots**；最终仍是 **蒙特卡洛精度 vs 迭代轮数** 的折中。

### 7.3 InQuanto 与 **`qchem_stack` 占位符**（勿混）

- **InQuanto**：工作流里常把 **期望值及其对参数的导数** 组织为可执行的 **Computable** 图（官方 API 中的 `ExpectationValueDerivative` 等节点以上游文档为准），便于与编译 / 后端调度 **同一套采样与 cost 模型**。  
- **本仓库**：`src/qchem_stack/protocols/computable.py` 中的 `ExpectationValueDerivative` 当前实现为 **对 `ExpectationValue.evaluate` 的中心有限差分**（默认步长 `1e-4`），**不是**生产级 parameter-shift 后端；**§5** 的 `UCCSDVQE` 亦走 **SciPy 无 `jac` 的 L‑BFGS‑B**，同样是 **经典侧数值 Jacobian** 路线。  
若你要 **论文级或硬件对齐的解析梯度 VQE**，须在 **量子侧** 实现 shift 规则或伴随法，并把 **解析 Jacobian** 显式传入优化器，而不是默认上述占位。

### 7.4 小结

- **成本账本**：对常见单参数旋转门，parameter-shift 与 **中心化两点差分**在「每坐标两次期望」粗算下 **同阶**；解析法的主要收益是 **无 $\delta$ 偏置、少试凑、高阶信息更结构化**，从而常在 **总 shots / 总外层迭代**上更省。  
- **收敛**：更干净的梯度方向有利于线搜索与 **BFGS / 自然梯度** 等；Brillouin 相关的 **真零梯度** 在解析形式下可辨识，便于 **freeze / mask**。  
- **本仓库现状**：默认 VQE / UCCSD 路径仍为 **经典数值 Jacobian 或 FD 占位**，与 InQuanto 全栈 **导数 Computable** **不对等**（§7.3）。

---

## 参阅

- 公开矩阵：`docs-site` parity — `AlgorithmVQE` + **`uccsd`**。  
- 生成元构建：`src/qchem_stack/integrations/ucc_reference.py`；parity：`docs/inquanto_public_parity_matrix.md`（`AlgorithmVQE` + `uccsd`）。  
- InQuanto 官方：`ExpectationValueDerivative` [API 锚点](https://docs.quantinuum.com/inquanto/api/inquanto/computables.html#inquanto.computables.ExpectationValueDerivative)；本站镜像 `/mirror/api/computables/classes/ExpectationValueDerivative/`。  
- 本仓库 HEA 导数占位：`src/qchem_stack/protocols/computable.py`（`ExpectationValueDerivative` · 中心差分）；VQE 入口示例：`src/qchem_stack/quantum/algorithms/vqe.py`。
