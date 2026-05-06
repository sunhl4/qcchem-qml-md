# P1 化学与嵌入：InQuanto 镜像节点与 `qchem_stack` 复现程度对照

**版本**：与仓库当前源码及公开 parity 叙述对齐；镜像页 `frontmatter` 可能与本文不一致时，**以本文 + 源码 + 下列权威引用为准**。

**权威引用**

- 能力差距与边界：[与InQuanto能力差距与实施计划.md](与InQuanto能力差距与实施计划.md)、[架构_InQuanto闭源能力闭合与可复现边界.md](架构_InQuanto闭源能力闭合与可复现边界.md)
- 机读 driver 表面：`qchem_stack.chem.inquanto_driver_surface`、`qchem_stack.integrations.open_driver_surface.open_driver_coverage_matrix`
- 经典化学主实现：`qchem_stack.chem.drivers.pyscf_driver`、`qchem_stack.chem.embedding.*`
- **P1 跨后端 / 映射 conformance（pytest）**：`tests/test_backend_conformance.py`（`statevector`、`qiskit`·statevector/estimator、`ionstack`·注入、`JW/BK/SCBK`、TKET probe 字典；无 PySCF 则 skip，无 Qiskit/pytket 则对应 case skip）。
- 站点镜像树：`docs-site/docs/.vitepress/mirror-data.json`、`docs-site/scripts/inquanto-tree.yaml`（各 mirror 页 `index.md` 的 `status` / `qchem_module`）

---

## 1. 文档目的与口径

### 1.1 目的

将 **InQuanto 公开文档树中「化学 / 嵌入 / PySCF 扩展」镜像节点** 与 **本仓库 `qchem_stack` 实际实现** 做逐项对照，给出可维护的 **复现程度** 评级与 caveat，供：

- Y1 台账与 [InQuanto_Y1_public_alignment_ledger.md](InQuanto_Y1_public_alignment_ledger.md) 引用；
- 镜像页 `status`（shipped / partial / placeholder / not-applicable）的**二次校验**；
- 论文 Methods 中「开放栈做了什么 / 未声称什么」的表述依据。

### 1.2 不声称的范围（L0 排除）

本对照 **不** 声称与 **闭源 `inquanto-pyscf` wheel**、**InQuanto 内部默认启发式** 或 **类名级 API 一一对应**（L0）。对齐口径为公开资料可追溯 + 本仓可跑路径 + `repro` / parity 机读键（L1），见 [InQuanto_B_J_逐项闭合计划.md](InQuanto_B_J_逐项闭合计划.md)。

### 1.3 镜像 `status` 与源码的关系

- 镜像节点 `status` 来自站点生成配置（如 `inquanto-tree.yaml` → `mirror-data.json`），本质是 **IA 审计与导航标签**。
- 个别页面存在 **标签与正文矛盾**（例如 `AVAS` 标 `shipped` 但 `qchem_module` 为空、正文仍写未实现）。**复现程度以源码与差距总表为准**；若需与附录 C / backlog 计数一致，应单独维护「镜像 status ↔ 源码证据」纠偏列。

#### 1.3.1 纠偏清单（与 Phase0 对账同源）

| 纠偏项 | 权威依据 | 维护动作 |
|--------|----------|----------|
| 镜像 `status` vs 正文 | 本文 §2–§4、`open_driver_coverage_matrix` | 改版镜像 YAML 时对照 [InQuanto_B_J_逐项闭合计划.md](InQuanto_B_J_逐项闭合计划.md) **附录 A** |
| AVAS / CASSCF 产品深度 | `integrations/open_driver_surface.py` 行 `not_claimed` | 矩阵 §3 与 gap `drivers_cosmo_pbc` 不升级为 `yes` 除非实现 |
| UCCSD 变分 × 映射 | `quantum/algorithms/uccsd_vqe.py`（JW-only） | 与 `ucc_chem_ansatz` 机读条一致；BK/SCBK 用于 Hamiltonian+VQE 见 `test_backend_conformance` |

### 1.4 复现程度等级定义

| 等级 | 含义 |
|------|------|
| **高** | 主路径可跑；有配置 / 管线 / `repro` 或 pytest；**不**宣称与 InQuanto 闭源数值或 API 等价 |
| **中** | 子路径可跑或仅覆盖公开叙事的一部分（积分、嵌入子步骤等）；caveat 在 parity 矩阵或技术文档中已固定 |
| **低** | 主要为文档镜像、机读 gap、或 `open_driver_coverage_matrix` 一行声明；无 InQuanto 同名 Python API |
| **无** | 当前无对应实现，或列为「刻意不做」 |

---

## 2. 手册 / 教程 / 扩展层（与镜像「manual / tutorials / extensions」对应）

| 镜像主题 | 典型镜像路径 | 镜像常见 status | `qchem_stack` 对应实现 | 复现程度 | 说明与 caveat |
|----------|----------------|-----------------|------------------------|----------|----------------|
| 几何 | `manual`（几何） | partial | `MoleculeSpec`（`qchem_stack.config`）、`MolecularSystem`（`qchem_stack.chem.system`） | **高** | 符号、Bohr 坐标、电荷、多重度、基组进入 PySCF `gto.M` |
| 嵌入与 DMET（总述） | `manual` / embedding | partial | `EmbeddingSpec`、`chem/embedding/*`、`orchestration.pipeline` | **中** | `none` / `dmet` / `projection`；Schmidt 生产、whole_active 单碎片、stub 账本；**非**闭源 bath 全拟合 |
| DMET 概览 | `manual` / embedding | partial | `chem/embedding/dmet.py` + 管线 DMET 钩子 | **中** | `DMETContext`、占位 solver；字段契约见 [技术文档_DMET与parity_snapshot开放契约.md](技术文档_DMET与parity_snapshot开放契约.md)；口径与 [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) §3 一致 |
| 投影嵌入 | `manual` / embedding | partial | `projection.py`、`projection_hamiltonian.py` | **中** | Mulliken 片段排序 + PySCF CASCI 活性积分 + JW；**非** full many-body projection embedding |
| NEVPT2 / AC0 | `manual` / embedding | placeholder | — | **无** | 无独立量子化学实现；配置中 `classical_reference_method` 等为文档 / parity 占位 |
| Fe4N2 案例（AVAS+CASSCF 等） | `tutorials/case_study_fe4n2/*` | placeholder | 无单独「Fe4N2」化学包 | **低** | 教程树为镜像占位；量子管线见 `configs/`、`quantum.*` |
| Fe4N2：噪声硬件评估 | tutorials | 刻意不做 | — | **无** | 与公开矩阵「非专有硬件专优」一致 |
| 碎片化教程 / 大体系 DMET 等 | `tutorials/fragmentation` | partial / placeholder | 同嵌入与 `PySCFDriver` | **中～低** | 与 manual 同源能力，无第二套代码路径 |
| InQuanto-PySCF（扩展叙事） | `extensions` | partial | `chem/drivers/pyscf_driver.py` | **中** | 气相 RHF/ROHF/UHF、ddCOSMO、PBC（Γ / KRHF）；**非** inquanto-pyscf 二进制 |
| InQuanto-NGLView | `extensions` | 刻意不做 | — | **无** | 无 3D 可视化栈 |
| `inquanto.embeddings`（厂商包名） | api / 文档 | 刻意不做 | `EmbeddingSpec` 等 YAML 表达 | **无** | 不复制厂商包名级 API |

---

## 3. `api` 层：公开 API 名与开源栈映射

| 镜像 / InQuanto 相邻名 | 镜像常见 status | 复现程度 | `qchem_stack` 锚点 | 备注 |
|-------------------------|-----------------|----------|-------------------|------|
| `inquanto.geometries` | partial | **高** | `MoleculeSpec`、`MolecularSystem` | 与「几何」行一致 |
| `inquanto.extensions.pyscf` | partial | **中** | `PySCFDriver`、`ChemistryExtendedSpec` | 见 §4 driver 细表 |
| `qchem_stack.chem.embedding`（镜像指向） | partial | **中** | `chem/embedding` | 与 §2 嵌入行一致 |
| `qchem_stack.chem.drivers.pyscf_driver` | partial | **中** | `chem/drivers/pyscf_driver.py` | 同上 |

---

## 4. `api/extensions_pyscf/classes`：Driver 与碎片类名细表

下列 InQuanto **类名片段** 在开源栈中**多数无同名 Python class**；对照的是 **「化学意图 → 本仓实际调用的 PySCF / 配置路径」**。

### 4.1 AVAS / CASSCF（高关注）

| InQuanto 镜像类 | 镜像 status（常见） | 复现程度 | 源码事实 | 纠偏说明 |
|-----------------|---------------------|----------|----------|----------|
| **AVAS** | shipped（部分镜像页） | **低**（建议镜像改为 placeholder 或与差距表对齐） | 仓库 **无** 独立 AVAS 算法模块或 `qchem_module` 绑定 | [与InQuanto能力差距与实施计划.md](与InQuanto能力差距与实施计划.md) 写明 **「无 AVAS / 全 CASSCF 产品深度」**；若 backlog 记为 shipped，属**台账与源码不一致**，应修订 |
| **CASSCF** | partial | **中** | `active_space_integrals` 使用 `pyscf.mcscf.CASCI` 的 `get_h1eff` / `get_h2eff`；projection 路径亦用 CASCI 活性块 | InQuanto **CASSCF** 与开源栈 **CASCI 积分 + 固定活性空间** 语义**部分重叠**，**非**完整 CASSCF 产品行为 |

### 4.2 ChemistryDriverPySCF*（分子气相 + 溶剂 + 周期）

| InQuanto 镜像类 | 镜像 status（常见） | 复现程度 | `qchem_stack` 行为 |
|-----------------|---------------------|----------|---------------------|
| ChemistryDriverPySCFMolecular**RHF** | partial | **高** | `PySCFDriver.run_rhf()` → `scf.RHF` |
| ChemistryDriverPySCFMolecular**ROHF** | partial | **高** | `run_rohf()` → `scf.ROHF` |
| ChemistryDriverPySCFMolecular**UHF** | 占位（若树中为占位） | **高** | `run_uhf()` → `scf.UHF`；若镜像标占位，**应以源码为准改镜像** |
| …Molecular**RHF**QMMMCOSMO | partial | **中** | `solvent_model=ddcosmo` 时 `solvent.ddCOSMO(mf)` 接在 **已构建的 mf** 上；当前主路径与 **RHF+ddCOSMO** 一致 |
| …Molecular**ROHF**/…**UHF**QMMMCOSMO | 占位 | **低** | **无**与 InQuanto 一一对应的独立 ROHF/UHF+QM/MM driver 类；是否可接 PySCF 视版本，**未**作产品级承诺 |
| ChemistryDriverPySCF**GammaRHF** | partial | **中** | `run_pbc_rhf` + `pbc_kpoint_mesh=[1,1,1]` → Γ 点 RHF |
| ChemistryDriverPySCF**GammaROHF** | 占位 | **低** | `run_pbc_rhf` **要求** `scf.method=RHF`；**无** Γ 点 ROHF 周期支路 |
| ChemistryDriverPySCF**MomentumRHF** | partial | **中** | `mesh` 非全 1 → `KRHF` + `make_kpts` |
| ChemistryDriverPySCF**MomentumROHF** | 占位 | **低** | 同上，周期 ROHF **未**单独实现 |
| ChemistryDriverPySCF**Embedding***（多类） | 占位 | **低** | 嵌入由 **`EmbeddingSpec` + 管线** 表达，**非** PySCF `ChemistryDriverPySCFEmbedding*` 同名封装 |
| ChemistryDriverPySCF**Integrals** | 占位 | **中** | `active_space_integrals` 提供活性空间积分；**无** InQuanto 同名 Integrals driver 类 |

### 4.3 DMET / FMO / 活性空间辅助类

| InQuanto 镜像类 | 镜像 status（常见） | 复现程度 | `qchem_stack` 行为 |
|-----------------|---------------------|----------|---------------------|
| DMETRHFFragmentPySCF**Active** | partial | **中** | Schmidt 生产 / 活性哈密顿量 + `DMETContext` 等钩子；**非** PySCF fragment 类 API |
| DMETRHFFragmentPySCF**RHF** | partial | **中** | RHF 参考与碎片叙事部分覆盖 |
| DMETRHFFragmentPySCF**{CCSD,FCI,MP2}** | 占位 | **低** | **未**以同名 fragment solver 矩阵暴露；部分相关能力出现在 Schmidt / FCI 审计子路径，**不等价**于 InQuanto 全表 |
| ImpurityDMETROHF* 系列 | 占位 | **低** | 无 ROHF 杂质专用 driver 族 |
| FromActiveOrbitals / FromActiveSpace / FrozenCore | 占位 | **低** | 概念由 `ActiveSpaceSpec` 等承载，**无**同名类 |
| FMO / FMOFragment* | 占位 | **无** | 未实现 |

### 4.4 积分算子类

| InQuanto 镜像类 | 镜像 status（常见） | 复现程度 | `qchem_stack` 行为 |
|-----------------|---------------------|----------|---------------------|
| PySCFChemistry**Restricted**IntegralOperator | partial | **中** | `active_space_integrals` + OpenFermion 下游；**无**该类名文件级实现 |
| PySCFChemistry**Unrestricted**IntegralOperator | 占位 | **低** | 主路径以闭壳 / CASCI 常用分支为主；**未**对标 UHF 积分算子类 |

---

## 5. 机读汇总：`open_driver_coverage_matrix`

`qchem_stack.integrations.open_driver_surface.open_driver_coverage_matrix()` 返回的 `rows` 为 **四行** 声明式汇总，可与上表对照：

| `inquanto_adjacent_name` | `status` | 与 §2–§4 关系 |
|--------------------------|----------|----------------|
| gas-phase RHF/UHF/ROHF | `yes_pyscf` | 对应 §4.2 分子气相 **高** |
| ddCOSMO / implicit solvent | `partial_ddCOSMO` | §4.2 COSMO 行 **中** |
| PBC / k-point mesh | `partial_kmesh` | §4.2 周期 **中** |
| Full COSMO/PBC feature parity with InQuanto drivers | `not_claimed` | 占位 / 刻意不做 / 未拆分 QM/MM 类名等 **统一口径** |

更细的 YAML 别名见 `qchem_stack.chem.inquanto_driver_surface.INQUANTO_DRIVER_ALIAS_TO_CONFIG`（当前为 **短表**，不覆盖全部 InQuanto 类名）。

---

## 6. 节点计数（如 1 shipped / 20 partial / …）与本文关系

附录 C / `inquanto-node-backlog.generated.*` 中的 **按节点 `status` 计数** 可与镜像站点一致，但 **「shipped」数量不自动等于源码已交付」**——至少 **AVAS** 需在台账中单独纠偏（见 §4.1）。

建议在 Y1 台账增加一列：

- **evidence**：`pytest` 路径 / `configs/*.yaml` / `repro` 键 / `open_driver_coverage_matrix` 行 id。

---

## 7. 维护约定

- 镜像页 `status` 或 `qchem_module` 变更时：同步检查本文 §4 对应行，并更新 [与InQuanto能力差距与实施计划.md](与InQuanto能力差距与实施计划.md) §1 经典化学行（若涉及公开承诺）。
- 新增 PySCF 支路时：更新 `pyscf_driver.py`、`open_driver_coverage_matrix`、必要时 `inquanto_driver_surface.py` 与本文 §4。

---

*本文档由仓库内实现与公开差距叙述整理而成；不替代 Quantinuum 官方 API 文档。*
