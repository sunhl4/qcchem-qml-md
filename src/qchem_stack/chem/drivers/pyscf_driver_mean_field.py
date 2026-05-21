"""Mean-field execution helpers for :class:`~qchem_stack.chem.drivers.pyscf_driver.PySCFDriver`."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from qchem_stack.chem.bridges.interchange import merge_canonical_classical_bridge_headers
from qchem_stack.chem.drivers.pyscf_driver_types import PySCFRHFResult

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.drivers.pyscf_driver import PySCFDriver


def mean_field_reference_for_benchmarks(
    driver: PySCFDriver,
    rhf: PySCFRHFResult | ClassicalMeanFieldReference | None,
) -> ClassicalMeanFieldReference:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference

    if rhf is None:
        pr = run_molecular_mean_field(driver)
        meta = dict(pr.driver_meta)
        meta.setdefault("upstream_classical_software_tag", "pyscf")
        return ClassicalMeanFieldReference(
            mf=pr.mf,
            e_tot=float(pr.e_tot),
            mo_energy=np.asarray(pr.mo_energy, dtype=float),
            molecular_system=driver.system,
            driver_meta=meta,
        )
    if isinstance(rhf, ClassicalMeanFieldReference):
        return rhf
    meta = dict(rhf.driver_meta)
    meta.setdefault("upstream_classical_software_tag", "pyscf")
    return ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=np.asarray(rhf.mo_energy, dtype=float),
        molecular_system=rhf.molecular_system,
        driver_meta=meta,
    )


def run_molecular_mean_field(driver: PySCFDriver) -> PySCFRHFResult:
    run = driver._integral_solver().compute_mean_field(periodic=False)
    meta = dict(run.driver_meta)
    if driver.chemistry_extended.solvent.model == "ddcosmo":
        meta.setdefault("solvent", "ddcosmo")
        meta.setdefault("ddcosmo_epsilon", float(driver.chemistry_extended.solvent.epsilon))
    meta = merge_canonical_classical_bridge_headers(
        meta,
        upstream_software_tag="pyscf",
        periodic_boundary_condition=False,
    )
    return PySCFRHFResult(
        mf=run.mf,
        e_tot=run.e_tot,
        mo_energy=run.mo_energy,
        molecular_system=driver.system,
        driver_meta=meta,
    )


def run_pbc_mean_field(driver: PySCFDriver) -> PySCFRHFResult:
    run = driver._integral_solver().compute_mean_field(periodic=True)
    meta = dict(run.driver_meta)
    if driver.chemistry_extended.solvent.model == "ddcosmo":
        meta.setdefault("solvent", "ddcosmo")
        meta.setdefault("ddcosmo_epsilon", float(driver.chemistry_extended.solvent.epsilon))
    meta = merge_canonical_classical_bridge_headers(
        meta,
        upstream_software_tag="pyscf",
        periodic_boundary_condition=True,
    )
    return PySCFRHFResult(
        mf=run.mf,
        e_tot=run.e_tot,
        mo_energy=run.mo_energy,
        molecular_system=driver.system,
        driver_meta=meta,
    )
