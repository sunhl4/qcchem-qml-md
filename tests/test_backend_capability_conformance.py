from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.embedding.projection_hamiltonian import (
    molecular_hamiltonian_fragment_mulliken_projection,
)
from qchem_stack.chem.embedding.schmidt_production import (
    SchmidtProductionError,
    build_schmidt_impurity_integrals,
)
from qchem_stack.chem.solvers import create_solver, register_mock_external_solver
from qchem_stack.chem.system import MolecularSystem
from qchem_stack.config import load_experiment_config
from qchem_stack.exceptions import EmbeddingError, PipelineError
from qchem_stack.integrations.rdm_corrections import run_pyscf_nevpt2_casci_correction
from qchem_stack.integrations.schmidt_dmet_self_consistent import (
    run_schmidt_density_feedback_cycles,
)
from qchem_stack.orchestration.pipeline import run_pipeline_sync


def test_builtin_backend_capability_matrix_smoke() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    cfg.scf.driver = "psi4"
    psi4 = create_solver(cfg).capabilities
    assert not psi4.supports_restricted_active_space_qubit_hamiltonian
    assert not psi4.supports_projection_fragment_mulliken_hamiltonian
    assert not psi4.supports_schmidt_atomic_hamiltonian
    assert not psi4.supports_embedding_input_ao_lowdin
    assert not psi4.supports_casscf_orbital_audit
    assert not psi4.supports_avas_active_space_projection
    assert not psi4.supports_rdm_correction_hooks
    assert not psi4.supports_rdm_nevpt2_casci
    assert not psi4.supports_get_integrals

    pytest.importorskip("pyscf")
    cfg.scf.driver = "pyscf"
    pyscf = create_solver(cfg).capabilities
    assert pyscf.supports_restricted_active_space_qubit_hamiltonian
    assert pyscf.supports_projection_fragment_mulliken_hamiltonian
    assert pyscf.supports_schmidt_atomic_hamiltonian
    assert pyscf.supports_embedding_input_ao_lowdin
    assert pyscf.supports_casscf_orbital_audit
    assert pyscf.supports_avas_active_space_projection
    assert pyscf.supports_rdm_correction_hooks
    assert pyscf.supports_rdm_nevpt2_casci
    assert pyscf.supports_get_integrals


def test_canonical_pack_requires_backend_builder() -> None:
    ref = ClassicalMeanFieldReference(
        mf=object(),
        e_tot=0.0,
        mo_energy=np.zeros(1, dtype=float),
        molecular_system=MolecularSystem(
            symbols=["H"],
            coordinates_bohr=np.zeros((1, 3), dtype=float),
            basis="sto-3g",
        ),
        driver_meta={"upstream_classical_software_tag": "psi4"},
    )
    with pytest.raises(NotImplementedError, match="from_classical_reference"):
        CanonicalActiveSpaceIntegralPack.from_classical_reference(
            ref,
            n_active_orbitals=1,
            n_active_electrons=0,
        )


def test_rdm_correction_gate_requires_backend_capability() -> None:
    root = Path(__file__).resolve().parents[1]
    p = root / "configs" / "example_decomposition_plugin_toy.yaml"
    cfg = load_experiment_config(p)
    register_mock_external_solver()
    cfg.scf.driver = "mock_external"
    cfg.chemistry_extended.rdm_correction_method = "stub_nevpt2"
    with pytest.raises(
        PipelineError, match="rdm_correction_method requires backend RDM extraction support"
    ):
        run_pipeline_sync(cfg, cfg_path=p)


def test_projection_and_schmidt_builders_require_pyscf_backend_tag() -> None:
    ref = ClassicalMeanFieldReference(
        mf=object(),
        e_tot=0.0,
        mo_energy=np.zeros(1, dtype=float),
        molecular_system=MolecularSystem(
            symbols=["H"],
            coordinates_bohr=np.zeros((1, 3), dtype=float),
            basis="sto-3g",
        ),
        driver_meta={"upstream_classical_software_tag": "psi4"},
    )
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h4_projection_mulliken.yaml")
    with pytest.raises(EmbeddingError, match="currently implemented on the PySCF backend"):
        molecular_hamiltonian_fragment_mulliken_projection(ref, cfg)
    with pytest.raises(SchmidtProductionError, match="currently implemented for backend='pyscf'"):
        build_schmidt_impurity_integrals(
            ref,
            fragment_atom_indices=[0],
            n_bath_orbitals=1,
            max_impurity_spatial_orbitals=2,
        )
    with pytest.raises(SchmidtProductionError, match="requires backend='pyscf'"):
        run_schmidt_density_feedback_cycles(
            ref,
            fragment_atom_indices=[0],
            n_bath_orbitals=1,
            max_impurity_spatial_orbitals=2,
            max_cycles=1,
            mixing_alpha=0.3,
            convergence_tol=1e-4,
        )
    rep = run_pyscf_nevpt2_casci_correction(ref, n_active_orbitals=1, n_active_electrons=0)
    assert rep.get("status") == "failed"
    assert "backend_not_supported" in str((rep.get("pyscf_nevpt2") or {}).get("reason"))
