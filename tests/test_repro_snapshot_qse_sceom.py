"""Parity snapshot includes QSE/SCEOM YAML fields (no PySCF)."""

from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.config import (
    ActiveSpaceSpec,
    ExperimentConfig,
    MoleculeSpec,
    QuantumSpec,
)
from qchem_stack.config.quantum_helpers import (
    PAULI_PATH_DISABLED,
    PAULI_PATH_EXACT,
    PAULI_PATH_STATEVECTOR_SHOT_SIM,
)
from qchem_stack.orchestration.pipeline import collect_repro_metadata
from tests.embedding_nested import embedding_dmet


def _minimal_cfg(**quantum_overrides: object) -> ExperimentConfig:
    quantum_data: dict = {
        "algorithm": "vqe",
        "vqe": {"depth": 1, "maxiter": 200},
        "pauli": {"use_protocol": True},
        "adapt": {"max_iter": 5},
        "iqeb": {"max_rounds": 2},
    }
    quantum_data.update(dict(quantum_overrides))
    return ExperimentConfig(
        schema_version="2",
        experiment_id="snap_qse",
        random_seed=1,
        molecule=MoleculeSpec(
            symbols=["H", "H"],
            coordinates=[[0, 0, 0], [0, 0, 1.4]],
            coordinate_unit="bohr",
        ),
        active_space=ActiveSpaceSpec.model_validate(
            {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
        ),
        quantum=QuantumSpec.model_validate(quantum_data),
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
            "embedding": embedding_dmet(
                fragment_labels=["A"],
                n_scf_cycles_embedding=3,
                classical_reference_method="NEVPT2",
            ),
            "mitigation": cfg.mitigation.model_copy(
                update={
                    "pmsv": cfg.mitigation.pmsv.model_copy(
                        update={
                            "enabled": True,
                            "stabilizers": ["Z0"],
                            "retention_rate": 0.88,
                        }
                    ),
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
        excited={
            "qse": {
                "after_variational": True,
                "shot_mode": "pauli_transitions",
                "shots_per_ij_term": 128,
                "max_basis": 6,
            },
            "sceom": {
                "after_variational": True,
                "shots_per_matrix_element": 200,
                "subspace_dim": 3,
            },
        }
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
        vqe={"depth": 2, "maxiter": 150},
        adapt={"max_iter": 8},
        pauli={
            "use_protocol": False,
            "run_sampled": True,
            "record_histograms": True,
        },
    )
    cfg = cfg.model_copy(
        update={
            "backend": cfg.backend.model_copy(update={"provider": "qiskit"}),
            "mitigation": cfg.mitigation.model_copy(
                update={"zne": cfg.mitigation.zne.model_copy(update={"enabled": True})}
            ),
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
    c2 = _minimal_cfg(pauli={"use_protocol": True, "run_sampled": True})
    s2 = collect_repro_metadata(c2)["parity_snapshot"]
    assert s2["pauli_protocol_expectation_path"] == PAULI_PATH_STATEVECTOR_SHOT_SIM


def test_embedding_whole_active_system_yaml_validation() -> None:
    from pydantic import ValidationError

    with pytest.raises(
        ValidationError, match="embedding.none.dmet|dmet_hamiltonian_source|embedding.mode"
    ):
        ExperimentConfig(
            schema_version="2",
            experiment_id="bad_mode",
            random_seed=0,
            molecule=MoleculeSpec(
                symbols=["H", "H"], coordinates=[[0, 0, 0], [0, 0, 1.4]], coordinate_unit="bohr"
            ),
            active_space=ActiveSpaceSpec.model_validate(
                {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
            ),
            embedding={
                "mode": "none",
                "dmet": {"hamiltonian_source": "whole_active_system", "fragment_labels": ["a"]},
            },
        )
    with pytest.raises(ValidationError, match="exactly one"):
        ExperimentConfig(
            schema_version="2",
            experiment_id="bad_frags",
            random_seed=0,
            molecule=MoleculeSpec(
                symbols=["H", "H"], coordinates=[[0, 0, 0], [0, 0, 1.4]], coordinate_unit="bohr"
            ),
            active_space=ActiveSpaceSpec.model_validate(
                {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
            ),
            embedding={
                "mode": "dmet",
                "dmet": {
                    "hamiltonian_source": "whole_active_system",
                    "fragment_labels": ["a", "b"],
                },
            },
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
