"""Backend-neutral active-space resolution metadata (AVAS-derived sizing sync)."""

from __future__ import annotations

from typing import TYPE_CHECKING

RESOLVED_ACTIVE_SPACE_META_KEY = "qchem_active_space_resolution_v1"

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.config import ExperimentConfig


def patch_experiment_active_space_resolution(
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
) -> ExperimentConfig:
    """Synchronize YAML active-space sizing with AVAS-derived ``ncas`` / ``nelecas``."""
    meta = reference.driver_meta or {}
    res = meta.get(RESOLVED_ACTIVE_SPACE_META_KEY)
    if not isinstance(res, dict):
        return cfg
    n_a = res.get("n_active_orbitals")
    n_e = res.get("n_active_electrons")
    if n_a is None or n_e is None:
        return cfg
    n_act, n_el = int(n_a), int(n_e)
    a = cfg.active_space
    cur_n_orb = int(a.cas.n_orbitals)
    cur_n_el = int(a.cas.n_electrons)
    if cur_n_orb == n_act and cur_n_el == n_el:
        return cfg
    new_cas = a.cas.model_copy(update={"n_orbitals": n_act, "n_electrons": n_el})
    new_as = a.model_copy(update={"cas": new_cas})
    return cfg.model_copy(update={"active_space": new_as})
