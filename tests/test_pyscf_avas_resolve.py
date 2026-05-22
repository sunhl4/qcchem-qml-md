"""AVAS projection + YAML active-space patch (PySCF numerical tests)."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from qchem_stack.config import ExperimentConfig, load_experiment_config
from qchem_stack.exceptions import ConfigurationError
from qchem_stack.orchestration.pipeline import run_pipeline_sync


def test_experiment_validation_rejects_avas_without_labels() -> None:
    raw = {
        "schema_version": "2",
        "experiment_id": "bad_avas",
        "random_seed": 0,
        "molecule": {
            "symbols": ["H", "H"],
            "coordinates": [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
            "coordinate_unit": "bohr",
            "charge": 0,
            "multiplicity": 1,
            "basis": "sto-3g",
        },
        "scf": {"driver": "pyscf", "method": "RHF"},
        "active_space": {"strategy": "avas", "ncas": 2, "nelecas": 2},
        "chemistry_extended": {"avas_ao_labels": []},
        "quantum": {"use_pauli_protocol": False},
    }
    from qchem_stack.exceptions import ConfigurationError

    with pytest.raises((ValidationError, ConfigurationError), match="avas.ao_labels"):
        ExperimentConfig.from_yaml_dict(raw)


def test_experiment_validation_rejects_avas_on_driver_without_capability() -> None:
    from qchem_stack.chem.solvers.base import MolecularMeanFieldResult, SolverCapabilities
    from qchem_stack.chem.solvers.registry import register_solver
    from tests.helpers.solver_registry_state import reset_solver_registry_state

    reset_solver_registry_state()

    class _MockChemSolver:
        def __init__(self, cfg: ExperimentConfig) -> None:
            self.cfg = cfg

        @property
        def capabilities(self) -> SolverCapabilities:
            return SolverCapabilities(
                backend_id="mockchem",
                supports_molecular_scf=True,
                supports_avas_active_space_projection=False,
            )

        def set_physical_data(self, cfg: ExperimentConfig) -> None:
            self.cfg = cfg

        def compute_mean_field(self, *, periodic: bool = False) -> MolecularMeanFieldResult:
            import numpy as np

            return MolecularMeanFieldResult(
                mf={"backend": "mockchem"},
                e_tot=0.0,
                mo_energy=np.zeros(2),
                driver_meta={"driver_family": "mockchem"},
            )

    register_solver("mockchem", _MockChemSolver)
    raw = {
        "schema_version": "2",
        "experiment_id": "bad_avas_driver",
        "random_seed": 0,
        "molecule": {
            "symbols": ["H", "H"],
            "coordinates": [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
            "coordinate_unit": "bohr",
            "charge": 0,
            "multiplicity": 1,
            "basis": "sto-3g",
        },
        "scf": {"driver": "mockchem", "method": "RHF"},
        "active_space": {"strategy": "avas", "cas": {"n_orbitals": 2, "n_electrons": 2}},
        "chemistry_extended": {"avas": {"ao_labels": ["H 1s"]}},
        "quantum": {"algorithm": "vqe", "vqe": {"depth": 1, "maxiter": 5}},
        "embedding": {"mode": "none"},
    }
    with pytest.raises(ConfigurationError, match="supports_avas_active_space_projection"):
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


def test_mean_field_spin_symmetry_and_ncas_helper() -> None:
    pytest.importorskip("pyscf")
    import numpy as np
    from pyscf import gto, scf

    from qchem_stack.chem.active_space.sizing import (
        classify_mean_field_spin_symmetry,
        ncas_nelec_couplet,
    )
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.system import MolecularSystem
    from qchem_stack.config import ActiveSpaceSpec
    from qchem_stack.config.active_space_specs import ActiveSpaceCasSpec

    mol = gto.M(atom="H 0 0 0; H 0 0 1.4", basis="sto3g")
    mf = scf.RHF(mol).run()
    assert classify_mean_field_spin_symmetry(mf) == "RHF"
    ms = MolecularSystem(
        symbols=["H", "H"],
        coordinates_bohr=np.asarray([[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]], dtype=float),
        charge=0,
        multiplicity=1,
        basis="sto-3g",
    )
    ref = ClassicalMeanFieldReference(
        mf=mf,
        e_tot=float(mf.e_tot),
        mo_energy=mf.mo_energy,
        molecular_system=ms,
        driver_meta={"upstream_classical_software_tag": "pyscf"},
    )
    asp = ActiveSpaceSpec(strategy="cas", cas=ActiveSpaceCasSpec(n_orbitals=2, n_electrons=2))
    assert ncas_nelec_couplet(asp, reference=ref) == (2, 2)
