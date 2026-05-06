# P2-W3：AVAS / 产品级 CASSCF — 与开放栈 `partial` 边界

**母稿**：[P2_详细实施计划.md](P2_详细实施计划.md) §6 序 6、§8 第 5–6 周。

---

## 已交付（诚实 `partial`，非 L0）

| 能力 | 机读 / 配置 | 说明 |
|------|-------------|------|
| **一步 CASSCF 轨道优化审计** | `chemistry_extended.casscf_orbital_optimization_audit`；`configs/example_h2_casscf_audit.yaml` | 将 PySCF `mcscf.CASSCF` 轨道步能量写入 `hamiltonian_meta.pyscf_driver.casscf_orbital_audit_v1`；**不**替代全活性空间迭代产品流 |
| **CASCI 默认变分哈密顿量** | 主 `pipeline` 路径 | 变分阶段仍以 CASCI 型积分为默认；与「全 CASSCF 产品深度」叙事区分 |

---

## 未交付（仍为差距表 `partial`）

- **AVAS**：无等价 InQuanto 公开 AVAS 产品路径；若引入须独立 gap 行 + driver 钩子设计。  
- **InQuanto 级 CASSCF 产品**：多步轨道 + 活性空间自洽与闭源默认 **不** 逐键对齐。

---

## 维护动作

- 矩阵 [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) §3「PySCF / active space」行与本文件一致时即视为文档闭合。  
- 若扩展 PySCF 可选链：同步 [chem/inquanto_driver_surface.py](../src/qchem_stack/chem/inquanto_driver_surface.py) 与 `tests/test_inquanto_driver_surface_l1.py`。
