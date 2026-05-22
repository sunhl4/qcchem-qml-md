from __future__ import annotations

from qchem_stack.config import ExperimentConfig
from qchem_stack.config.quantum_helpers import (
    excited_qse_after_variational,
    excited_sceom_after_variational,
    pauli_protocol_enabled,
    pauli_record_histograms,
    pauli_run_qiskit_shots,
    pauli_run_sampled,
    qpe_demo_track_requested,
    qpe_three_pack_requested,
    quantum_repro_core_fields,
    quantum_repro_sidecar_fields,
    resolve_pauli_grouping,
    resolve_pauli_support_max_terms,
    resolve_uccsd_trotter_steps,
    resolve_vqe_maxiter,
    vqs_track_requested,
)


def test_resolve_vqe_maxiter_from_nested_quantum() -> None:
    cfg = ExperimentConfig.model_validate(
        {
            "experiment_id": "t",
            "molecule": {"symbols": ["H", "H"], "coordinates": [[0, 0, 0], [0, 0, 0.74]]},
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
            "quantum": {"vqe": {"maxiter": 42}},
        }
    )
    assert resolve_vqe_maxiter(cfg) == 42


def test_pauli_protocol_enabled() -> None:
    cfg = ExperimentConfig.model_validate(
        {
            "experiment_id": "t",
            "molecule": {"symbols": ["H", "H"], "coordinates": [[0, 0, 0], [0, 0, 0.74]]},
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
            "quantum": {"pauli": {"use_protocol": False}},
        }
    )
    assert pauli_protocol_enabled(cfg) is False


def test_excited_vqd_after_variational_default_false() -> None:
    cfg = ExperimentConfig.model_validate(
        {
            "experiment_id": "t",
            "molecule": {"symbols": ["H", "H"], "coordinates": [[0, 0, 0], [0, 0, 0.74]]},
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
        }
    )
    from qchem_stack.config.quantum_helpers import excited_vqd_after_variational

    assert excited_vqd_after_variational(cfg) is False
    assert excited_qse_after_variational(cfg) is False
    assert excited_sceom_after_variational(cfg) is False


def test_quantum_repro_core_fields_includes_algorithm() -> None:
    cfg = ExperimentConfig.model_validate(
        {
            "experiment_id": "t",
            "molecule": {"symbols": ["H", "H"], "coordinates": [[0, 0, 0], [0, 0, 0.74]]},
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
            "quantum": {"algorithm": "vqe", "vqe": {"maxiter": 10}},
        }
    )
    fields = quantum_repro_core_fields(cfg)
    assert fields["quantum_algorithm"] == "vqe"
    assert fields["vqe_maxiter"] == 10


def test_qpe_demo_track_requested_helper() -> None:
    cfg = ExperimentConfig.model_validate(
        {
            "experiment_id": "t",
            "molecule": {"symbols": ["H", "H"], "coordinates": [[0, 0, 0], [0, 0, 0.74]]},
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
            "quantum": {"demos": {"qpe": {"track_after_variational": True}}},
        }
    )
    assert qpe_demo_track_requested(cfg) is True
    assert vqs_track_requested(cfg) is False


def test_resolve_uccsd_trotter_steps_none_by_default() -> None:
    cfg = ExperimentConfig.model_validate(
        {
            "experiment_id": "t",
            "molecule": {"symbols": ["H", "H"], "coordinates": [[0, 0, 0], [0, 0, 0.74]]},
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
        }
    )
    assert resolve_uccsd_trotter_steps(cfg) is None


def test_pauli_run_helpers() -> None:
    cfg = ExperimentConfig.model_validate(
        {
            "experiment_id": "t",
            "molecule": {"symbols": ["H", "H"], "coordinates": [[0, 0, 0], [0, 0, 0.74]]},
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
            "quantum": {
                "pauli": {
                    "use_protocol": True,
                    "run_sampled": True,
                    "run_qiskit_shots": False,
                    "record_histograms": True,
                    "grouping": "greedy_commuting",
                    "support_max_terms": 128,
                }
            },
        }
    )
    assert pauli_protocol_enabled(cfg) is True
    assert pauli_run_sampled(cfg) is True
    assert pauli_run_qiskit_shots(cfg) is False
    assert pauli_record_histograms(cfg) is True
    assert resolve_pauli_grouping(cfg) == "greedy_commuting"
    assert resolve_pauli_support_max_terms(cfg) == 128


def test_quantum_repro_sidecar_fields_includes_sceom() -> None:
    cfg = ExperimentConfig.model_validate(
        {
            "experiment_id": "t",
            "molecule": {"symbols": ["H", "H"], "coordinates": [[0, 0, 0], [0, 0, 0.74]]},
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
            "quantum": {"excited": {"sceom": {"after_variational": True, "subspace_dim": 3}}},
        }
    )
    core = quantum_repro_core_fields(cfg)
    sidecar = quantum_repro_sidecar_fields(cfg)
    assert core["sceom_after_variational"] is True
    assert sidecar["sceom_subspace_dim"] == 3
    assert "vqd_overlap_exponent_yaml" in sidecar


def test_classify_pauli_expectation_path_for_config() -> None:
    cfg = ExperimentConfig.model_validate(
        {
            "experiment_id": "t",
            "molecule": {"symbols": ["H", "H"], "coordinates": [[0, 0, 0], [0, 0, 0.74]]},
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
            "quantum": {"pauli": {"use_protocol": False}},
        }
    )
    from qchem_stack.config.quantum_helpers import (
        PAULI_PATH_DISABLED,
        PAULI_PATH_EXACT,
        PAULI_PATH_STATEVECTOR_SHOT_SIM,
        classify_pauli_expectation_path_for_config,
        excited_any_after_variational,
    )

    assert classify_pauli_expectation_path_for_config(cfg) == PAULI_PATH_DISABLED
    assert excited_any_after_variational(cfg) is False
    cfg2 = ExperimentConfig.model_validate(
        {
            "experiment_id": "t",
            "molecule": {"symbols": ["H", "H"], "coordinates": [[0, 0, 0], [0, 0, 0.74]]},
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
            "quantum": {"pauli": {"use_protocol": True, "run_sampled": True}},
        }
    )
    assert classify_pauli_expectation_path_for_config(cfg2) == PAULI_PATH_STATEVECTOR_SHOT_SIM
    cfg3 = ExperimentConfig.model_validate(
        {
            "experiment_id": "t",
            "molecule": {"symbols": ["H", "H"], "coordinates": [[0, 0, 0], [0, 0, 0.74]]},
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
            "quantum": {"pauli": {"use_protocol": True}},
        }
    )
    assert classify_pauli_expectation_path_for_config(cfg3) == PAULI_PATH_EXACT


def test_quantum_excited_run_summary_yaml_fields() -> None:
    cfg = ExperimentConfig.model_validate(
        {
            "experiment_id": "t",
            "molecule": {"symbols": ["H", "H"], "coordinates": [[0, 0, 0], [0, 0, 0.74]]},
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
            "quantum": {
                "excited": {
                    "vqd": {"after_variational": True, "n_states": 3},
                    "qse": {"subspace_dim": 4},
                }
            },
        }
    )
    from qchem_stack.config.quantum_helpers import (
        excited_any_after_variational,
        quantum_excited_run_summary_yaml_fields,
    )

    assert excited_any_after_variational(cfg) is True
    fields = quantum_excited_run_summary_yaml_fields(cfg)
    assert fields["vqd_n_states_yaml"] == 3
    assert fields["qse_subspace_dim_yaml"] == 4


def test_quantum_variational_run_summary_yaml_fields() -> None:
    cfg = ExperimentConfig.model_validate(
        {
            "experiment_id": "t",
            "molecule": {"symbols": ["H", "H"], "coordinates": [[0, 0, 0], [0, 0, 0.74]]},
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
            "quantum": {
                "algorithm": "iqeb",
                "adapt": {"max_iter": 7, "pool_id": "fermionic_uccsd"},
                "iqeb": {"max_rounds": 4, "pool_id": "iqeb_qubit_excitation"},
            },
        }
    )
    from qchem_stack.config.quantum_helpers import (
        quantum_variational_run_summary_yaml_fields,
        quantum_workflow_preview_qpe_fields,
        quantum_workflow_preview_vqs_fields,
        resolve_adapt_max_iter,
        resolve_iqeb_max_rounds,
    )

    fields = quantum_variational_run_summary_yaml_fields(cfg)
    assert fields["adapt_max_iter_yaml"] == 7
    assert fields["iqeb_max_rounds_yaml"] == 4
    assert resolve_adapt_max_iter(cfg) == 7
    assert resolve_iqeb_max_rounds(cfg) == 4
    vqs = quantum_workflow_preview_vqs_fields(cfg)
    assert "vqs_mode" in vqs
    qpe = quantum_workflow_preview_qpe_fields(cfg)
    assert "qpe_demo_track_n_bits" in qpe


def test_excited_plugin_params_helpers() -> None:
    cfg = ExperimentConfig.model_validate(
        {
            "experiment_id": "t",
            "molecule": {"symbols": ["H", "H"], "coordinates": [[0, 0, 0], [0, 0, 0.74]]},
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
            "quantum": {
                "excited": {
                    "vqd": {"after_variational": True, "n_states": 3},
                    "qse": {"subspace_dim": 4, "shot_mode": "exact"},
                    "sceom": {"subspace_dim": 2, "generator_strategy": "legacy"},
                }
            },
        }
    )
    from qchem_stack.config.quantum_helpers import (
        excited_qse_plugin_params,
        excited_sceom_plugin_params,
        excited_vqd_plugin_params,
    )

    assert excited_vqd_plugin_params(cfg)["n_states"] == 3
    assert excited_qse_plugin_params(cfg)["subspace_dim"] == 4
    assert excited_sceom_plugin_params(cfg)["generator_strategy"] == "legacy"


def test_qpe_three_pack_requested_helper() -> None:
    cfg = ExperimentConfig.model_validate(
        {
            "experiment_id": "t",
            "molecule": {"symbols": ["H", "H"], "coordinates": [[0, 0, 0], [0, 0, 0.74]]},
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
            "quantum": {"demos": {"qpe": {"three_pack": {"after_variational": True}}}},
        }
    )
    assert qpe_three_pack_requested(cfg) is True
