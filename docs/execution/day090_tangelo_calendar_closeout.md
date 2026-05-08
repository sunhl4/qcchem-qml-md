# Day90 — Tangelo gap calendar closeout (2026)

本文档作为 [`day001_day090_tangelo_gap_calendar.md`](day001_day090_tangelo_gap_calendar.md) 的 **封板签字稿**：对照日历三条主线，汇总已落地的工程产物与周闸门口径；**不**编辑上游计划文件本身。

## 周闸门（滚动验收）

1. **pytest**：相关子集随 PR；季度节点建议全量。
2. **`python scripts/check_parity_export_sample.py`**：抽样 YAML → export / contract 一致性。
3. **`inquanto_contract` / export / `RUN_SUMMARY_DOCUMENTED_KEYS`**：同源键注册。
4. **`docs/` 与 `docs-site/`**：入口互链抽检。
5. **新能力**：对应 **示例 YAML + 最小测试**。

## 主线交付对照

### Chem 契约（Day 1–30）

- **`energy_components_v1`**：`qchem_stack.chem.energy_components.build_energy_components_v1`，管线输出 `energy_components`；契约键与 export 镜像对齐。
- **Decomposition**：`decomposition_plugin_contract_v1` + 可选 `decomposition_fragment_energy_terms_v1`；示例 `configs/example_decomposition_plugin_contract.yaml` + `configs/decomposition_plugin_contract_integrals.json`。
- **Parity sample**：`scripts/check_parity_export_sample.py` 覆盖分解契约、AVAS stub、shadows stub 等 YAML。

### Tangelo 对齐 — 广度钉扎（Day 31–60）

- **Registry / 命名锚**：`quantum/ansatz_registry.py`（含 ADAPT 教程命名别名注释）；`chem/fermion_mapping_registry.py`（JKMN 等映射的白名单诚实边界）。
- **Mitigation**：`mitigation.classical_shadows_stub_enabled` — DAG 节点置于 SPAM 之后、PMSV 之前；迹一致性见 `tests/test_mitigation_dag_trace_homology.py`。
- **AVAS / CASSCF 诚实边界**：`active_space.strategy=avas_stub`（CAS 尺寸语义，**无**阈值投影）与 **`strategy=avas`**（PySCF **`mcscf.avas`**，`configs/example_h2_avas.yaml`）；**`casscf_orbital_optimization_for_integrals`** 与 audit 共用单次 CASSCF。**`chem.active_space.mean_field_meta`** / hooks → `hamiltonian_meta.pyscf_driver`；stub 示例仍见 `configs/example_h2_avas_stub.yaml`。

### 产品收口（Day 61–90）

- **三条用户路径**：见仓库根 [`examples/README.md`](../../examples/README.md)（教程脚本 / YAML 管线 / `md_bridge`）。
- **QMEF trainer smoke**：`tests/test_qmef_trainer_smoke.py`（`StubTorchMLIPTrainer`）。
- **契约稳定**：上述闸门 + `docs/inquanto_public_parity_matrix.md` 矩阵行更新（mitigation、经典化学 embedding）。

## _residual / 下一季度指针

- 真实 AVAS 投影、JKMN 等映射执行路径、Psi4 整条 driver：保持 **spike / 诚实 partial**，除非缩减其它包。
- Day91+ 节奏：[`day91_day120_daily_breakdown_2026Q3.md`](day91_day120_daily_breakdown_2026Q3.md)。
