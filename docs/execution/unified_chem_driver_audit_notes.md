# 统一化学接口审计笔记（`scf.driver` / PySCF 在编排层的出现）

**状态**：进行中（随 `day001_day090_unified_chemistry_interface_calendar.md` 第 4 天及后续关闭条目）。

## 1. `orchestration/pipeline.py`

| 符号 / 模式 | 用途分类 | 备注 |
|---------------|----------|------|
| `import pyscf`（版本探测） | **可接受**：仅写入 repro 元数据，不参与化学分支 | 可长期保留；与 driver 无关 |
| `_require_pyscf_reference` | **PySCF 专属能力**：需裸 `mf`（AO / AVAS / Schmidt 等） | 应用 capability 门控 + 清晰错误；见日历第 5–6 天 |
| `PySCFDriver` 导入 | **混合**：哈密顿量 / driver 高级 API | 默认哈密顿路径在 `supports_restricted_active_space_qubit_hamiltonian` 为真时使用；非 pyscf 后端应在此之前失败 |

## 2. `config.py`

| 模式 | 分类 | 备注 |
|------|------|------|
| `active_space.strategy=avas` 要求 `scf.driver=pyscf` | **阶段性产品约束** | 与「AVAS 为 PySCF 插件」一致；错误信息应同时提示 **capability**（日历第 15 天） |
| `MoleculeSpec.coordinates_in_bohr` 使用 `pyscf.gto` 解析 zmatrix | **几何解析依赖**：任何后端若用 zmatrix 当前走 PySCF | 中长期可抽到 `chem/geometry/` 中性模块 |

## 3. `quantum/`、`mitigation/`

- **已核对**（静态 grep）：`src/qchem_stack/quantum/`、`src/qchem_stack/mitigation/` 下 **无** `import pyscf` / `from pyscf`。

## 4. 关闭记录

- 2026-05-08 — 写入 `PLAN_START_DATE` 并建立 week W01-W13 周记骨架（执行台账就绪） — local workspace
- 2026-05-08 — 新增 capability 矩阵文档 `unified_chem_capabilities_matrix.md`，对齐 pipeline gate — local workspace
- 2026-05-08 — `SolverCapabilities` 新增 `supports_get_integrals`；PySCF/Psi4 显式声明 false — local workspace
- 2026-05-08 — pipeline 补充 capability 报错模板与 `_require_pyscf_reference` call-site TODO 标注 — local workspace
- 2026-05-08 — repro 元数据新增 `classical_software_versions`（保留 `pyscf_version` 兼容键） — local workspace
- 2026-05-08 — export/methods 视图新增 `scf_driver`、`solver_capabilities_snapshot`、`registered_solvers`、`classical_backend_id` — local workspace
- 2026-05-08 — 新增 mockchem capability gate 测试与 quantum 层 pyscf import 守卫测试 — local workspace
