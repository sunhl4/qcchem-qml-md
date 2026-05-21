# BK / SCBK 映射路径说明与性能优化备忘

本文记录 **Bravyi–Kitaev（BK）** 与 **对称守恒 BK（SCBK）** 在本仓库中的实现状态、与 **Jordan–Wigner（JW）** 的差异、YAML 中应/不应使用的参数，以及后续性能优化待办。字段总览见 [说明_active_space配置.md](说明_active_space配置.md)。

---

## 1. 当前实现状态（2026 年工程现状）

### 1.1 三种映射是否可用？

| `fermion_qubit_mapping` | 哈密顿量构建 | 说明 |
|-------------------------|--------------|------|
| `jordan_wigner` | ✅ | OpenFermion JW；可选 `jordan_wigner_coeff_atol`；可选 `prefer_restricted_spatial_fermion_for_jordan_wigner` |
| `bravyi_kitaev` | ✅ | OpenFermion `bravyi_kitaev` |
| `symmetry_conserving_bravyi_kitaev` | ✅ | OpenFermion `symmetry_conserving_bravyi_kitaev`；活性空间需给出自旋轨道数与电子数；**量子比特数比 JW 少 2** |

UCCSD 变分 ansatz 目前仅允许 `jordan_wigner` 与 `bravyi_kitaev`（见 `_experiment_validation.py`），**不允许** `symmetry_conserving_bravyi_kitaev`。

### 1.2 两条构建路径（`meta["qubit_build"]` / `jw_build`）

```
经典活性空间积分
        ↓
┌──────────────────────────────────────────────────────────┐
│ 路径 A：restricted_spatial_fermion_operator（省内存）       │
│   空间 MO 积分 → FermionOperator → JW / BK / SCBK          │
│   BK / SCBK：默认自动走此路径                               │
│   JW：需 prefer_restricted_spatial_fermion_for_jordan_wigner │
│   ❌ 不支持 jordan_wigner_coeff_atol                        │
└──────────────────────────────────────────────────────────┘
        ↓（JW 且设置了 atol，或未走 spatial）
┌──────────────────────────────────────────────────────────┐
│ 路径 B：interaction_operator                              │
│   稠密 InteractionOperator → JW（可稀疏 atol）/ BK / SCBK   │
└──────────────────────────────────────────────────────────┘
```

| 路径 | 何时使用 |
|------|----------|
| `restricted_spatial_fermion_operator` | **BK、SCBK 始终**（在 compact / canonical pack / pipeline 主路径）；JW 且 `prefer_restricted_spatial_fermion_for_jordan_wigner: true` |
| `interaction_operator` | JW/BK/SCBK 的稠密积分路径；**JW 在设置 `jordan_wigner_coeff_atol` 时必须走此路径** |

### 1.3 源码与测试入口

| 内容 | 路径 |
|------|------|
| 映射与路径选择 | `src/qchem_stack/chem/hamiltonian.py`（`_fermion_operator_to_qubits`、`_interaction_operator_to_qubits`、`_use_restricted_spatial_fermion_build`） |
| JW 稀疏 atol | `src/qchem_stack/chem/jordan_wigner_sparse.py` |
| 配置字段 | `src/qchem_stack/config/active_space.py` |
| BK/SCBK spatial 与 InteractionOperator 数值一致（H₂） | `tests/test_spatial_fermion_jw_path.py`（参数化 BK、SCBK） |
| 映射指纹 / 比特数 | `tests/test_fermion_qubit_mapping.py`、`tests/test_pyscf_h2_optional.py` |
| 示例 yaml | `configs/example_h2_uccsd_bk.yaml`（BK） |

---

## 2. 不要对 BK/SCBK 使用的 JW 专用参数（及原因）

### 2.1 不要设 `prefer_restricted_spatial_fermion_for_jordan_wigner`

**这个开关是干什么的**

- 名字限定 **for_jordan_wigner**：在 **JW** 映射时，用「空间轨道积分 → 费米子算符 → 量子比特」代替先构造巨大自旋轨道 ERI 再映射。
- 它是 **JW 的可选加速开关**，不是「所有映射的总开关」。

**BK/SCBK 为何不要写**

- 改版后，BK/SCBK **已默认**走与 JW 同类的 `restricted_spatial_fermion_operator` 路径，**无需**再打该 flag。
- 若对 BK/SCBK 仍写 `prefer_restricted_spatial_fermion_for_jordan_wigner: true`，配置语义矛盾（JW 专用开关 + 非 JW 映射），加载时会 **报错**，避免误以为该 flag 在控制 BK。

| 映射 | 是否写 `prefer_restricted_spatial_fermion_for_jordan_wigner` |
|------|-----------------------------------------------------------|
| `jordan_wigner` | 可选；`true` → spatial 路径（且不能与 `jordan_wigner_coeff_atol` 同开） |
| `bravyi_kitaev` / `symmetry_conserving_bravyi_kitaev` | **不要写** |

### 2.2 不要设 `jordan_wigner_coeff_atol`

**这个参数是干什么的**

- 仅在 **InteractionOperator → JW** 时，按阈值丢弃小系数项（`jordan_wigner_interaction_operator_sparse`）。
- 用于 **稀疏化 JW 哈密顿量**，名字与实现均绑定 JW。

**BK/SCBK 为何不要写**

- BK/SCBK 使用 OpenFermion 的 `bravyi_kitaev` / `symmetry_conserving_bravyi_kitaev`，**没有**与 JW 共用的 atol 实现。
- 若允许在 BK 上写该字段，容易被理解为「也在截断」，实际无效或必须误走 JW 逻辑。
- 代码规则：设 `jordan_wigner_coeff_atol` → 只能 `fermion_qubit_mapping: jordan_wigner` 且走 `interaction_operator` 路径；BK/SCBK 带 atol 会在配置或构建阶段被拒绝/无法走 spatial 路径。

**一句话：** `jordan_wigner_coeff_atol` = **JW 专用**；BK/SCBK 要么完整映射，要么将来单独增加 `bk_*` / `scbk_*` 截断参数（见下文待办）。

---

## 3. 推荐 YAML 写法

### Bravyi–Kitaev

```yaml
active_space:
  n_active_orbitals: 2
  n_active_electrons: 2
  fermion_qubit_mapping: bravyi_kitaev
  # 不要写 prefer_restricted_spatial_fermion_for_jordan_wigner
  # 不要写 jordan_wigner_coeff_atol
```

### 对称守恒 Bravyi–Kitaev

```yaml
active_space:
  n_active_orbitals: 2
  n_active_electrons: 2
  fermion_qubit_mapping: symmetry_conserving_bravyi_kitaev
```

运行后可在 repro / `qubit_hamiltonian.meta` 中确认：

- `fermion_to_qubit_map` 为所选映射；
- `qubit_build` 一般为 `restricted_spatial_fermion_operator`（主 pipeline 路径）。

### Jordan–Wigner（对照）

**省内存（spatial 路径）：**

```yaml
active_space:
  fermion_qubit_mapping: jordan_wigner
  prefer_restricted_spatial_fermion_for_jordan_wigner: true
```

**系数截断（必须 InteractionOperator 路径，不能与上一条 prefer 同开）：**

```yaml
active_space:
  fermion_qubit_mapping: jordan_wigner
  jordan_wigner_coeff_atol: 1.0e-12
```

---

## 4. 与 JW 仍不对等的部分（正确性已对齐，性能/功能未完全对齐）

| 能力 | JW | BK / SCBK |
|------|----|-----------|
| spatial 费米子快捷路径 | ✅（需 flag 或默认 pipeline 分支） | ✅（自动） |
| InteractionOperator 稠密路径 | ✅ | ✅ |
| 映射后 Pauli 系数截断（atol） | ✅ `jordan_wigner_coeff_atol` | ❌ 未实现 |
| UCCSD + 该映射 | JW、BK 支持 | SCBK **配置层禁止** |
| 嵌入/投影部分侧路径 | JW 为主 | 非 JW 时可能回退（见 `hamiltonian.py` 注释） |

**历史问题（已修复）：** 早前 BK/SCBK 在 compact 路径会退回 `compact.to_interaction_operator()` 稠密 spin-ERI；现已与 JW spatial 路径对齐，并有 H₂ parity 测试。

---

## 5. 后续性能优化备忘（回看本文时从此节开工）

下列为 **尚未完成** 的增强项，按建议优先级排列。完成每项后请更新本节状态，并补测试与 `说明_active_space配置.md` 链接。

### P1 — BK 映射后系数截断（类比 JW atol）

- **目标：** 在 BK 哈密顿量 Pauli 展开后（或映射过程中）丢弃 $|c| \le \tau$ 的项，控制项数与 VQE 成本。
- **注意：** 不能复用 `jordan_wigner_coeff_atol` 字段名；建议新增如 `bravyi_kitaev_coeff_atol` 或通用的 `qubit_hamiltonian_coeff_atol`（需文档说明对各映射是否生效）。
- **参考实现：** `src/qchem_stack/chem/jordan_wigner_sparse.py`。
- **验收：** H₂ 能量随 $\tau$ 的偏差表；`meta` 记录 $\tau$ 与剩余项数；`tests/test_spatial_fermion_jw_path.py` 或新文件。

### P2 — SCBK 映射后系数截断

- 与 P1 类似；SCBK 比特数更少，截断策略可能对能量更敏感，需单独测。

### P3 — UCCSD 放开 `symmetry_conserving_bravyi_kitaev`

- **现状：** `_experiment_validation.py` 中 `_UCCSD_ALLOWED_FERMION_QUBIT_MAPPINGS` 仅 JW、BK。
- **工作：** 扩展 `operator_pool_registry` 的 SCBK UCCSD 池（若 OpenFermion/现有池可复用）；更新校验与 `test_uccsd_mapping_support_matrix.py`。
- **风险：** SCBK 比特编码与 JW/BK 不同，激发算符池需逐类验证。

### P4 — 嵌入 / 投影路径的 BK、SCBK 一等支持

- **现状：** `hamiltonian.py` 中部分注释写明非 JW 时回退 InteractionOperator 或 JW 专用逻辑。
- **工作：** 审计 `projection_hamiltonian`、`embedding` 相关模块；统一走 `_use_restricted_spatial_fermion_build`。

### P5 — 配置层友好报错与文档生成

- 在 `ActiveSpaceSpec` 加载时：若 BK/SCBK + `jordan_wigner_coeff_atol` / 错误组合 `prefer_*`，错误信息指向本文。
- 可选：`fermion_mapping_registry.tangelo_public_mapping_alias_surface_v1` 增加「推荐 yaml 片段」。

### P6 — 大活性空间基准与 profiling

- 对比 spatial vs interaction_operator 路径在时间/内存上的差异（BK/SCBK vs JW）。
- 记录 `ncas` 增大时的推荐默认路径。

---

## 6. 设计原则（为何严格区分参数）

1. **参数名与实现一一对应**：避免 yaml 里写 JW 专用项却作用在 BK 上，造成「以为截断、实际没有」的 silent wrong。
2. **路径在 meta 里可追溯**：`qubit_build` / `jw_build` 写入 repro，便于 Methods 与 parity 对读。
3. **先正确性、后性能**：BK/SCBK 已与 JW 在 spatial 路径上数值一致（H₂ 测试）；截断与 UCCSD+SCBK 属于下一层优化，单独排期。

---

## 7. 相关文档

- [说明_active_space配置.md](说明_active_space配置.md) — `active_space` 全字段与加载校验  
- [说明_实验配置加载_io.md](说明_实验配置加载_io.md) — yaml 如何进入 `ExperimentConfig`  
- [活性空间指定与AVAS_理论实践与开源对照.md](活性空间指定与AVAS_理论实践与开源对照.md) — AVAS 与活性空间理论背景  
- [public_parity_matrix.md](public_parity_matrix.md) — 能力矩阵与样例 config 索引  
