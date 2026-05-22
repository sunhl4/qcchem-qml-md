"""Active-space sizing helpers (no PySCFDriver; spin classification uses lazy PySCF imports)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from qchem_stack.chem.active_space.resolution import RESOLVED_ACTIVE_SPACE_META_KEY

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.config import ActiveSpaceSpec


def classify_mean_field_spin_symmetry(mf: object) -> Literal["RHF", "ROHF", "UHF"]:
    from pyscf import scf as scf_mod

    if isinstance(mf, scf_mod.uhf.UHF):
        return "UHF"
    if isinstance(mf, scf_mod.rohf.ROHF):
        return "ROHF"
    return "RHF"


def ncas_nelec_couplet(
    active_space: ActiveSpaceSpec,
    *,
    reference: ClassicalMeanFieldReference | None = None,
) -> tuple[int, int]:
    """Return ``(n_active_orbitals, n_active_electrons)`` from reference meta or YAML spec."""
    if reference is not None:
        blk = reference.driver_meta.get(RESOLVED_ACTIVE_SPACE_META_KEY)
        if isinstance(blk, dict) and blk.get("n_active_orbitals") is not None:
            return int(blk["n_active_orbitals"]), int(blk["n_active_electrons"])  # type: ignore[index]
    from qchem_stack.config.active_space_helpers import resolve_n_electrons, resolve_n_orbitals

    return int(resolve_n_orbitals(active_space)), int(resolve_n_electrons(active_space))
