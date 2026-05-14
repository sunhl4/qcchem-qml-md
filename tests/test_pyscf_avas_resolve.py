"""AVAS projection + YAML active-space patch (PySCF numerical tests)."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from qchem_stack.config import ExperimentConfig, load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync


def test_experiment_validation_rejects_avas_without_labels() -> None:
    raw = {
        "schema_version": "1",
        "experiment_id": "bad_avas",
        "random_seed": 0,
        "molecule": {
            "symbols": ["H", "H"],
            "coordinates_bohr": [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
            "charge": 0,
            "multiplicity": 1,
            "basis": "sto-3g",
        },
        "scf": {"driver": "pyscf", "method": "RHF"},
        "active_space": {"strategy": "avas", "ncas": 2, "nelecas": 2},
        "chemistry_extended": {"avas_ao_labels": []},
        "quantum": {"use_pauli_protocol": False},
    }
    with pytest.raises(ValidationError, match="avas_ao_labels"):
        ExperimentConfig.from_yaml_dict(raw)


def test_experiment_validation_rejects_avas_on_psi4_driver() -> None:
    raw = {
        "schema_version": "1",
        "experiment_id": "bad_avas_driver",
        "random_seed": 0,
        "molecule": {
            "symbols": ["H", "H"],
            "coordinates_bohr": [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
            "charge": 0,
            "multiplicity": 1,
            "basis": "sto-3g",
        },
        "scf": {"driver": "psi4", "method": "RHF"},
        "active_space": {"strategy": "avas", "ncas": 2, "nelecas": 2},
        "chemistry_extended": {"avas_ao_labels": ["H 1s"]},
        "quantum": {"use_pauli_protocol": False},
    }
    with pytest.raises(ValidationError, match="scf.driver"):
        ExperimentConfig.from_yaml_dict(raw)


def test_pipeline_h2_avas_sets_resolution_and_executes_projection() -> None:
    pytest.importorskip("pyscf")
    root = Path(__file__).resolve().parents[1]
    p = root / "configs" / "example_h2_avas.yaml"
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    hm = out.get("hamiltonian_meta") or {}
    pd = hm.get("pyscf_driver") or {}
    assert pd.get("avas_atomic_projection_executed") is True
    res = pd.get("qchem_active_space_resolution_v1")
    assert isinstance(res, dict)
    assert res.get("source") == "pyscf_mcscf_avas_kernel_v1"
    assert int(res["n_active_orbitals"]) == 2
    assert int(res["n_active_electrons"]) == 2


def test_pyscf_driver_from_mean_field_and_ncas_helper() -> None:
    pytest.importorskip("pyscf")
    from pyscf import gto, scf

    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.drivers.pyscf_driver import PySCFDriver
    from qchem_stack.config import ActiveSpaceSpec

    mol = gto.M(atom="H 0 0 0; H 0 0 1.4", basis="sto3g")
    mf = scf.RHF(mol).run()
    drv = PySCFDriver.from_pyscf_mean_field(
        mf, active_space=ActiveSpaceSpec(strategy="cas", ncas=2, nelecas=2)
    )
    assert drv.classify_mean_field_spin_symmetry(mf) == "RHF"
    ref = ClassicalMeanFieldReference(
        mf=mf,
        e_tot=float(mf.e_tot),
        mo_energy=mf.mo_energy,
        molecular_system=drv.system,
        driver_meta={"upstream_classical_software_tag": "pyscf"},
    )
    assert drv.get_ncas_nelec_couplet(resolved_reference=ref) == (2, 2)
