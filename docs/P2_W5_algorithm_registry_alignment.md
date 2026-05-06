# P2-W5：公开算法 / ansatz / 映射 — 机读 registry 对照（Tangelo / InQuanto 叙事）

**角色**：把「研究包里常见的算法名」钉到本仓 **registry 模块**与 **parity 矩阵 §2**，避免口头对齐。不声称与闭源类名 L0 同构。

**母稿**：[P2_详细实施计划.md](P2_详细实施计划.md) §6 序 3、§8 第 1–2 周。

---

## 1. YAML `quantum.algorithm`（`ALGORITHM_REGISTRY`）

| Registry `id` | 实现入口（摘要） | 公开文档类比（叙事级） |
|-----------------|------------------|-------------------------|
| `vqe` | `quantum.algorithms.vqe.VQE` | 通用 VQE / HEA 变分层 |
| `adapt` | `adapt.FermionicAdaptVQE` | ADAPT-VQE；pool 与日程见 [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) §2 |
| `iqeb` | `iqeb.IQEBVQE` | IQEB 类外环；`configs/example_h2_iqeb.yaml` |

源码：`src/qchem_stack/quantum/algorithm_registry.py`。

---

## 2. 变分 ansatz 名（`ANSATZ_REGISTRY`）

| Registry `id` | 说明 |
|-----------------|------|
| `hea` | HEA 深度由 `quantum.vqe_depth` |
| `uccsd` | JW 参考态 UCCSD（`UCCSDVQE`） |
| `fermionic_adapt` | ADAPT 池驱动 |
| `iqeb` | IQEB 与算法键一致 |
| `uccsd_closed_shell_reference` | 激发计数 / bookkeeping 入 `parity_snapshot`，主线仍可 HEA |
| `trotter_ucc_placeholder` | JW + `quantum.uccsd_trotter_steps` → `UCCSDTrotterVQE`；**BK/SCBK 上 UCCSD Trotter 仍为矩阵 `n/a`** |

源码：`src/qchem_stack/quantum/ansatz_registry.py`。

---

## 3. Fermion→qubit 映射（`DOCUMENTED_FERMION_QUBIT_MAPPINGS`）

| 映射名 | 备注 |
|--------|------|
| `jordan_wigner` | 默认 |
| `bravyi_kitaev` | 全栈 Hamiltonian 构建 |
| `symmetry_conserving_bravyi_kitaev` | OpenFermion SCBK |

源码：`src/qchem_stack/chem/fermion_mapping_registry.py`；conformance：`tests/test_backend_conformance.py`。

---

## 4. 维护

- 新增 registry 键：同步本表 + [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) §2（若影响对外叙事）+ `export_parity_criteria_table` 稳定列（若导出暴露名称）。  
- P2 双月闸门见 [P2_详细实施计划.md](P2_详细实施计划.md) §5。
