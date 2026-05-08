"""``ChemistryProblemBundle`` snapshot from :class:`RestrictedActiveSpaceQuantumProblem`."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("pyscf")

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.drivers.pyscf_driver import PySCFDriver
from qchem_stack.chem.problem_bundle import ChemistryProblemBundle
from qchem_stack.config import load_experiment_config


def test_bundle_from_ras_problem_roundtrip_public_dump() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    drv = PySCFDriver.from_config(cfg)
    rhf = drv.run_rhf()
    ref = ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy,
        molecular_system=rhf.molecular_system,
        driver_meta=dict(rhf.driver_meta),
    )
    prob = drv.get_restricted_active_space_quantum_problem(2, 2, rhf=rhf)
    b = ChemistryProblemBundle.from_restricted_active_space_problem(prob, reference=ref)
    assert b.reference_energy_hf_au == pytest.approx(float(rhf.e_tot))
    assert b.backend_driver_meta.get("driver_family") == "pyscf"
    assert b.classical_mean_field_snapshot is ref
    pub = b.model_dump_public()
    assert pub["schema"] == "chemistry_problem_bundle_v1"
    assert pub["fermion_space"]["n_spin_orbitals"] == 4


def test_bundle_accepts_classical_reference_directly() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    drv = PySCFDriver.from_config(cfg)
    rhf = drv.run_rhf()
    ref = ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy,
        molecular_system=rhf.molecular_system,
        driver_meta=dict(rhf.driver_meta),
    )
    prob = drv.get_restricted_active_space_quantum_problem(2, 2, rhf=rhf)
    b = ChemistryProblemBundle.from_restricted_active_space_problem(prob, reference=ref)
    assert b.classical_mean_field_snapshot is ref
    assert b.reference_energy_hf_au == pytest.approx(float(rhf.e_tot))
