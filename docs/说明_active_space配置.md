# 实验 YAML 中的 `active_space:` 配置说明

本文说明 `src/qchem_stack/config/active_space.py` 里 `ActiveSpaceSpec` 各字段与加载时的自动检查。经典平均场见 [说明_scf配置.md](说明_scf配置.md)；配置加载流程见 [说明_实验配置加载_io.md](说明_实验配置加载_io.md)。

---

## 这段配置管什么

`scf` 算完分子轨道之后，通常**不会用全部轨道**去建量子问题，而是只取一小块「活性」轨道和电子。`active_space:` 用来写明：

- 这块空间 **多大**（几条轨道、几个电子）  
- **怎么定**这块空间（你手写数字，还是走 AVAS 等流程）  
- 电子问题 **怎么写成量子比特上的算符**（映射方式）

不负责分子几何、不负责 VQE 迭代次数（后者在 `quantum:`）。

---

## 为什么很多示例只有三行

例如 `configs/example_h2_geometry_file_xyz.yaml`：

```yaml
active_space:
  n_active_orbitals: 2
  n_active_electrons: 2
  fermion_qubit_mapping: jordan_wigner
```

未写出项使用默认值：

| 未写项 | 默认 |
|--------|------|
| `strategy` | `cas` |
| `ncas` / `nelecas` | 加载时由 `n_active_*` **自动对齐为 2** |
| `frozen_orbitals` | `[]` |
| `prefer_restricted_spatial_fermion_for_jordan_wigner` | `false` |
| `jordan_wigner_coeff_atol` | 不设置 |

---

## 参数详解

实现：`ActiveSpaceSpec`（`active_space.py`）；复杂规则在 `_active_space_validation.py`。

### `strategy`（默认 `cas`）

**含义：** 活性空间「怎么定下来」的套路。

| 取值 | 通俗理解 |
|------|----------|
| `cas` | **默认、最常见**：在 yaml 里直接写活性轨道数、活性电子数。 |
| `manual` | 同样手写数目，并可配合 `frozen_orbitals` 记录哪些轨道视为冻住（ bookkeeping ）。 |
| `avas_stub` | 数字写法同 `cas`，但**不执行**真实 AVAS 轨道投影；元数据标明为占位/桩（见 `example_h2_avas_stub.yaml`）。 |
| `avas` | 用 PySCF `mcscf.avas` 核按阈值选活性空间；需 **`supports_avas_active_space_projection`** + 非空 **`chemistry_extended.avas.ao_labels`**（PySCF：`example_h2_avas.yaml`；Psi4：`example_h2_psi4_avas.yaml`）。 |

`avas` / `avas_stub` 的化学细节见 [活性空间指定与AVAS_理论实践与开源对照.md](活性空间指定与AVAS_理论实践与开源对照.md)。

---

### `n_active_orbitals` / `n_active_electrons`（可为空）

**含义：** 活性空间内 **轨道条数**、**电子个数**（直观写法）。

- H₂ 示例 `2` / `2`：2 轨道 2 电子（占满），决定后面量子比特规模的大致量级。  
- 在 `cas` / `avas*` 模式下会与 `ncas` / `nelecas` 在加载后 **填成同一组数**。

---

### `ncas` / `nelecas`（可为空）

**含义：** 与上一对相同，另一套常用命名（化学文献里常见）。

- 可只写 `n_active_*`（多数 H₂ 示例），或只写 `ncas` / `nelecas`（如 `example_h2_active_space_cas_strategy.yaml`）。  
- **两套都写时数值必须一致**，否则加载失败。

---

### `frozen_orbitals`（默认 `[]`）

**含义：** 在 `strategy: manual` 时，列出 **冻结核轨道编号**（从 0 起），用于 manual 策略下的 bookkeeping。

- 一般 H₂ 示例为 `[]` 或不写。  
- 不能为负、不能重复（见下文校验）。

---

### `fermion_qubit_mapping`（默认 `jordan_wigner`）

**含义：** 把电子算符问题 **翻译到量子比特** 时用的规则。

| 取值 | 说明 |
|------|------|
| `jordan_wigner` | 默认；绝大多数 H₂ 示例。 |
| `bravyi_kitaev` | 另一种编码；见 `example_h2_uccsd_bk.yaml`。 |
| `symmetry_conserving_bravyi_kitaev` | 带对称性约束的 BK 变体。 |

只影响 **量子哈密顿量如何写成 Pauli 项**，不改变经典 SCF 怎么算。若 `quantum.variational_ansatz=uccsd`，实验级校验会限制允许的映射集合（见 `_experiment_validation.py`）。

### 三种映射在代码里是否已实现？

| `fermion_qubit_mapping` | 活性空间哈密顿量 | 说明 |
|-------------------------|------------------|------|
| `jordan_wigner` | ✅ | OpenFermion JW；可选稀疏 `jordan_wigner_coeff_atol`；可选 `prefer_restricted_spatial_fermion_for_jordan_wigner` 走空间轨道→费米子→JW（省内存） |
| `bravyi_kitaev` | ✅ | OpenFermion BK；**默认**走 `restricted_spatial_fermion_operator` 路径（与 JW 快捷路径同级，不再强制稠密 spin-ERI） |
| `symmetry_conserving_bravyi_kitaev` | ✅ | OpenFermion SCBK；同上空间轨道快捷路径；比特数比 JW 少 2 |

**构建路径（`meta["qubit_build"]` / `jw_build`）：**

| 路径 | 何时使用 |
|------|----------|
| `restricted_spatial_fermion_operator` | BK / SCBK；JW 且 `prefer_restricted_spatial_fermion_for_jordan_wigner` |
| `interaction_operator` | JW / BK / SCBK 的稠密 `InteractionOperator` 路径；JW 在设 `jordan_wigner_coeff_atol` 时必须走此路径 |

**仍与 JW 不对等的部分（已知）：**

- `jordan_wigner_coeff_atol` **仅** JW + `interaction_operator` 路径。  
- `quantum.variational_ansatz=uccsd` 不允许 `symmetry_conserving_bravyi_kitaev`（`_experiment_validation.py`）。  
- 部分嵌入/投影侧路径仍以 JW 为主（见 `hamiltonian.py` 注释）。

实现入口：`_fermion_operator_to_qubits`、`_interaction_operator_to_qubits`、`_use_restricted_spatial_fermion_build`（`src/qchem_stack/chem/hamiltonian.py`）。parity 测试：`tests/chem/test_spatial_fermion_jw_path.py`（含 BK/SCBK 与 InteractionOperator 路径数值一致）。

**BK/SCBK 勿用 JW 专用项、构建路径图解、后续性能优化待办：** [说明_BK与SCBK映射路径与性能优化备忘.md](说明_BK与SCBK映射路径与性能优化备忘.md)。

---

### `prefer_restricted_spatial_fermion_for_jordan_wigner`（默认 `false`）

**含义：** 仅在 `jordan_wigner` 时有效：用 **更省内存的路径** 从空间轨道积分直接建费米子算符，避免为映射步骤构造巨大的自旋积分张量。

- 默认关闭即可。  
- 为 `true` 时 **不能** 同时设置 `jordan_wigner_coeff_atol`。

---

### `jordan_wigner_coeff_atol`（默认不设置）

**含义：** 可选正数阈值：JW 路径上绝对值过小的系数可丢弃，减少算符项数。

- 必须为正；与 `prefer_restricted_spatial_fermion_for_jordan_wigner: true` **互斥**。  
- parity 小样例中极少出现。

---

## 加载时的自动检查

字段类型通过后，运行三个检查（不跑量子计算）：

```
YAML active_space: { ... }
    → frozen_orbitals 列表是否合法
    → 按 strategy 对齐 ncas/nelecas 与 n_active_*
    → JW 相关两个开关是否矛盾
    → ActiveSpaceSpec
```

### `_validate_frozen_orbitals`（字段级）

| 规则 | 失败时 |
|------|--------|
| 每项 ≥ 0 | 报错 |
| 不重复 | 报错 |

### `_normalize_active_space_entry`（事后，逻辑在 `_active_space_validation.py`）

**`strategy` 为 `cas` / `avas_stub` / `avas`：**

- 必须能确定轨道数、电子数（`ncas`+`nelecas` 或 `n_active_*`）。  
- 两套名字都写时须一致；均 ≥ 1。  
- 写回四套字段为同一组整数。

**`strategy` 为 `manual`：**

- **必须**写 `n_active_orbitals` 与 `n_active_electrons`。  
- 若写了 `ncas`/`nelecas`，须与 `n_active_*` 一致。

### `validate_active_space_post_normalize`（规范化之后）

| 规则 | 失败时 |
|------|--------|
| `nelecas <= 2 * ncas` | 电子数不能超过轨道数的 2 倍 |
| `frozen_orbitals` 非空时 `strategy` 必须为 `manual` | 避免在 cas/avas 下误用冻结核轨道列表 |

### `_jw_optimizer_flags_consistent`（事后，`validate_jw_optimizer_flags`）

| 情况 | 结果 |
|------|------|
| 开了空间轨道 JW 优化，但映射不是 `jordan_wigner` | ❌ |
| 同时开空间轨道优化与 `jordan_wigner_coeff_atol` | ❌ |
| 设置了 `jordan_wigner_coeff_atol`，但映射不是 `jordan_wigner`（含 BK/SCBK） | ❌（配置加载即失败，不必等到 `hamiltonian.py`） |
| `jordan_wigner_coeff_atol` 非正 | ❌ |

**说明：** `strategy: avas` 与 `scf.driver`、PBC、`chemistry_extended` 等的搭配，在 **`ExperimentConfig` 层** 另有检查（`_experiment_validation.py`），详见下文 [跨模块校验与多后端](#跨模块校验与多后端) 与 [后续开发备忘](#后续开发备忘)。

---

## 与示例 yaml 对照

| 参数 | `example_h2_geometry_file_xyz.yaml` | 仓库中另有示例 |
|------|-------------------------------------|----------------|
| `n_active_orbitals` / `n_active_electrons` | ✅ 2 / 2 | 普遍 |
| `fermion_qubit_mapping` | ✅ `jordan_wigner` | `bravyi_kitaev` 等 |
| `strategy` | 默认 `cas` | `manual`、`avas_stub`、`avas` |
| `ncas` / `nelecas` | 加载后自动填 2 | 显式写法见 `example_h2_active_space_cas_strategy.yaml` |
| `frozen_orbitals` | 默认 `[]` | `example_h2_active_space_manual_strategy.yaml` |
| JW 优化两项 | 默认 | 多在注释或高级配置 |

---

## 按场景的最小写法

**与小 H₂ 示例相同（默认 cas）：**

```yaml
active_space:
  n_active_orbitals: 2
  n_active_electrons: 2
  fermion_qubit_mapping: jordan_wigner
```

**显式 cas 命名：**

```yaml
active_space:
  strategy: cas
  ncas: 2
  nelecas: 2
```

**manual + 冻结核轨道列表：**

```yaml
active_space:
  strategy: manual
  n_active_orbitals: 2
  n_active_electrons: 2
  frozen_orbitals: []
```

**真实 AVAS（需 PySCF + `chemistry_extended`）：**

```yaml
active_space:
  strategy: avas
  ncas: 2
  nelecas: 2
# chemistry_extended.avas_ao_labels 等在 experiment 其它段配置
```

---

## 与上下游分工

| 块 | 内容 |
|----|------|
| `scf` | 平均场、轨道从哪来 |
| **`active_space`** | 切哪一块、几个电子、如何映到量子比特 |
| `quantum` | VQE/QSE 等算法与迭代 |

活性轨道越多，量子比特与哈密顿量项数通常越大。

---

## 跨模块校验与多后端

`ActiveSpaceSpec` **只描述**活性空间尺寸与映射；**不绑定**某一量子化学程序。与 `molecule` / `scf` / `quantum` / 后端能力的组合规则在 `ExperimentConfig` 加载时由 `_experiment_validation.py` 检查。

**多后端总览（registry + 能力位，而非写死 PySCF）：** 见 [说明_经典化学后端驱动_registry与能力位.md](说明_经典化学后端驱动_registry与能力位.md)。

| 检查项 | 所在文件 | 要点 |
|--------|----------|------|
| `nelecas <= 2*ncas`、`frozen_orbitals` 仅 `manual`、JW 开关互斥 | `_active_space_validation.py` | 与 `scf.driver` 无关 |
| `strategy: avas` → `avas_ao_labels`、后端须 `supports_avas_active_space_projection` | `_experiment_validation.validate_avas_strategy_requires_labels_and_capability` | **已完成 C2**：按 capability + labels 门控；Psi4 等可委托 PySCF AVAS 核 |
| `strategy: avas` → `supports_avas_active_space_projection` | `validate_backend_capabilities_for_pre_quantum_path` | 按 **当前 driver 的 capabilities** 拒绝，不 import PySCF |
| 默认 pre-quantum → `supports_restricted_active_space_qubit_hamiltonian` | 同上 | **PySCF 与 Psi4 均已声明 True**（见能力位表） |
| `avas` + PBC | `validate_pbc_excludes_casscf_hooks` | 与 driver 无关 |
| UCCSD → 映射 ∈ `{jordan_wigner, bravyi_kitaev}` | `validate_uccsd_variational_constraints` | 与 driver 无关 |
| `nelecas` 与 `molecule.multiplicity` 自旋一致 | **尚未实现** | 见 [后续开发备忘](#后续开发备忘) |

---

## 后续开发备忘

深入开发 `_active_space_validation.py`、活性空间策略或多后端接入时，优先对照本表与 [config_校验分层约定.md](config_校验分层约定.md)。

### A. `_active_space_validation.py` — 已完成（2026-05）

| 编号 | 内容 | 函数/位置 |
|------|------|-----------|
| A1 | `jordan_wigner_coeff_atol` 仅在 `fermion_qubit_mapping='jordan_wigner'` 时允许 | `validate_jw_optimizer_flags` |
| A2 | `validate_active_space_post_normalize`：`ncas`/`nelecas` 未填则 **报错**（禁止静默跳过） | `validate_active_space_post_normalize` |
| A3 | cas/manual 写回四套计数字段 DRY | `_assign_active_space_counts` |
| A4 | 错误信息统一前缀 `active_space:` | 全文件 |

### B. `_active_space_validation.py` — 模块内待办

| 编号 | 建议 | 说明 |
|------|------|------|
| B1 | `frozen_orbitals` 规范化 | 可选：加载时排序或 `sorted(set(...))`，便于 repro 比对 |
| B2 | `frozen_orbitals` 与总 MO 数 | 需 mean field 后才能知上界；宜 pipeline 或 **ExperimentConfig** 层（见 C3） |
| B3 | 合并两个 `@model_validator(mode="after")` | `active_space.py` 中 normalize + JW 可合并为一个入口，减少顺序依赖 |
| B4 | 重命名 `validate_jw_optimizer_flags` | 若继续增加 BK/SCBK 专用 atol 字段，可改为 `validate_fermion_mapping_flags` |
| B5 | 单测补齐 | `manual` 缺字段、双套名字冲突、`prefer_*`+`atol` 互斥、负 `frozen_orbitals`、normalize 幂等；与上文错误表一一对应 |
| B6 | 类 docstring 缩短 | `ActiveSpaceSpec` 长说明以本文为准，Python 内保留简短版 + 链接 |

### C. `ExperimentConfig` / `_experiment_validation.py` — 跨模块待办

| 编号 | 建议 | 说明 |
|------|------|------|
| C1 | **`molecule.multiplicity` × `active_space.nelecas` 粗校验** | 闭壳 RHF 下活性电子奇偶与总自旋明显矛盾时警告或拒绝；须约定 ROHF/UHF/CAS 例外，避免误杀 |
| C2 | **AVAS：以 capability 为主、弱化 `driver=='pyscf'` 字面量** | **已完成** — `validate_avas_strategy_requires_labels_and_capability` |
| C3 | **`frozen_orbitals` 索引 < 总轨道数** | 需 `n_mo` 或 SCF 结果；与 B2 同源 |
| C4 | **AVAS 前置条件单页** | 汇总 `avas_ao_labels`、PBC 禁用、capabilities、示例 yaml 链（`example_h2_avas.yaml`） |
| C5 | **UCCSD / embedding / PBC** | 已有函数见 [跨模块校验与多后端](#跨模块校验与多后端)；新组合只加 `_experiment_validation.py`，勿塞进 `_active_space_validation.py` |

### D. 映射与性能（`chem/hamiltonian.py`）

见 [说明_BK与SCBK映射路径与性能优化备忘.md](说明_BK与SCBK映射路径与性能优化备忘.md)：

| 编号 | 内容 |
|------|------|
| D1 | BK/SCBK 专用系数截断（勿复用 `jordan_wigner_coeff_atol` 字段名） |
| D2 | UCCSD + SCBK |
| D3 | `prefer_restricted_spatial_fermion_for_jordan_wigner` 独立 H₂ parity yaml |
| D4 | 启用 atol 时在 `driver_meta`/repro 记录截断阈值与 Pauli 项数 |

### E. 架构与多后端（中长期）

| 编号 | 内容 |
|------|------|
| E1 | **`chem/active_space/` 能力位** | 将「按 AO 标签投影 / 选活性轨道」从 PySCF 专用实现抽成后端可插拔接口；config 只保留 `strategy` + 尺寸 + 标签列表（与 [execution/unified_chem_driver_audit_notes.md](execution/unified_chem_driver_audit_notes.md) 一致） |
| E2 | **`avas_stub` vs `avas` 选型表** | 模板：`example_h2_avas_stub.yaml` / `example_h2_avas.yaml` |
| E3 | **新后端接入清单** | 注册 `create_solver` → 填 `SolverCapabilities` → 跑 `validate_backend_capabilities_for_pre_quantum_path` 相关用例；见 [说明_经典化学后端驱动_registry与能力位.md](说明_经典化学后端驱动_registry与能力位.md) |

### F. 暂不建议在 `_active_space_validation.py` 内做

- **按基组自动推断 `ncas`**：加载阶段尚无 mean field。  
- **在 config 层 `import pyscf`**：破坏多后端、轻量加载；AVAS **执行** 留在 chem solver。  
- **把 UCCSD/embedding/PBC 规则写进本文件**：违反 [config_校验分层约定.md](config_校验分层约定.md)。

---

## 源码

| 内容 | 路径 |
|------|------|
| `ActiveSpaceSpec` | `src/qchem_stack/config/active_space.py` |
| 校验逻辑 | `src/qchem_stack/config/_active_space_validation.py` |
| `avas` 等与 driver 搭配 | `src/qchem_stack/config/_experiment_validation.py` |
| 总配置 | `src/qchem_stack/config/experiment.py` |
