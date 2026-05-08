"""
InQuanto-PySCF *name* ↔ `qchem_stack` config keys (documentation + static validation).

Closed-source InQuanto drivers are not reproduced; this module is the **supported surface**
for parity tables and future PySCF hooks.

**与 `inquanto_public_parity_matrix.md` §3 对照**（L1）：

| InQuanto / 文档标签 | YAML / 行为 | 矩阵档位（§3） |
|----------------------|-------------|----------------|
| solvent_ddCOSMO / cosmo_like | `chemistry_extended.solvent_model=ddcosmo` | `partial`（PySCF `ddCOSMO`） |
| GeometryPeriodic / PBC | `chemistry_extended.pbc_cell_vectors_bohr` + `pbc_kpoint_mesh`（PySCF pbc RHF 或 KRHF） | `partial`（Γ→RHF，非 Γ→KRHF；k 网与 InQuanto 闭源 driver 非行级等价） |
| ActiveSpace (CAS / manual frozen / AVAS stub / AVAS(PySCF)) | `active_space.strategy=cas|manual|avas_stub|avas`（`cas` 用 `ncas/nelecas`；`manual` 用 `n_active_*` + `frozen_orbitals`；`avas_stub` **CAS 尺寸与 cas 等价** + `mean_field_meta` 诚实钩子；**`avas`**：PySCF `mcscf.avas.AVAS` 阈值投影，需非空 `chemistry_extended.avas_ao_labels`，管线写入 `qchem_active_space_resolution_v1` 回填尺寸）；`avas_ao_labels` 在非 `avas` strategy 下仍可 **仅日志** | `partial`（Psi4 等对 `avas` 能力门；闭源全菜单非行级等价） |
| Classical post-HF benchmark table | `chemistry_extended.classical_benchmark_enabled=true`（schema `qchem_classical_post_hf_benchmarks_v1`，`run_summary` 镜像 `classical_bench_*`） | `partial`（开放栈统一接口，非 InQuanto 产品默认组合） |
| Embedding pre-input representation | `embedding.embedding_input_representation=ao|lowdin_orth_ao`（输出 `embedding_input_system`） | `partial`（开放输入形态，非闭源嵌入产品等价） |
| RDM correction hook | `chemistry_extended.rdm_correction_method=stub_nevpt2|stub_ac0|pyscf_nevpt2_casci` | `partial`（stub：零校正；`pyscf_nevpt2_casci`：PySCF ``mrpt.NEVPT`` on CASCI，开放栈非 InQuanto L0） |

PySCF **最低建议版本**见本模块 `PYSCF_MIN_VERSION_RECOMMENDED`（与 ``pyproject.toml`` optional `chem` extra 一致）；PBC+溶剂组合见矩阵「partial」列；本表**不**声称与闭源 `inquanto-pyscf` 行级一致。

**维护**：若上调 ``PYSCF_MIN_VERSION_RECOMMENDED``，请同步更新 [inquanto_public_parity_matrix.md](../../docs/inquanto_public_parity_matrix.md) §3 driver 备注、[与InQuanto能力差距与实施计划 — 附录 B §6](../../docs/与InQuanto能力差距与实施计划.md#y1-residual-partial-sla-template) 中 ``drivers_cosmo_pbc`` 行与 ``tests/test_inquanto_driver_surface_l1.py``。
"""

from __future__ import annotations

# Optional dependency pin (see ``pyproject.toml`` ``[project.optional-dependencies] chem``).
PYSCF_MIN_VERSION_RECOMMENDED = "2.4"

# InQuanto / documentation common tags → YAML path under ``ExperimentConfig``.
INQUANTO_DRIVER_ALIAS_TO_CONFIG: dict[str, str] = {
    "solvent_ddCOSMO": "chemistry_extended.solvent_model=ddcosmo",
    "cosmo_like": "chemistry_extended.solvent_model=ddcosmo",
    "GeometryPeriodic": "chemistry_extended.pbc_cell_vectors_bohr + pbc_kpoint_mesh (PySCF pbc RHF or KRHF)",
    "PBC": "chemistry_extended.pbc_cell_vectors_bohr + pbc_kpoint_mesh (PySCF pbc RHF or KRHF)",
}

SUPPORTED_SOLVENT_MODELS: frozenset[str] = frozenset({"none", "ddcosmo"})
