"""Build :class:`ClassicalMeanFieldReference` from experiment config via the solver bridge."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qchem_stack.chem.active_space.mean_field_meta import annotate_mean_field_reference_active_space
from qchem_stack.chem.bridges.facade import classical_mean_field_via_solver_bridge
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.molecular_system_config import molecular_system_from_experiment

if TYPE_CHECKING:
    from qchem_stack.chem.drivers.pyscf_driver_types import PySCFRHFResult
    from qchem_stack.config import ExperimentConfig


def classical_mean_field_reference_from_config(
    cfg: ExperimentConfig,
) -> ClassicalMeanFieldReference:
    """Run SCF through the registry-backed bridge and return interchange reference."""
    pack = classical_mean_field_via_solver_bridge(cfg)
    ref = ClassicalMeanFieldReference.from_mean_field_pack(
        pack,
        molecular_system=molecular_system_from_experiment(cfg),
    )
    return annotate_mean_field_reference_active_space(cfg, ref)


def pyscf_rhf_result_from_config(cfg: ExperimentConfig) -> PySCFRHFResult:
    """PySCF-native result container for code paths that still expect :class:`PySCFRHFResult`."""
    ref = classical_mean_field_reference_from_config(cfg)
    tag = ref.backend_tag()
    if tag != "pyscf":
        raise ValueError(f"pyscf_rhf_result_from_config requires scf.driver='pyscf' (got {tag!r}).")
    return ref.as_pyscf_rhf_result()
