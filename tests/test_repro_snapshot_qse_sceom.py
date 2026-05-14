"""Parity snapshot includes QSE/SCEOM YAML fields (no PySCF)."""

from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.config import (
    ActiveSpaceSpec,
    EmbeddingSpec,
    ExperimentConfig,
    MoleculeSpec,
    QuantumSpec,
)
from qchem_stack.orchestration.pipeline import collect_repro_metadata
from qchem_stack.protocols.inquanto_contract import (
    PAULI_PATH_DISABLED,
    PAULI_PATH_EXACT,
    PAULI_PATH_STATEVECTOR_SHOT_SIM,
)


def _minimal_cfg(**quantum_overrides: object) -> ExperimentConfig:
    q = QuantumSpec(**quantum_overrides)
    return ExperimentConfig(
        experiment_id="snap_qse",
        random_seed=1,
        molecule=MoleculeSpec(
            symbols=["H", "H"],
            coordinates_bohr=[[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
        ),
        active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
        quantum=q,
    )


def test_repro_includes_embedding_config_block() -> None:
    cfg = _minimal_cfg()
    r = collect_repro_metadata(cfg)
    emb = r.get("embedding_config")
    assert isinstance(emb, dict)
    assert emb.get("mode") == "none"


def test_parity_snapshot_embedding_and_pmsv_fields() -> None:
    cfg = _minimal_cfg()
    cfg = cfg.model_copy(
        update={
            "embedding": EmbeddingSpec(
                mode="dmet",
                n_scf_cycles_embedding=3,
                classical_reference_method="NEVPT2",
                fragment_labels=["A"],
            ),
            "mitigation": cfg.mitigation.model_copy(
                update={
                    "pmsv_enabled": True,
                    "pmsv_stabilizers": ["Z0"],
                    "pmsv_retention_rate": 0.88,
                }
            ),
        }
    )
    r = collect_repro_metadata(cfg)
    snap = r["parity_snapshot"]
    assert snap["embedding_mode"] == "dmet"
    assert snap["n_scf_cycles_embedding"] == 3
    assert snap["classical_reference_method"] == "NEVPT2"
    assert snap["embedding_fragment_labels"] == ["A"]
    assert snap["pmsv_enabled"] is True


def test_parity_snapshot_has_qse_sceom_from_config() -> None:
    cfg = _minimal_cfg(
        qse_after_variational=True,
        qse_shot_mode="pauli_transitions",
        qse_shots_per_ij_term=128,
        qse_max_basis=6,
        sceom_after_variational=True,
        sceom_shots_per_matrix_element=200,
        sceom_subspace_dim=3,
    )
    r = collect_repro_metadata(cfg)
    snap = r["parity_snapshot"]
    assert snap["qse_after_variational"] is True
    assert snap["qse_shot_mode"] == "pauli_transitions"
    assert snap["qse_shots_per_ij_term"] == 128
    assert snap["qse_max_basis"] == 6
    assert snap["sceom_after_variational"] is True
    assert snap["sceom_shots_per_matrix_element"] == 200
    assert snap["sceom_subspace_dim"] == 3


def test_parity_snapshot_variational_backend_mitigation_flags() -> None:
    cfg = _minimal_cfg(
        use_pauli_protocol=False,
        vqe_depth=2,
        vqe_maxiter=150,
        adapt_max_iter=8,
        run_sampled_pauli_protocol=True,
        record_pauli_measurement_histograms=True,
    )
    cfg = cfg.model_copy(
        update={
            "backend": cfg.backend.model_copy(update={"provider": "qiskit"}),
            "mitigation": cfg.mitigation.model_copy(update={"zne_enabled": True}),
        }
    )
    r = collect_repro_metadata(cfg)
    snap = r["parity_snapshot"]
    assert snap["use_pauli_protocol"] is False
    assert snap["vqe_depth"] == 2
    assert snap["vqe_maxiter"] == 150
    assert snap["adapt_max_iter"] == 8
    assert snap["iqeb_max_rounds"] == 2
    assert snap["run_sampled_pauli_protocol"] is True
    assert snap["record_pauli_measurement_histograms"] is True
    assert snap["backend_provider"] == "qiskit"
    assert snap["zne_enabled"] is True
    assert snap.get("run_qiskit_shots_pauli_protocol") is False
    assert snap["pauli_protocol_expectation_path"] == PAULI_PATH_DISABLED


def test_parity_snapshot_pauli_path_exact_vs_sampled() -> None:
    c1 = _minimal_cfg()
    s1 = collect_repro_metadata(c1)["parity_snapshot"]
    assert s1["pauli_protocol_expectation_path"] == PAULI_PATH_EXACT
    c2 = _minimal_cfg(run_sampled_pauli_protocol=True)
    s2 = collect_repro_metadata(c2)["parity_snapshot"]
    assert s2["pauli_protocol_expectation_path"] == PAULI_PATH_STATEVECTOR_SHOT_SIM


def test_embedding_whole_active_system_yaml_validation() -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError, match="embedding.mode"):
        ExperimentConfig(
            experiment_id="bad_mode",
            random_seed=0,
            molecule=MoleculeSpec(symbols=["H", "H"], coordinates_bohr=[[0, 0, 0], [0, 0, 1.4]]),
            active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
            embedding=EmbeddingSpec(
                mode="none",
                dmet_hamiltonian_source="whole_active_system",
                fragment_labels=["a"],
            ),
        )
    with pytest.raises(ValidationError, match="exactly one"):
        ExperimentConfig(
            experiment_id="bad_frags",
            random_seed=0,
            molecule=MoleculeSpec(symbols=["H", "H"], coordinates_bohr=[[0, 0, 0], [0, 0, 1.4]]),
            active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
            embedding=EmbeddingSpec(
                mode="dmet",
                dmet_hamiltonian_source="whole_active_system",
                fragment_labels=["a", "b"],
            ),
        )


def test_parity_snapshot_open_stack_extensions_default_on() -> None:
    cfg = _minimal_cfg()
    snap = collect_repro_metadata(cfg)["parity_snapshot"]
    assert snap.get("open_stack_contract_schema") == "parity_open_stack_contract_v1"
    assert "qnexus_probe" in snap
    assert snap.get("open_qermit_capability_matrix", {}).get("schema") == "qermit_open_reference_v1"
    assert (
        snap.get("tensornet_closure_reference", {}).get("schema")
        == "tensornet_closure_reference_v1"
    )
    assert "uccsd_reference_closed_shell" in snap
    assert snap["uccsd_reference_closed_shell"]["n_spin_orbitals"] == 4
    assert (
        snap.get("open_gap_closure_reference", {}).get("schema") == "open_gap_closure_reference_v1"
    )


def test_parity_integrations_disabled_skips_open_block() -> None:
    from qchem_stack.config import ParityIntegrationsSpec

    cfg = _minimal_cfg()
    cfg = cfg.model_copy(
        update={"parity_integrations": ParityIntegrationsSpec(enabled=False)},
    )
    snap = collect_repro_metadata(cfg)["parity_snapshot"]
    assert snap.get("open_stack_contract_schema") is None
    assert snap.get("parity_integrations", {}).get("enabled") is False


def test_parity_snapshot_projection_embedding_open_trace_from_packaged_yaml() -> None:
    from qchem_stack.config import load_experiment_config

    p = Path(__file__).resolve().parents[1] / "configs" / "example_h2_projection_trace.yaml"
    cfg = load_experiment_config(p)
    snap = collect_repro_metadata(cfg, cfg_path=p)["parity_snapshot"]
    pet = snap.get("projection_embedding_open_trace")
    assert isinstance(pet, dict)
    assert pet.get("schema") == "projection_embedding_open_trace_v1"
    assert pet.get("low_level") == "HF"
