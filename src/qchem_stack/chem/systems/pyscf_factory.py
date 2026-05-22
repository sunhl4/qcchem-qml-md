"""PySCF AO / Löwdin system views without :class:`PySCFDriver`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qchem_stack.chem.bridges.driver_meta import merge_driver_meta_updates
from qchem_stack.chem.integrals.pyscf_lowdin import build_lowdin_system_from_rhf
from qchem_stack.chem.systems.pyscf_views import PySCFAOSystem, PySCFLowdinSystem

if TYPE_CHECKING:
    from qchem_stack.chem.drivers.pyscf_driver_types import PySCFRHFResult
    from qchem_stack.config import ExperimentConfig


def pyscf_ao_system_from_rhf(rhf: PySCFRHFResult) -> PySCFAOSystem:
    """AO wrapper over a converged PySCF mean-field result."""
    meta = merge_driver_meta_updates(
        rhf.driver_meta,
        integral_representation="ao",
        ao_reference_kind="scf_object",
        ao_run_hf=True,
    )
    return PySCFAOSystem(
        mf=rhf.mf,
        molecular_system=rhf.molecular_system,
        driver_meta=meta,
        has_run_hf=True,
        e_tot=float(rhf.e_tot),
    )


def pyscf_ao_system_without_scf(cfg: ExperimentConfig) -> PySCFAOSystem:
    """AO tensors bound to an unconverged PySCF mean-field object (``run_hf=False`` analog)."""
    if cfg.chemistry_extended.pbc.cell_vectors_bohr is not None:
        raise ValueError("pyscf_ao_system_without_scf supports molecular branch only (non-PBC).")
    if str(cfg.scf.driver).strip().lower() != "pyscf":
        raise ValueError("pyscf_ao_system_without_scf requires scf.driver='pyscf'.")
    from qchem_stack.chem.molecular_system_config import molecular_system_from_experiment
    from qchem_stack.chem.solvers.pyscf_solver import PySCFIntegralSolver

    system = molecular_system_from_experiment(cfg)
    solver = PySCFIntegralSolver.from_experiment_config(cfg)
    mf = solver.build_molecular_mf_without_kernel()
    meta = merge_driver_meta_updates(
        solver.idle_molecular_driver_meta(),
        integral_representation="ao",
        ao_reference_kind="scf_object",
        ao_run_hf=False,
    )
    if cfg.chemistry_extended.solvent.model == "ddcosmo":
        meta.setdefault("solvent", "ddcosmo")
        meta.setdefault("ddcosmo_epsilon", float(cfg.chemistry_extended.solvent.epsilon))
    return PySCFAOSystem(
        mf=mf,
        molecular_system=system,
        driver_meta=meta,
        has_run_hf=False,
        e_tot=None,
    )


def pyscf_lowdin_system_from_rhf(rhf: PySCFRHFResult) -> PySCFLowdinSystem:
    """Löwdin-orthogonal AO integrals from a PySCF mean-field reference."""
    return build_lowdin_system_from_rhf(rhf, molecular_system=rhf.molecular_system)


def pyscf_ao_system_from_config(
    cfg: ExperimentConfig,
    *,
    run_hf: bool = True,
) -> PySCFAOSystem:
    from qchem_stack.chem.bridges.reference_factory import pyscf_rhf_result_from_config

    if run_hf:
        return pyscf_ao_system_from_rhf(pyscf_rhf_result_from_config(cfg))
    return pyscf_ao_system_without_scf(cfg)
