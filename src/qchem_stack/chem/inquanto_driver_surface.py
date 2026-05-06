"""
InQuanto-PySCF *name* ↔ `qchem_stack` config keys (documentation + static validation).

Closed-source InQuanto drivers are not reproduced; this module is the **supported surface**
for parity tables and future PySCF hooks.

**与 `inquanto_public_parity_matrix.md` §3 对照**（L1）：

| InQuanto / 文档标签 | YAML / 行为 | 矩阵档位（§3） |
|----------------------|-------------|----------------|
| solvent_ddCOSMO / cosmo_like | `chemistry_extended.solvent_model=ddcosmo` | `partial`（PySCF `ddCOSMO`） |
| GeometryPeriodic / PBC | `chemistry_extended.pbc_cell_vectors_bohr` + `pbc_kpoint_mesh`（PySCF pbc RHF 或 KRHF） | `partial`（Γ→RHF，非 Γ→KRHF；k 网与 InQuanto 闭源 driver 非行级等价） |

PySCF **最低建议版本**见本模块 `PYSCF_MIN_VERSION_RECOMMENDED`（与 ``pyproject.toml`` optional `chem` extra 一致）；PBC+溶剂组合见矩阵「partial」列；本表**不**声称与闭源 `inquanto-pyscf` 行级一致。

**维护**：若上调 ``PYSCF_MIN_VERSION_RECOMMENDED``，请同步更新 [inquanto_public_parity_matrix.md](../../docs/inquanto_public_parity_matrix.md) §3 driver 备注、[Y1_residual_partial_SLA_template.md](../../docs/Y1_residual_partial_SLA_template.md) 中 ``drivers_cosmo_pbc`` 行与 ``tests/test_inquanto_driver_surface_l1.py``。
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
