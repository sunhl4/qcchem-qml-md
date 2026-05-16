# 密度拟合、RI‑JK 与 PySCF 中周期性 GDF 方法

本文聚焦 **Gaussian Density Fitting（GDF / 周期 RI‑JK）**的数学结构与 PySCF 实现；**更广义的 PBC 思想、Γ 与 k 点网格、驱动级对照与费米空间的 k 量子数**见姊妹篇《[周期性体系模拟：PBC、布里渊区与 Vendor platform/开源驱动对照](./周期性体系模拟_PBC_Brillouin与Vendor platform驱动对照.md)》。

---

在量子化学中，双电子排斥积分（ERI）的计算是 Hartree‑Fock（HF）和密度泛函理论（DFT）中最耗时的部分。传统方法需要直接计算四中心积分 $(ij|kl)$，其计算量随基函数数目 $N$ 呈 $O(N^4)$ 增长。对于周期性体系，这一问题更为突出，因为还要对晶格矢量求和。**密度拟合**（Density Fitting, DF），也称为**恒等分解**（Resolution of the Identity, RI），通过引入一组辅助基函数将四中心积分分解为三中心积分的乘积，从而大幅降低计算标度。**GDF**（Gaussian Density Fitting）是 PySCF 中针对**周期性高斯型轨道**（GTO）实现的一种高效 DF 方法，它同时加速 Coulomb（J）和交换（K）部分的构建，常被视为 **RI‑JK** 在周期性体系下的变体。

---

## 1. 密度拟合的基本物理思想

在 HF 或 DFT 中，Coulomb 项 $J$ 与交换项 $K$ 均可表达为双电子积分与密度矩阵的缩并：

$$
J_{ij} = \sum_{kl} D_{kl} (ij|kl), \quad
K_{ij} = \sum_{kl} D_{kl} (ik|jl)
$$

其中 $(ij|kl) = \iint \phi_i(\mathbf{r})\phi_j(\mathbf{r}) \frac{1}{|\mathbf{r}-\mathbf{r}'|} \phi_k(\mathbf{r}')\phi_l(\mathbf{r}') \,\mathrm{d}\mathbf{r}\,\mathrm{d}\mathbf{r}'$。

物理上，每一对轨道乘积 $\phi_i\phi_j$ 可视为一个“电荷密度”。DF 的核心是用一组有限的辅助基函数 $\{\chi_P\}$ 将其展开：

$$
\phi_i(\mathbf{r})\phi_j(\mathbf{r}) \approx \sum_P C_{ij}^P \, \chi_P(\mathbf{r})
$$

通过选择适当的系数 $C_{ij}^P$，使得该近似在 Coulomb 度量下误差最小。该度量由库仑算符 $\hat{V}$ 的核 $1/|\mathbf{r}-\mathbf{r}'|$ 定义，对应的拟合泛函为：

$$
\Delta_{ij} = \frac{1}{2} \iint \left[ \phi_i\phi_j - \sum_P C_{ij}^P \chi_P \right](\mathbf{r}) \frac{1}{|\mathbf{r}-\mathbf{r}'|} \left[ \phi_i\phi_j - \sum_Q C_{ij}^Q \chi_Q \right](\mathbf{r}') \,\mathrm{d}\mathbf{r}\,\mathrm{d}\mathbf{r}'
$$

求极值可得：

$$
C_{ij}^P = \sum_Q (ij|Q) [\mathbf{V}^{-1}]_{QP}
$$

其中三中心积分 $(ij|Q) = \iint \phi_i(\mathbf{r})\phi_j(\mathbf{r}) \frac{1}{|\mathbf{r}-\mathbf{r}'|} \chi_Q(\mathbf{r}') \,\mathrm{d}\mathbf{r}\,\mathrm{d}\mathbf{r}'$，辅助基的 Coulomb 矩阵 $V_{PQ} = \iint \chi_P(\mathbf{r}) \frac{1}{|\mathbf{r}-\mathbf{r}'|} \chi_Q(\mathbf{r}') \,\mathrm{d}\mathbf{r}\,\mathrm{d}\mathbf{r}'$。

代入双电子积分即得核心分解式：

$$
(ij|kl) \approx \sum_{P,Q} (ij|P) [\mathbf{V}^{-1}]_{PQ} (Q|kl) \tag{1}
$$

此即 **RI 近似**，将四中心积分转化为三中心积分与一个与轨道无关的辅助矩阵的逆的乘积，标度由 $O(N^4)$ 降为 $O(N^3)$（若辅助基数目 $N_{\text{aux}} \propto N$）。

---

## 2. RI‑JK：同时加速 Coulomb 与 Exchange

利用 (1) 式可直接构建 $J$ 矩阵，但构建 $K$ 矩阵时需要对交换积分 $(ik|jl)$ 操作。若直接使用 (1) 式，则 $K_{ij} = \sum_{kl} D_{kl} \sum_{P,Q} (ik|P) [\mathbf{V}^{-1}]_{PQ} (Q|jl)$，其实现虽有加速但不够简洁。更高效的做法是对 (1) 式进行 Cholesky 分解或对称正交化：

$$
\mathbf{V} = \mathbf{L}\mathbf{L}^T, \quad
B_{ij}^P = \sum_Q (ij|Q) [\mathbf{L}^{-T}]_{QP}
$$

则

$$
(ij|kl) \approx \sum_P B_{ij}^P B_{kl}^P \tag{2}
$$

此时 $J$ 和 $K$ 都可利用 $B$ 张量高效构建：

$$
J_{ij} = \sum_P B_{ij}^P \sum_{kl} B_{kl}^P D_{kl}, \quad
K_{ij} = \sum_{P,k} B_{ik}^P \sum_{l} B_{jl}^P D_{kl}
$$

对于 Coulomb 项，可先收缩密度矩阵与 $B$，形成中间量再乘以 $B$；对于交换项，则需要分步对指标求和。通过 (2) 式的分解，Coulomb 与 Exchange 均被加速，这就是 **RI‑JK** 的精髓。在分子体系中，RI‑J 与 RI‑JK 常常分别实现，而 PySCF 中的 GDF 在周期性框架下同时处理 J 与 K，可视为周期性 RI‑JK。

---

## 3. 周期性体系中的 GDF 数学推导

考虑三维周期性体系，基函数为周期性高斯函数构成的 Bloch 轨道：

$$
\phi_{\mu}^{\mathbf{k}}(\mathbf{r}) = \sum_{\mathbf{R}} e^{i\mathbf{k}\cdot\mathbf{R}} \chi_{\mu}(\mathbf{r} - \mathbf{R})
$$

其中 $\chi_\mu$ 是晶胞内的原子基函数，$\mathbf{R}$ 为晶格矢量，$\mathbf{k}$ 为第一 Brillouin 区的波矢。双电子积分在 Bloch 基下变为：

$$
(\mu\nu|\lambda\sigma)^{\mathbf{k}_i\mathbf{k}_j\mathbf{k}_k\mathbf{k}_l} = \sum_{\mathbf{R}_j\mathbf{R}_k\mathbf{R}_l} e^{-i\mathbf{k}_j\cdot\mathbf{R}_j} e^{i\mathbf{k}_k\cdot\mathbf{R}_k} e^{i\mathbf{k}_l\cdot\mathbf{R}_l} (\mu \mathbf{0},\nu \mathbf{R}_j | \lambda \mathbf{R}_k, \sigma \mathbf{R}_l)
$$

其中 $\mathbf{0}$ 代表中心晶胞。直接计算此四中心、无界格点求和的积分极为昂贵。

**GDF 的周期性推广**：引入一组辅助基函数 $\{\chi_P\}$，同样做晶格平移，定义 Bloch 辅助函数：

$$
\chi_P^{\mathbf{k}}(\mathbf{r}) = \sum_{\mathbf{R}} e^{i\mathbf{k}\cdot\mathbf{R}} \chi_P(\mathbf{r} - \mathbf{R})
$$

在实空间中对晶胞内的轨道乘积进行拟合：

$$
\chi_\mu(\mathbf{r})\chi_\nu(\mathbf{r}-\mathbf{R}_j) \approx \sum_P \sum_{\mathbf{R}_P} C_{\mu\nu}^{P,\mathbf{R}_P} \, \chi_P(\mathbf{r} - \mathbf{R}_P)
$$

通过最小化 Coulomb 误差（同样考虑周期性晶格求和），可得到三中心积分与辅助基 Coulomb 矩阵的逆。由于平移对称性，最终在 $\mathbf{k}$ 空间得到简洁的表达：

$$
(\mu\nu|\lambda\sigma)^{\mathbf{k}_i\mathbf{k}_j\mathbf{k}_k\mathbf{k}_l} \delta_{\mathbf{k}_i+\mathbf{k}_j,\mathbf{k}_k+\mathbf{k}_l} \approx \sum_{P,Q} (\mu\nu|P)^{\mathbf{k}_i\mathbf{k}_j} \left[\mathbf{V}^{\mathbf{k}_i+\mathbf{k}_j}\right]^{-1}_{PQ} (Q|\lambda\sigma)^{\mathbf{k}_k\mathbf{k}_l}
$$

其中三中心积分 $(\mu\nu|P)^{\mathbf{k}_i\mathbf{k}_j}$ 只涉及两个 Bloch 轨道和一个辅助函数，且动量守恒体现在 $\mathbf{k}_i+\mathbf{k}_j$ 一致；$\mathbf{V}^{\mathbf{k}}$ 是辅助基在 $\mathbf{k}$ 空间的 Coulomb 矩阵。

通过对称正交化 $\mathbf{V}^{\mathbf{k}} = \mathbf{L}^{\mathbf{k}}(\mathbf{L}^{\mathbf{k}})^\dagger$，得到与 (2) 类似的分解：

$$
(\mu\nu|\lambda\sigma)^{\mathbf{k}_i\mathbf{k}_j\mathbf{k}_k\mathbf{k}_l} \approx \sum_P B_{\mu\nu}^{P}(\mathbf{k}_i,\mathbf{k}_j) B_{\lambda\sigma}^{P}(\mathbf{k}_k,\mathbf{k}_l)^*
$$

其中 $B_{\mu\nu}^{P}(\mathbf{k}_i,\mathbf{k}_j) = \sum_Q (\mu\nu|Q)^{\mathbf{k}_i\mathbf{k}_j} [(\mathbf{L}^{\mathbf{k}_i+\mathbf{k}_j})^{-1}]_{QP}$。

这样，所有需要的 J 和 K 的构建均可在 $\mathbf{k}$ 空间用张量收缩完成，避免了直接的四中心格点积分，同时利用了辅助基的平移对称性大幅压缩计算量。

---

## 4. 弥散 GTO、Bloch 求和与线性依赖（overlap 病态、`exp_to_discard`）

在启用 GDF/RI‑JK **之前**，周期高斯基必须先能在 $\mathbf{k}$ 点上形成数值良态的重叠矩阵 $S(\mathbf{k})$。**「越过边界」在这里首先是线性代数用语**：基的 Gram 矩阵近乎奇异（列近似线性相关），而不是单纯的「原子画出元胞图像」。

**Bloch 组合**（与 §3 记号一致）：晶胞内局域 AO $\chi_\mu$ 经平移与相位加权为

$$
\phi_{\mu}^{\mathbf{k}}(\mathbf{r})=\sum_{\mathbf{R}} e^{i\mathbf{k}\cdot\mathbf{R}}\,\chi_{\mu}(\mathbf{r}-\mathbf{R}-\boldsymbol{\tau}_\mu)\,.
$$

对每个 Gauss **原语** $\propto |\mathbf{r}-\mathbf{v}|^{\ell}\exp(-\zeta|\mathbf{r}-\mathbf{v}|^2)$，**$\zeta$ 越小越弥散**；在多套 $\mathbf{R}$ 副本上积分时，与 §3 中 Bloch $\phi_{\mu}^{\mathbf{k}}$ **同样的机制**会带来：**不同平移像在可积区域上高度重叠** $\Rightarrow$ $S_{\mu\nu}(\mathbf{k})$ 的多个列（行）几乎成比例 $\Rightarrow$ **极小本征值** $\lambda_{\min}(S)\to 0$ $\Rightarrow$ 条件数 $\kappa(S)=\lambda_{\max}/\lambda_{\min}$ **极大**。于是广义本征问题

$$
\mathbf{H}(\mathbf{k})\mathbf{c}=\varepsilon\,\mathbf{S}(\mathbf{k})\mathbf{c}
$$

以及对 $S$ 的 Cholesky/因子分解在浮点意义下变得不可靠，**SCF 与下游 GDF 都会建立在这种坏基上**（若连 overlap 都未稳住，谈拟合加速为时过早）。二维 **Slab**、面内 $L_x,L_y$ **偏小**时常最先在此步暴露问题。

**`exp_to_discard`**：在数值上丢弃指数 $\zeta$ 低于阈值的原语分量，等价于砍掉「在空间上延展过远」、在当前格矢精度下会先搞坏 Gram 矩阵的自由度，从而在**精度 vs 数值稳定**之间做折中（金属、隙间、氢键型长程细节往往依赖弥散函数，需在更大元胞或更严格积分控制下再行加回）。

图示与推导（KaTeX + SVG，含因果链简图）：仓库内 **`examples/artifacts/pbc_diffuse_linear_dependence.html`**（可与本文对照阅读）。

---

## 5. PySCF 中 GDF 的实现特点

PySCF 的 `pbc.df.GDF` 类专为二维/三维 PBC 下的高斯型轨道设计，核心步骤如下：

1. **辅助基生成**：用户可指定辅助基组（如 `'weigend'`、`'cc-pVDZ-jkfit'`），或程序根据轨道基组自动生成。辅助基同样为高斯函数，分布在原子上。
2. **实空间晶格积分**：计算三中心积分 $( \mu \mathbf{0}, \nu \mathbf{R} | P \mathbf{R}')$ 以及辅助基 Coulomb 矩阵 $V_{P\mathbf{0}, Q\mathbf{R}}$。通过考虑晶胞的近邻截断（如 `cell.precision` 控制）和利用高斯函数的局域性，大幅度减少积分格点数。
3. **傅里叶变换到 $\mathbf{k}$ 空间**：对上述积分进行 Bloch 相位求和，得到各 $\mathbf{k}$ 点的 $(\mu\nu|P)^{\mathbf{k}}$ 和 $\mathbf{V}^{\mathbf{k}}$。
4. **正交分解**：对各 $\mathbf{k}$ 点进行 Cholesky 分解或求逆，构造 $B^{\mathbf{k}}$ 张量。
5. **J/K 构建**：在 DFT 或 HF 迭代中，使用 $B^{\mathbf{k}}$ 张量高效收缩密度矩阵，计算 Coulomb 与交换势。对于杂化泛函，GDF 同时加速 J 和 K 部分，这是它与纯 RI‑J（如 `pbc.df.FFTDF` 仅加速 J）的本质区别。

此外，GDF 充分考虑了时间反演对称性、晶格对称性以减少存储和 FLOPs，并支持解析梯度和非绝热处理，是 PySCF 中周期性高斯基计算的首选 DF 方案之一。

---

## 6. 计算复杂度与加速效果

- 直接四中心积分：$O(N^4)$（分子）或 $O(N_k^2 N^4)$（周期性），其中 $N_k$ 是 k 点数目。
- GDF：三中心积分计算 $O(N^2 N_{\text{aux}})$，矩阵求逆 $O(N_{\text{aux}}^3)$，J/K 构建 $O(N^2 N_{\text{aux}})$ 至 $O(N_k N N_{\text{aux}}^2)$。通常 $N_{\text{aux}} \approx 3\sim 5 N$，故整体标度降为 $O(N^3)$ 或更低。
- 实际加速：例如对于中等大小晶胞（数百个基函数），GDF 比解析四中心积分快 1~2 个数量级，内存占用也显著减少。

---

## 7. 使用场景与限制

**适用场景**：

- 周期性 **HF** 和**杂化 DFT**（如 HSE06、PBE0）的计算，特别是交换部分占比大时，GDF 的 RI‑JK 加速优势明显。
- 中等大小的基组（如 cc-pVDZ、def2-SVP），此时辅助基“拟合误差”极小，能量误差通常 $< 10^{-4}$ Hartree/atom。
- 二维材料、表面模型、分子晶体等 **2D/3D PBC** 系统。PySCF 的 GDF 对 2D 系统额外优化了长程 Coulomb 求和。
- 后处理性质（如能带、态密度）的快速计算。

**局限性**：

- **数值与前处理**：极富弥散的 GTO 或过小的平面内 slab 胞常使重叠矩阵 $S(\mathbf{k})$ 病态；需调节 `exp_to_discard`、扩大元胞、`cell.precision` 等与 §4 一致的策略，再行 GDF／SCF。**图示页**：`examples/artifacts/pbc_diffuse_linear_dependence.html`（相对于仓库根目录）。
- 需要额外的辅助基组；对于非常大基组（如 cc-pV5Z），辅助基也会变得很大，优势减弱，且拟合误差可能增加。
- 内存需求与辅助基数目直接相关，超大晶胞时 $B$ 张量存储可能成为瓶颈。
- 对于仅需纯 DFT（非杂化）的 Coulomb 矩阵，PySCF 还提供了 `FFTDF`（基于快速傅里叶变换的密度拟合）往往更高效，此时 GDF 可能不是最佳选择。

**在 PySCF 中启用 GDF**：

```python
from pyscf.pbc import dft, gto
cell = gto.Cell()
cell.atom = ...
cell.basis = 'gth-dzvp'
cell.pseudo = 'gth-pade'
cell.a = ...
cell.build()

mf = dft.KRKS(cell, kpts=cell.make_kpts([2,2,2]))
mf.df = 'GDF'            # 使用 Gaussian 密度拟合
mf.auxbasis = 'weigend'  # 辅助基组
mf.kernel()
```

对于常规杂化泛函，GDF 会自动应用 RI‑JK 分解。

---

## 8. 总结

GDF 充分利用了密度拟合的数学结构，将周期性高斯轨道下的双电子积分转化为三中心量与辅助基 Coulomb 矩阵的逆的乘积，实现了对 Coulomb 和交换构建的同步低标度加速。它是 RI‑JK 在 PBC 框架内的天然延伸，也是 PySCF 中最成熟、稳健的周期性 DF 方法之一，为中等基组、二维/三维材料的杂化泛函模拟提供了高效途径。