"""repro.run_summary attachment after pipeline (no PySCF)."""

from __future__ import annotations

from qchem_stack.config import (
    ActiveSpaceSpec,
    EmbeddingSpec,
    ExperimentConfig,
    MoleculeSpec,
    QuantumSpec,
)
from qchem_stack.orchestration.pipeline import _attach_run_summary, collect_repro_metadata


def _base_cfg(quantum: QuantumSpec) -> ExperimentConfig:
    return ExperimentConfig(
        experiment_id="rsum",
        random_seed=0,
        molecule=MoleculeSpec(
            symbols=["H", "H"],
            coordinates_bohr=[[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
        ),
        active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
        quantum=quantum,
    )


def test_attach_run_summary_stages_and_protocol_semantics() -> None:
    cfg = _base_cfg(
        QuantumSpec(
            use_pauli_protocol=True,
            vqd_after_variational=True,
            qse_after_variational=True,
        )
    )
    out: dict = {
        "repro": collect_repro_metadata(cfg),
        "scf_energy": -1.99,
        "energy_after_variational": -1.23,
        "vqd": {"meta": {"reused_pipeline_ground": True}},
        "qse": {"excitation_energies": [0.1], "meta": {}},
        "energy_pauli_protocol": -1.1,
        "resource_summary": {
            "sum_shots": 100,
            "pauli_averaging_protocol_ran": True,
            "sum_shots_total_with_excited_upper_bound": 250,
            "excited_shots_upper_bound": 150,
            "n_pauli_terms": 7,
            "n_pauli_groups": 3,
            "n_circuits": 4,
            "n_qubits": 2,
        },
        "protocol_counts": {
            "expectation_source": "statevector_exact",
            "energy_stderr_model": "classical_bound",
            "total_shots_budget": 999,
            "n_measurement_circuits": 3,
            "shots_per_circuit_effective": 512,
            "energy_stderr": 0.01,
        },
    }
    _attach_run_summary(out, cfg)
    sm = out["repro"]["run_summary"]
    assert sm["stages_completed"] == [
        "scf",
        "variational",
        "vqd",
        "qse",
        "pauli_averaging_protocol",
    ]
    assert sm["protocol_expectation_source"] == "statevector_exact"
    assert sm["protocol_energy_stderr_model"] == "classical_bound"
    assert sm["protocol_total_shots_budget"] == 999
    assert sm["protocol_n_measurement_circuits"] == 3
    assert sm["protocol_shots_per_circuit_effective"] == 512
    assert sm["protocol_energy_stderr"] == 0.01
    assert sm["sum_shots_backend_protocol"] == 100
    assert sm["vqd_reused_pipeline_ground"] is True
    assert sm["sum_shots_total_with_excited_upper_bound"] == 250
    assert sm["scf_energy"] == -1.99
    assert sm["energy_pauli_protocol"] == -1.1
    assert sm["n_pauli_terms"] == 7
    assert sm["n_pauli_groups"] == 3
    assert sm["n_circuits"] == 4
    assert sm["n_qubits"] == 2
    assert sm["pauli_protocol_expectation_path"] == "exact_executor"
    assert sm["vqe_maxiter_yaml"] == 200
    assert "vqe_nfev" not in sm
    assert sm.get("vqd_n_states_yaml") == 2
    assert "vqd_n_energies_recorded" not in sm
    assert sm.get("qse_subspace_dim_yaml") == 4
    assert sm.get("qse_n_excitation_energies") == 1


def test_attach_run_summary_includes_scf_and_vqe_counters() -> None:
    cfg = _base_cfg(QuantumSpec(algorithm="vqe", vqe_maxiter=300, use_pauli_protocol=False))
    out: dict = {
        "repro": collect_repro_metadata(cfg),
        "scf_energy": -1.88,
        "energy_after_variational": -1.5,
        "nfev": 42,
    }
    _attach_run_summary(out, cfg)
    sm = out["repro"]["run_summary"]
    assert sm["scf_energy"] == -1.88
    assert sm["vqe_maxiter_yaml"] == 300
    assert sm["vqe_nfev"] == 42


def test_attach_run_summary_adapt_meta() -> None:
    cfg = _base_cfg(QuantumSpec(algorithm="adapt", adapt_max_iter=4, use_pauli_protocol=False))
    out: dict = {
        "repro": collect_repro_metadata(cfg),
        "scf_energy": -1.0,
        "energy_after_variational": -1.2,
        "adapt_meta": {
            "total_gradient_evals": 99,
            "adapt_steps": [{"iteration": 0}, {"iteration": 1}],
        },
        "adapt_pool": [(0, 1)],
    }
    _attach_run_summary(out, cfg)
    sm = out["repro"]["run_summary"]
    assert sm["quantum_algorithm"] == "adapt"
    assert sm["adapt_max_iter_yaml"] == 4
    assert sm["adapt_total_gradient_evals"] == 99
    assert sm["adapt_steps_recorded"] == 2
    assert sm["adapt_excitation_layers"] == 1


def test_attach_run_summary_iqeb() -> None:
    cfg = _base_cfg(QuantumSpec(algorithm="iqeb", iqeb_max_rounds=3, use_pauli_protocol=False))
    out: dict = {
        "repro": collect_repro_metadata(cfg),
        "scf_energy": -1.0,
        "energy_after_variational": -1.2,
        "nfev": 77,
        "iqeb_meta": {"rounds": 3},
        "iqeb_selected_pauli_strings": ["ZZ_round0", "ZZ_round1"],
    }
    _attach_run_summary(out, cfg)
    sm = out["repro"]["run_summary"]
    assert sm["quantum_algorithm"] == "iqeb"
    assert sm["iqeb_max_rounds_yaml"] == 3
    assert sm["iqeb_outer_rounds_recorded"] == 3
    assert sm["iqeb_selected_pauli_count"] == 2
    assert sm["iqeb_final_inner_vqe_nfev"] == 77
    assert sm["iqeb_implementation_path"] == "qchem_stack.quantum.algorithms.iqeb.IQEBVQE"


def test_attach_run_summary_includes_job_worker_expectation() -> None:
    cfg = _base_cfg(QuantumSpec(use_pauli_protocol=True))
    out: dict = {
        "repro": collect_repro_metadata(cfg),
        "job_result": {
            "expectation": -1.111,
            "energy_stderr": 0.02,
            "total_shots_budget": 888,
        },
    }
    _attach_run_summary(out, cfg)
    sm = out["repro"]["run_summary"]
    assert sm["job_async_expectation"] == -1.111
    assert sm["job_async_energy_stderr"] == 0.02
    assert sm["job_async_total_shots_budget"] == 888


def test_attach_run_summary_includes_async_job_metadata() -> None:
    cfg = _base_cfg(QuantumSpec(use_pauli_protocol=True))
    out: dict = {
        "repro": collect_repro_metadata(cfg),
        "job": {"job_id": "jid-1", "protocol_hash": "phash9"},
    }
    _attach_run_summary(out, cfg)
    sm = out["repro"]["run_summary"]
    assert sm["async_job_id"] == "jid-1"
    assert sm["protocol_hash_prefix"] == "phash9"


def test_parity_snapshot_includes_vqd_penalty_weight() -> None:
    cfg = _base_cfg(QuantumSpec(vqd_penalty_weight=2.5, vqd_after_variational=True))
    r = collect_repro_metadata(cfg)
    assert r["parity_snapshot"]["vqd_penalty_weight"] == 2.5


def test_attach_run_summary_vqd_energy_and_shot_yaml() -> None:
    cfg = _base_cfg(
        QuantumSpec(
            vqd_after_variational=True,
            vqd_n_states=2,
            vqd_shots_objective=10,
            vqd_shots_overlap=20,
            vqd_shots_weight=30,
            use_pauli_protocol=False,
        )
    )
    out: dict = {
        "repro": collect_repro_metadata(cfg),
        "scf_energy": -1.0,
        "energy_after_variational": -1.2,
        "vqd": {
            "energies": [-1.2, -0.5],
            "meta": {
                "reused_pipeline_ground": True,
                "vqd_channels": [
                    {"level": 0, "three_protocol": {"a": 1}},
                    {"level": 1, "three_protocol": {"b": 2}},
                ],
                "shots_objective": 10,
                "shots_overlap": 20,
                "shots_weight": 30,
            },
        },
    }
    _attach_run_summary(out, cfg)
    sm = out["repro"]["run_summary"]
    assert sm["vqd_n_energies_recorded"] == 2
    assert sm["vqd_deflation_levels_completed"] == 1
    assert sm["vqd_channels_count"] == 2
    assert sm["vqd_three_protocol_present"] is True
    assert sm["vqd_shots_objective_yaml"] == 10
    assert sm["vqd_shots_overlap_yaml"] == 20
    assert sm["vqd_shots_weight_yaml"] == 30


def test_attach_run_summary_qse_schedule_fields() -> None:
    cfg = _base_cfg(
        QuantumSpec(
            qse_after_variational=True,
            qse_subspace_dim=4,
            qse_max_basis=5,
            qse_shot_mode="pauli_transitions",
            use_pauli_protocol=False,
        )
    )
    out: dict = {
        "repro": collect_repro_metadata(cfg),
        "scf_energy": -1.0,
        "energy_after_variational": -1.2,
        "qse": {
            "excitation_energies": [0.1, 0.2],
            "meta": {
                "K": 3,
                "shot_noise_model": "independent_complex_gaussian_per_ij_term",
                "qse_pauli_transition_schedule": {
                    "n_transition_tasks": 9,
                    "total_shots_upper_bound": 900,
                },
            },
        },
    }
    _attach_run_summary(out, cfg)
    sm = out["repro"]["run_summary"]
    assert sm["qse_basis_dimension_K"] == 3
    assert sm["qse_n_excitation_energies"] == 2
    assert sm["qse_n_transition_tasks"] == 9
    assert sm["qse_total_shots_upper_bound"] == 900
    assert sm["qse_max_basis_yaml"] == 5


def test_attach_run_summary_sceom_nested_meta() -> None:
    cfg = _base_cfg(
        QuantumSpec(
            sceom_after_variational=True,
            sceom_subspace_dim=2,
            sceom_shots_per_matrix_element=128,
            use_pauli_protocol=False,
        )
    )
    out: dict = {
        "repro": collect_repro_metadata(cfg),
        "scf_energy": -1.0,
        "energy_after_variational": -1.2,
        "sceom": {
            "energies": [-1.0, -0.9],
            "meta": {
                "subspace_dim": 2,
                "construction": "M_ij=<psi|[Si,[H,Sj]]|psi> with Pauli toy generators",
                "shot_noise_model": "symmetric_gaussian_on_real_M",
            },
        },
    }
    _attach_run_summary(out, cfg)
    sm = out["repro"]["run_summary"]
    assert sm["sceom_n_energies_recorded"] == 2
    assert sm["sceom_active_generator_count"] == 2
    assert "Pauli toy" in sm["sceom_matrix_construction"]


def test_attach_run_summary_dmet_embedding_flags() -> None:
    cfg = ExperimentConfig(
        experiment_id="dmet_rsum",
        random_seed=0,
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates_bohr=[[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]]),
        active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
        quantum=QuantumSpec(use_pauli_protocol=False),
        embedding=EmbeddingSpec(
            mode="dmet",
            fragment_labels=["A", "B"],
            dmet_hamiltonian_source="parity_stub",
            dmet_uniform_multifragment_toy=True,
        ),
    )
    out: dict = {
        "repro": collect_repro_metadata(cfg),
        "scf_energy": -1.0,
        "energy_after_variational": -1.2,
        "dmet_fragment_solve": {"schema": "dmet_one_shot_v1", "fragments": []},
    }
    _attach_run_summary(out, cfg)
    sm = out["repro"]["run_summary"]
    assert sm["dmet_embedding_active"] is True
    assert sm["dmet_hamiltonian_source_yaml"] == "parity_stub"
    assert sm["dmet_fragment_count"] == 2
    assert sm["dmet_uniform_multifragment_toy_yaml"] is True
    assert sm["dmet_fragment_solve_present"] is True
    assert sm["dmet_fragment_solve_schema"] == "dmet_one_shot_v1"
