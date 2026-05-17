"""Hamiltonian fingerprint stability vs post-variational embedding audit."""

from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.chem.embedding.hamiltonian_semantics import pre_quantum_hamiltonian_semantics
from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync


def test_hamiltonian_semantics_none_mode() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    sem = pre_quantum_hamiltonian_semantics(cfg)
    assert sem["hamiltonian_branch"] == "canonical_active_space_integral_pack"
    assert sem["hamiltonian_fixed_before_variational"] is True
    assert sem["post_variational_embedding_audit_only"] is True


@pytest.mark.pyscf
def test_fingerprint_unchanged_after_variational_for_embedding_none() -> None:
    pytest.importorskip("pyscf")
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    out = run_pipeline_sync(cfg, cfg_path=root / "configs" / "example_h2.yaml")
    fp = out["pre_quantum_input"]["hamiltonian_fingerprint"]
    assert fp == out["hamiltonian_meta"]["hamiltonian_fingerprint"]
    assert out["pre_quantum_input"]["hamiltonian_fixed_before_variational"] is True
    ec = out["energy_components"]
    assert abs(float(out["scf_energy"]) - float(ec["mean_field_total_au"])) < 1e-8
    assert float(out["pre_quantum_input"]["reference_energy_au"]) == float(out["scf_energy"])
    ps = out["repro"]["parity_snapshot"]
    assert ps.get("pre_quantum_handoff_v1", {}).get("hamiltonian_fingerprint") == fp
    assert ps.get("pre_quantum_build_cache_v1", {}).get("pack_builds", 0) >= 1


@pytest.mark.pyscf
def test_schmidt_semantics_post_variational_audit_only() -> None:
    pytest.importorskip("pyscf")
    from qchem_stack.config import (
        ActiveSpaceSpec,
        BackendSpecConfig,
        EmbeddingSpec,
        ExperimentConfig,
        MoleculeSpec,
        QuantumSpec,
        SCFSpec,
    )

    cfg = ExperimentConfig(
        experiment_id="schmidt_sem",
        random_seed=0,
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates_bohr=[[0, 0, 0], [0, 0, 1.4]]),
        scf=SCFSpec(method="RHF"),
        active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
        backend=BackendSpecConfig(provider="statevector"),
        quantum=QuantumSpec(algorithm="vqe", vqe_depth=1, vqe_maxiter=10, use_pauli_protocol=False),
        embedding=EmbeddingSpec(
            mode="dmet",
            fragment_labels=["frag0"],
            dmet_hamiltonian_source="schmidt_atomic_production",
            schmidt_fragment_atom_indices=[0],
            schmidt_n_bath_spatial=1,
            schmidt_max_impurity_spatial_orbitals=8,
        ),
    )
    sem = pre_quantum_hamiltonian_semantics(cfg)
    assert sem["hamiltonian_branch"] == "schmidt_atomic_production"
    assert sem["post_variational_embedding_audit_only"] is True
    out = run_pipeline_sync(cfg)
    fp0 = out["pre_quantum_input"]["hamiltonian_fingerprint"]
    assert fp0 == out["hamiltonian_meta"]["hamiltonian_fingerprint"]
    assert out["pre_quantum_input"]["post_variational_embedding_audit_only"] is True
    assert out["pre_quantum_input"]["source"] == "schmidt_atomic_production"
