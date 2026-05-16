# 活性空间指定与 AVAS：理论、公式推导与工程实践（Vendor platform 教程对照）

> **行文约定：**行内公式用单美元 `$...$`；行间独立公式块用双美元 `$$...$$`。

本文从**二次量子化与能量划分**出发，系统说明 **为何要截断 Hilbert 空间**、如何在 **HF 分子轨道（MO）基**中用 **`frozen` / FromActiveSpace / AVAS`** 选定活性自由度，并结合 **Quantinuum Vendor platform‑PySCF 教程范例**给出分子图像解读；末节对照 **`qchem_stack`** 中与活性空间相关的**真实能力与诚实边界**。与 Fock 表占位列的读法可参考：`docusaurus-site/docs/guide/chemistry-and-embedding.md`（站内 `/guide/chemistry-and-embedding`，含二次量子化读法小节）。

---

## 1. 问题设定：从全 Hilbert 空间到活性子空间

### 1.1 全空间中电子哈密顿量的二次量子化（复习）

在给定一组单粒子基底（常为自旋轨道 $\{p,q,\ldots\}$）下，$N$ 电子哈密顿量写为

$$
\hat{H}
= \sum_{pq} h_{pq}\, a^\dagger_p a_q
\,+\,
\frac12 \sum_{pqrs} \langle pq|rs\rangle\, a^\dagger_p a^\dagger_q a_s a_r
\,+\,
E_{\mathrm{nuc}},
$$

其中 $h_{pq}$ 与 $\langle pq|rs\rangle$ 在选定基底下由量子化学程序（如 PySCF）生成，具体指标约定取决于 **chemist / physicist** 与 reorder（本仓库对齐 OpenFermion/Tangelo：`integral_convention`）。

**完备基**下对角化等价于 Full CI，基函数数目稍大即可使 **Hilbert 维数 $\binom{M}{N_{\alpha}}\binom{M}{N_{\beta}}$**（自旋适配时另一套计数）爆表，因而在 **CASCI/VQE/MCSCF** 上必须截取**活性子空间**。

### 1.2 「冻结」的理想化代数图像

将全部自旋轨道划成三组（概念上）：**冻结芯（inactive core） / 活性（active） / 冻结虚（inactive virtual）**。若芯轨道在求解相关问题时**始终保持双占据**（RHF‑closed shell 图景），可将芯电子单体+双体能与核相互作用并入**恒定能量项** $E_{\mathrm{core}}$，再在对角上移中吸收到有效哈密顿量，得到**仅限活性自由度**的有效算符 $\hat{H}^{\mathrm{(act)}}$。

下面这句话里的两个短语可以拆开理解：

- **「求解相关问题」**：指 **HF 完成之后**要做的 **电子相关**计算——例如 **CASCI/CASSCF、截断 CI、某些多体微扰步骤**——在这些步骤里波函数不再是单个 HF 行列式，而（至少在活性部分）可以是 **若干 Slater 行列式的叠加**。
- **「始终保持双占据」**：指被标成 **inactive core** 的那些 **空间轨道**在变分/展开的意义下 **永远不能改占据数**。在闭壳图景里即：**每根这样的空间轨道上始终各有一个 $\alpha$ 与一个 $\beta$ 电子**——CI 展开中 **不允许**包含「从芯轨道把电子激到活性或虚轨」的行列式，也不允许芯上出现 **空穴**或 **超过双占**的非法占据。形式上，总波函数常写成 **$\Phi_{\mathrm{core}}\otimes\Psi_{\mathrm{act}}$**：**$\Phi_{\mathrm{core}}$** 固定在 HF 给的闭壳芯因子上，只有 **$\Psi_{\mathrm{act}}$**（活性电子在活性轨道上的组合）在变。

这样做的化学动机：深芯电子 **激发能极高**，对你关心的 **价键/化学反应曲面**贡献通常极小；把它们锁在 HF 双占上可以 **巨幅削减 CI 基底规模**。极限对立面是 **full CI / 芯层相关 / 电离芯**等问题：那时就不应再把芯当作「永恒双占据」——需要更大的活性空间或非冻结芯方法。

严格构造需投影算符或对芯空间求迹；工程上 **`frozen` 语义**等价于：**在后续的 Fock 空间/`FermionSpace`构造中不再为冻结轨道列出独立产生/湮灭自由度**——它们在 HF 水平上「锁死」，相关试探波函数不改变其占据图案。

这不是说物理上忽略了芯电子：而是把其效应对活性电子的势能场与 **能量零点**并入 **`energy_core` / 常数项**（PySCF **CASCI `get_h1eff`** 返回的 `e_core` 即含此类折叠；见本仓库 `active_space_casci_raw_blocks` 文档串）。

---

## 2. Hartree–Fock 参考与 Fock 态打印

### 2.1 RHF 行列式作为参考向量

闭壳 HF 给定 **$N_{\mathrm{elec}}/2$ 个占据空间轨道** $\{ \psi_i \}$，每项自旋双倍。其二阶量子化解为 **Vacuum $\lvert \mathrm{vac}\rangle$**，上填入 **occupied 自旋轨道**上的产生算符序列；Vendor platform 的 `print_state` 本质是 **所选 `FermionSpace`的一组有序自旋模式**各自 **占据数 $n_p\in\{0,1\}$**。

教程中 **H₂O / 6‑31G** 第一幅长表：**10 对（20 电子）在低能 MO 填满**，对应 **$N=10$ 闭壳**。后续 **截断活性后**仅剩 **8 条「模式」**：即 **CAS(4 e , 4 o)** 在自旋轨道上 **4 空间 ×2 自旋 = 8 费米模式**，其中仍有 **四个电子**：占据图显示 **`1,1,1,1,0,0,0,0`**（与教程一致）。

阅读要点：

- **`a/b`**：自旋 $\alpha/\beta$ 成对出现于同一 **空间轨道指标**上。
- 截断前后 **序号重排**：Vendor platform 在构造约化 `FermionSpace`** 时对模式重新枚举**；不要盲目把「缩减表里的序号」与原始全 HF 序号混用——除非对照 driver 源码或显式 orbital map。

与本仓库：**费米空间中模式顺序**必须与 **`InteractionOperator` / JW 向量维度**一致；若在 pipeline 外用别的排序，会破坏与 `hartree_fock_state_jw` 的对齐。

---

## 3. 活性空间的手工指定：`frozen=[…]`

### 3.1 MO 基底与编号约定

Tutorial 写法：

```text
frozen=[0, 1, 2, 7, 8, 9, 10, 11, 12]
```

一般指 **canonical RHF MO 指标**（自 **0** 起），所列轨道 **整块移出相关性 Hilbert**：在 **FCI/CAS** 变分中这些 MO 的占据数**固定为 HF 值**（芯为双占，高位虚为 0）。

**余下 MO**构成 **活性**。若与 **`FromActiveSpace(ncas=4, nelecas=4)`** 等价，则冻结补集恰留下 **4 条空间轨道**、**4 个电子可在其中任意重排**：即 CAS **(4e, 4o)**。

### 3.2 手写 `frozen` 与 `FromActiveSpace`的化学差别

两者在 **Tutorial 特例**中可以给出**相同的占据图**，一般性上不等价：

| 方式 | 机制 | 利弊 |
|------|------|------|
| **显式 frozen 列表** | 人为指定扔掉哪几根 MO（可非连续索引） | 灵活；需靠 ** Mulliken/IOP 成分**确认对应哪根键或孤对 |
| **`FromActiveSpace(ncas, nelecas)`** | 依 CAS 记号 $n_{\mathrm{elec}}$、$n_{\mathrm{o}}$（空间轨道数）与程序约定，从 HF MO 序列中截取 **算法定义的一段连续（或可复现排序）轨道块** | 简短；若化学上希望的活性 MO **在能量序上不占连续块状**，则可能 **不切在目标子空间** |

### 3.3 CAS Hilbert 维数（自检用）

闭壳 $(n_{\mathrm{e}},\,n_{\mathrm{o}})$（$n_{\mathrm{o}}$ 为**空间**活性轨道数，$n_{\mathrm{e}}$ 为活性电子数且为偶）时，全活性 FCI 维数的一种常用写法为 $\binom{n_{\mathrm{o}}}{n_{\mathrm{e}}/2}^2$。例 **(4e, 4o)**：$\binom{4}{2}^2 = 36$ 个行列式。若与你的编码维数不一致，首先核对：**$n_{\mathrm{e}}$ 是否与 `nelecas` 同源、是否为空间 CAS 还是对自旋轨道计数**。

---

## 4. Atomic Valence Active Space（AVAS）

### 4.1 目标

对某些键 / 原子价层，希望得到 **化学成分透明**活性：不仅控制 **电子数**，还控制哪些 **HF MO** 主要来自 **给定 AO 标签**（如 **`Li 2s`**, **`H 1s`**）。

### 4.2 数学骨架与计算流程（细读）

本节把 AVAS **从 HF MO 向量到「哪些是 active/inactive」**走一遍：先固定 **记号**，再给 **投影与权重**，最后说明 **阈值双分支、`avas.frozenf`、`transf=`**各自干什么。

---

#### 步 0 · 已有对象

在完成 **RHF** 后你有：

1. **AO 基底** $\{\chi_\mu(\mathbf{r})\}_{\mu=1}^{N_{\mathrm{AO}}}$（可非正交），**重叠矩阵**  
   $$
   S_{\mu\nu}=\langle\chi_\mu|\chi_\nu\rangle.
   $$
2. **第 $J$ 个空间 MO（列向量形式）**：在 AO 表示下系数为 $\{C_{J\mu}\}$，对应实空间函数  
   $$
   \psi_J(\mathbf{r})=\sum_\mu C_{J\mu}\,\chi_\mu(\mathbf{r}).
   $$
   （与 PySCF `mo_coeff` 中 **第 $J$ 列**一致，具体行/列习惯以实现为准。）

**AVAS** 额外指定 **原子型标签集合** $\mathcal{L}$（如 `Li 2s`, `H 1s`），程序在：

- **极小参考基**（常为 **minao** 类）；
- **全基**（当前计算如 **6‑31G**）

之间建立 **同名 AO 线性嵌入**，最终得到在当前 AO 基底里张成的 **物理子空间的指标集合**。下文把「程序根据这些标签在 **全基 AO** 中挑出的那一段指标」抽象记为索引集 **$\mathcal{S}\subseteq\{1,\ldots,N_{\mathrm{AO}}\}$**。

---

#### 步 1 · 子空间 $\mathcal{S}$ 上的投影 $\hat{P}_{\mathcal{S}}$

令 **$\mathcal{S}$**张成的 AO 向量张成 Hilbert（或 $L^2$）子空间的 **（重叠）投影算符**为 $\hat{P}_{\mathcal{S}}$。在非正交 AO 基下常见的 **抽象形式**是把 $\hat{P}_{\mathcal{S}}$ 视作：在 AO 上对 **仅限于 $\mathcal{S}$ 的子块重叠 $S_{\mathcal{S}}$** 构造的局域正交投影，再拉回满 AO 维度；等价地，对每个 MO：

$$
|\psi_J\rangle=\sum_\mu C_{J\mu}\,|\chi_\mu\rangle,
\qquad
\hat{P}_{\mathcal{S}}|\psi_J\rangle
$$

是 **$|\psi_J\rangle$「只保留能落在 $\mathcal{S}$‑成分上的那一部分』**。实现上可选用 **加权 Mulliken‑型人口**、**IAO/极小基嵌入**或对 $S_{\mathcal{S}}$ **广义本征**，细节以 PySCF / Vendor platform 所用例程为准。

**关键点**：$\mathcal{S}$ 不是「整条 HF MO」，而是事先选好的 **原子价层 AO（或其线性张成）**，保证化学标签 $\mathcal{L}$ → 几何与子空间对齐。

---

#### 步 2 · 「耦合权重」$w_J$（占据与虚分开算）

对每个 **HF 空间 MO** $|\psi_J\rangle$，定义 **与该原子子空间的耦合强度**为一个 **$[0,1]$（或可归一化成该区间）的量**：

$$
w_J^{\mathrm{(occ)}\;\mathrm{或}\;\mathrm{(vir)}} \equiv 
\big\langle \psi_J \big| \hat{P}_{\mathcal{S}} \big| \psi_J \big\rangle
$$

或 **等价变体**：先对 $|\psi_J\rangle$ **归一**（若有 AO 度量），或使用 **Schmidt‑型重叠本征值**——教程里 **`eig` 一栏**指的就是 **某一种实现里对角化得到的「可见度分数」**。不同实现差一个 **归一约定的常数倍**，不改变 **阈值比较**的工程用途。

---

#### 步 3 · 占据 / 虚轨 **两遍**阈值（`threshold` 与 `threshold_vir`）

AVAS **分岔处理**：

| 分支 | MO 集合 | 截断参数 | 典型逻辑（概念） |
|------|---------|-----------|-------------------|
| **占据** | RHF **已占**的 MO | `threshold` | 按权重 **从高到低**排序；$\ge$阈值的记入 **candidate active occupied** |
| **虚轨** | RHF **空**的 MO | `threshold_vir` | 同上，$\ge \texttt{threshold\_vir}$ 的记入 **candidate active virtual** |

于是 **活性轨道集**近似为：**与 $\mathcal{S}$耦合足够强的占据 + 虚轨**。其余占据 MO 往往成为 **inactive（芯或近芯双占冻结）**，其余虚轨 **inactive virtual**。**两阈值可不同**：若只愿从价层挑出「长得像」的成分，可把虚轨阈值设高一点，避免吃进太多扩散虚成分。

---

#### 步 4 · **`avas.frozenf` 是什么？**

在完成上面分类之后，驱动器生成 **`frozen`** 一列 **MO 序号**：即 **永远不进入活性 CAS/Fock 自由度**的那些轨道。**`frozen` 等价于前文「整块移出相关性」**。Vendor platform 把该列表暴露在 **`avas.frozenf`**，供构造函数 **`frozen=avas.frozenf`** 直接使用。

---

#### 步 5 · **`transf=avas` 旋转 MO 是什么意思？**

阈值只解决 **索引集合**；为了在 **块对角**或 **局域化基底**上对活性块做哈密顿构造，常在 AO→MO 系数矩阵上做一次 **幺正或有界旋转**：

- 把 **active / inactive / virtual** MO **按块重排**（或等价地 **局域化**，使活性块在空间上集中到目标原子）。
- **`transf=`**将这种旋转之后的 **`mo_coeff`** 传给 `get_system()`，使后续 **`FermionSpace` 维数**与缩减后的轨道块一致，并与 **JW/积分构造**对齐。

若没有这个旋转仍能算，但数值与可解释性与教程默认不符。

---

#### 步 6 · **`get_system()`** 接收到什么？

综合起来：**哈密顿量在「旋转后的 MO」子空间里只保留 active 自由度**；inactive 等价 **冻结**或 **不出现于费米算符串**。这样 **CAS 的电子数 $\times$轨道数** 与 **HF 行列式投影到 active 块的占据**一致。

---

#### 再回到 LiH × `threshold = 0.8` **细读教程输出**

教程打印 **HF MO = 11**、**occupied = 2**（LiH **闭壳**：**6‑31G 下整条价带的 MO 计数与占据与具体几何有关**）；AVAS **从占据里筛出 Active from occupied = 1**——即 **有一条占据 MO「几乎完全」落在 `Li 2s` / `H 1s` 张成的空间里**（`eig ≈ 0.97`）。**从虚里筛 Active from virtual = 1**，`eig ≈ 0.985`——一条 **低空虚轨同样强耦合到同一原子价 AO 集合**，化学上解释为 **与该键／极化配套的虚伙伴**。**Number of active spatial orbitals = 2** ⇒ **CAS(2e, 2o)**：**只有 2 个电子在两个 active 轨道上相关**——余下价电子被算法判 **inactive**，以 **近似双占据 / 不配进 active** 的自由度处理（以实现细节为准）。

这 **不是**断言「LiH 只有 4 个价电子里物理上只有两个相关」的唯一正确模型——而是 **`threshold`** 极强时给出的 **极小自动子空间**；调低阈值或 **`aolabels`**加入 **Li 2p** 等会看到 **活性维数上浮**。

### 4.3 日志两行「reference AO indices」如何读？

对应 **§4.2 步 0**：同名 `aolabel` 在 **极小参考基**与**全工作基**两套 AO 编号中的位置不同，故打印两行。

- **`minao`（或类似）索引行**：在 **极小参考基**中的列号，用于低成本构造 $\mathcal{S}$ 与 $\hat{P}_{\mathcal{S}}$ 的中间量；
- **全基「6‑31G」索引行**：同一 `aolabel` 在当前 **HF 所用的全 AO 集**中的列索引，与 **`mo_coeff` 行索引**对上。

二者不是矛盾，而是 **basis embedding / 极小基对齐**的常见输出。**eig** ≈ 0.97、0.985：即 **§4.2 步 2** 里某种实现给出的 **耦合权重或对角 Schmidt 分数**，供 **步 3** 与阈值比较。

---

## 5. 活性空间如何做「对的」——实践清单（不依赖某一闭源教程）

| 步骤 | 建议动作 |
|------|----------|
| **基组与方法** | 活性空间语义基于 **你给定的 HF / DFT orbitals**。换泛函／基组等价于换 CAS 截面。 |
| **对称性** | 若要保持不可约表示块状，frozen/active 必须与 **_MO irreps_对齐**或用对称适配投影。 |
| **芯电子** | 轻元素可把内层塞进 frozen；重金属需 **赝势／ECP一致性**核对。 |
| **验证** | 做 **CASCI+FCI(or selected CI)**小规模对比或 **CASPT2校正**敏感度试验；或对关键 MO 导出 **cube**看 **HOMO/active**是否与化学直觉一致。 |
| **收敛** | 活性太小 → 偏差大；太大 → **计算量与 Hilbert 维数暴涨**；可用 **CASPT2 能量差 / 性质对活性尺寸的响应**扫格 |

---

## 6. **`qchem_stack` 对齐与已知局限**

本节据 **`ActiveSpaceSpec`、**`chem.active_space.mean_field_meta`**、`chem/drivers/pyscf_driver.py`、`integrations/open_driver_surface`、CASCI glue**写成；随代码演进请以 **`src/qchem_stack/chem/active_space/`、`config.py`、`pyscf_driver.py`** 为准。

| Vendor platform 教程概念 | **`qchem_stack` 近似 / 等价** |
|-------------------|------------------------------|
| `frozen=[…]` 驱动级改变活性 MO 集合 | **`active_space.strategy=manual`** + **`frozen_orbitals`** 当前 **记入 `driver_meta` / recipe**（`pipeline._run_scf`），**不等价于自动重排 **`mo_coeff`**；默认 **`active_space_casci_raw_blocks`** 仍按 **PySCF `CASCI` 与传入 MO 次序**截取——需非连续 frozen 时请 **自行置换 MO 列**或走 **embedding/projection** 路径。 |
| `FromActiveSpace` | **`strategy=cas`** + **`ncas` / `nelecas`**（或 legacy `n_active_*`）；对应 **CAS(n e , n o)** **尺寸**。 |
| `AVAS` **阈值投影**（PySCF、`mo_coeff` 再接 CASCI） | **`strategy=avas`**（**仅** `scf.driver=pyscf`，**必须**非空 **`chemistry_extended.avas_ao_labels`**）；`configs/example_h2_avas.yaml`；钩子 **`chem.active_space.pyscf_active_space_hooks`**；写入 **`qchem_active_space_resolution_v1`** + **`avas_atomic_projection_executed`**；管线回填 **`ncas`/`nelecas`** 与 **`SolverCapabilities.supports_avas_active_space_projection`** 门控。 |
| **`AVAS` stub（parity 钩子，无阈值投影）** | **`strategy=avas_stub`**（CAS 同款 **`ncas`/`nelecas`**）；**meta**：`avas_partial_stub`、`avas_atomic_projection_executed=false`、`avas_stub_semantics`。**`avas_ao_labels`** 在非 **`strategy=avas`** 下仍为 **仅日志**。 |
| `get_restricted_active_space_quantum_problem`（量子哈密顿流水线） | 提供 **`RestrictedActiveSpaceQuantumProblem`**：**紧凑 MO 积分、`InteractionOperator`、费米/qubit哈密顿**。 |

嵌入路径 **`projection_hamiltonian`** 另有一套 **fragment Mulliken 排序 + CASCI**：属于 **局域片段「选轨」**，与 Vendor platform‑driver‑级 **全局 frozen 列表语义**不同层级。

### 诚实边界（避免误用）

- **`strategy=avas`**：**阈值投影选轨 + 回填活性空间尺寸**已由 PySCF 路径接入（见上表）；**不构成**「与 Vendor platform **闭源产品 driver** 全流程」的二进制/L0 等价。**`frozen=avas.frozenf` 风格的自动 frozen 列表**若以独立元数据字段暴露，仍为 roadmap（当前以 **`qchem_active_space_resolution_v1`** 收敛尺寸为主）。  
- **`strategy=avas_stub`**：仍为 **钩子 / 诚实 partial**，不改变 MO。
- 若你只设 **`frozen_orbitals`** 但未改 **MO ordering**，CASCI **`get_h1eff`**拿到的 **不一定是**你想要的那个化学 active block——应 **自检 PySCF 文档**或通过 **embedding / 自定义 permutation**显式对齐 Vendor platform 教程。

---

## 7. 参考文献与交叉索引

| 材料 |
|------|
| Vendor platform 官方 extensions API：`AVAS`、`FromActiveSpace`、`ChemistryDriverPySCFMolecularRHF` |
| PySCF：`mcscf.CASCI`、`Mcscf.fast_newton_casscf`‑族、内建 **`avas`**‑辅助（具体API以 PySCF 版本为准） |
| AVAS / 极小活性空间自动生成：以 **PySCF `mcscf.avas`** 及各版本说明书中的文献引用为准 |

仓库内：**《[技术分析_Vendor platform_PySCF_vs_原生PySCF\_及工程借鉴](./技术分析_Vendor platform_PySCF_vs_原生PySCF_及工程借鉴.md)》§ 3.5**；parity 综述 **engineering_memory／public matrix** **`AVAS`** 行。
