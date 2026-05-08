# 周期性体系模拟：PBC、布里渊区与 InQuanto/开源驱动对照

本文按「思想 → Bloch AO 表象 → Γ / k 网 → Roothaan 方程 → GDF（仅衔接）→ 参数与驱动对照 → `FermionSpaceBrillouin` → 小结」铺开。**GDF、`exp_to_discard`、重叠矩阵病态**的推导与图示不重复写入，请参阅《[密度拟合与周期性 GDF](./密度拟合与周期性GDF_PySCF_RI-JK.md)》及 **`examples/artifacts/pbc_diffuse_linear_dependence.html`**。

---

## 1. PBC、平移对称与布洛赫定理（单电子）

实空间周期格矢 $\{\mathbf{a}_1,\mathbf{a}_2,\mathbf{a}_3\}$ 生成 $\mathbf{R}=\sum_i n_i \mathbf{a}_i$。**单电子**在周期晶格势中具有布洛赫本征函数

$$
\psi_{n\mathbf{k}}(\mathbf{r})
= \mathrm{e}^{\mathrm{i}\mathbf{k}\cdot\mathbf{r}}\, u_{n\mathbf{k}}(\mathbf{r}),
\quad
u_{n\mathbf{k}}(\mathbf{r}+\mathbf{R}) = u_{n\mathbf{k}}(\mathbf{r}),
$$

$n$ 为能带索引，$\mathbf{k}$ 取**第一布里渊区**。**LCAO** 实现中用局域 AO $\chi_\mu$ 先做 Bloch 和：

$$
\phi_{\mu}^{\mathbf{k}}(\mathbf{r})
=\sum_{\mathbf{R}}\mathrm{e}^{\mathrm{i}\mathbf{k}\cdot\mathbf{R}}\,
 \chi_{\mu}(\mathbf{r}-\mathbf{R}-\boldsymbol{\tau}_\mu).
$$

随后在 $\{\phi_{\mu}^{\mathbf{k}}\}$ 上对给定 $\mathbf{k}$ 求解 Fock/Hamilton——与 $\psi_{n\mathbf{k}}$ 的差别主要是「基底为 AO 还是已对角化 MO」。

离散 $\mathbf{k}$ 常用 **Monkhorst–Pack**；归一权重写为 $\sum_{\mathbf{k}} w_{\mathbf{k}} = 1$。

---

## 2. Γ 点近似（$\mathbf{k}=\mathbf{0}$）

### 2.1 适用条件

大超胞、能带平缓、分子晶体占位模型，或以 **量子算法预处理**仅需单参照行列式时，**Γ** 常与连续极限差距可接受。**金属、小隙、小胞**则常不足。

Γ 的机器成本：**每个 SCF 步只对一个 $\mathbf{k}$** 组装 Fock 并求解广义本征问题。

### 2.2 Γ ≠ 孤立分子的库仑图画

$\mathbf{k}=\mathbf{0}$ 时 Bloch AO **和的内部格点相位为 1**，矩阵形状最接近「分子 Roothaan」，但电子–核–电子 Coulomb **仍是无限周期**。实现上必须使用 **Ewald / 多级格点求和** 等数值稳定化路径，不能与有限盒分子气体混谈。

**InQuanto：**`ChemistryDriverPySCFGammaRHF`。

**qchem_stack：**`chemistry_extended.pbc_kpoint_mesh` 为 `[1,1,1]` 时使用 **`pyscf.pbc.scf.hf.RHF`**；参见 **`PySCFDriver.run_pbc_rhf`** 与 **`PyscfIntegralSolver._execute_periodic_mean_field`**。

---

## 3. Monkhorst–Pack / Momentum driver

需要带色散的材料或极小原胞等场景下，需在布里渊区内显式取样。**InQuanto：**`ChemistryDriverPySCFMomentumRHF` 常以 **`nks=[n_x,n_y,n_z]`** 给定；若在二维 slab (`dimension=2`) 情形下，常在非周期方向上把 Monkhorst 分割固定在 `1`。 **qchem_stack：**YAML 键 **`pbc_kpoint_mesh`**；任一维 $>1$ 时，`pyscf_solver` 走 **`KRHF(cell, cell.make_kpts(mesh))`**。

---

## 3.1 周期 RHF 的 Roothaan 方程（各 $\mathbf{k}$）

对每个离散 $\mathbf{k}$，

$$
\mathbf{F}(\mathbf{k})\mathbf{C}(\mathbf{k})
=
\mathbf{S}(\mathbf{k})\mathbf{C}(\mathbf{k})\boldsymbol{\varepsilon}(\mathbf{k}),
$$

$$
S_{\mu\nu}(\mathbf{k})
=\langle\phi_{\mu}^{\mathbf{k}}|\phi_{\nu}^{\mathbf{k}}\rangle,
\quad
\mathbf{C}^\dagger(\mathbf{k})\mathbf{S}(\mathbf{k})\mathbf{C}(\mathbf{k})=\mathbf{I}.
$$

$\mathbf{F}(\mathbf{k})$ 内含单体、Hartree、交换及所选泛函和长程 Coulomb/`exxdiv`；**HF 或 KS 总能量**为各 $\mathbf{k}$ 上电子能对 $w_{\mathbf{k}}$ **加权后对单胞的汇聚**，再加上核相互作用。用户草稿中的显式双 $\mathbf{k}$ 遍历 ERIs 长式易受实现脚标惯例干扰，这里**不写**——手推时请对照固态量子化学教材与 **`mf.kernel()`、`mf.e_tot`** 分项。

---

## 4. GDF（`mf.df='GDF'`）

周期 Bloch 上的 $(\mu\nu|P)^{\mathbf{k}}$、$\mathbf{V}^{\mathbf{k}}$、Cholesky 与 $\mathcal{O}(N^3)$ 量级的缩放见姊妹篇 §2–§7；PySCF 片段见姊妹篇末尾代码。**要点**：HF/杂化交换昂贵，**周期 RI‑JK / GDF** 是常规加速路径；但该层建在**数值良态的 $S(\mathbf{k})$** 之上——overlap 先于 GDF 失灵，见姊妹篇 §4 与 HTML。

---

## 5. 参数：`cell`、`nks`、赝势、`exp_to_discard` vs 本仓库映射

| 教程 / PySCF | 含义 | **`qchem_stack`** |
|----------------|------|---------------------|
| `cell`（格矢 + 原子） | 周期胞 | **`pbc_cell_vectors_bohr`**（Bohr 行向量矩阵） + `molecule` |
| **`dimension`** | 二维 slab（`2`）、一维链等 | **`_make_pbc_cell` 当前未封装**——需自定义 `Cell` 或日后扩展 YAML |
| **`nks` / `make_kpts`** | k 点数 | **`pbc_kpoint_mesh`** |
| **`exp_to_discard`** | 过滤过低指数的原语 Gauss | **配置未透出**；参见姊妹篇 §4；手写 PySCF 时 `cell.build(exp_to_discard=…)` |
| 在哪个 k 上取 CAS / VQE 积分切片 | $\mathbf{k}$ 索引 | **`pbc_active_space_kpoint_index`**（Γ‑only 为 `0`） |

Γ 占位示例：**`configs/example_h2_pbc_gamma.yaml`**。

---

## 6. `FermionSpaceBrillouin`

多 $\mathbf{k}$ 时单粒子空间带 **晶体动量**量子数，可形式上写 $\bigoplus_{\mathbf{k},n,\sigma}$；产生湮灭算符常以 $(\mathbf{k},n,\sigma)$ 三联标记，相互作用必须满足 Bloch 动量守恒。**Γ‑only** 则退化为不带 k 标签的 **`FermionSpace`**。**`qchem_stack`** 开源路径上对分子主线费米/qubit 载体已闭环；周期多 $\mathbf{k}$ 与 **`FermionSpaceBrillouin`** 的闭源对齐在公开 parity 中为 **`partial`**（见 parity 矩阵、`inquanto_driver_surface`）。

---

## 7. Gamma vs Momentum（驱动选型）

| InQuanto 常见名 | 典型体系 | **`qchem_stack`** | 产出 |
|-----------------|----------|-------------------|------|
| `…GammaRHF` | slab 大胞、Γ 足够准确 | **`pbc_kpoint_mesh`** 全 `1` | **`RHF` @ Γ**，维数最小 |
| `…MomentumRHF` | 金属、窄隙、必修色散 | 非平凡 **mesh** | **`KRHF`**，多 $\mathbf{k}$ 加权总能 |

量子侧仍映射 **Jordan–Wigner / Bravyi–Kitaev**；自由度规模大致随「自旋轨道数 × $\mathbf{k}$ 点数」增长。

---

## 8. 教学：原子链 vs「二原子」最小胞

**(A)** 单胞内含一个氢：**晶格常量** \(L\) 即为沿链方向的周期长度；可取 **`pbc_kpoint_mesh = [n_k, 1, 1]`**（若 \(y,z\) 取大方盒以降低映像耦合）离散 $\varepsilon_n(k)$。

**(B)** 单胞内含**两个氢**的二聚最小胞：**键长** \(d\)，周期长度 \(L\) 满足 \(d < L\)（最短平移为长度 \(L\) 的矢量）；同样在沿周期方向设定 Monkhorst 网离散能带。**本仓库**：将 **`example_h2_pbc_gamma.yaml`** 中 mesh 改为 **`[4,1,1]`** 并保持 **`scf.method=RHF`**，在安装 **`pyscf.pbc`** 的环境下即走 **`KRHF`** 分支——与 Γ-only 示例仅差 k 取样策略。

---

## 9. 参阅

| 文件 |
|------|
| 《[密度拟合与周期性 GDF](./密度拟合与周期性GDF_PySCF_RI-JK.md)》 |
| 《[技术分析 · InQuanto PySCF vs 原生](./技术分析_InQuanto_PySCF_vs_原生PySCF_及工程借鉴.md)》§3.4 |
| **`examples/artifacts/pbc_diffuse_linear_dependence.html`**（相对于仓库根目录）|

**与用户草稿之比**：校正布洛赫括号；去掉易被脚标惯例误读的 HF 双 $\mathbf{k}$ 总长显式公式，改为对齐 PySCF **`mf`** 能量分解；写明 **`dimension` / `exp_to_discard`** 在当前 `qchem_stack` YAML 中**未全盘透出**的工程事实。
