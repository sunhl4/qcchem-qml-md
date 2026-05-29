from __future__ import annotations

import json
import math

import pytest

pyscf = pytest.importorskip("pyscf")

from qchem_stack.config import load_experiment_config
from qchem_stack.integrations.methods_resource_unified import build_methods_resource_unified_v1
from qchem_stack.orchestration.pipeline import run_pipeline_from_config, run_pipeline_sync
from tests.helpers.h2_yaml import H2_STO3G_FCI_ENERGY, write_h2_pipeline_yaml
from tests.helpers.paths import configs_path


def test_run_pipeline_sync_h2(tmp_path) -> None:
    cfg_path = write_h2_pipeline_yaml(
        tmp_path / "h2.yaml",
        experiment_id="orch_test",
        backend={"shots_per_circuit": 512},
        quantum={"vqe": {"maxiter": 120}, "pauli": {"use_protocol": True}},
    )
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    assert "scf_energy" in out
    assert "energy_pauli_protocol" in out
    assert out["repro"]["config_sha256_prefix"]
    assert out["embedding_workflow"]["mode"] == "none"
    assert out["repro"]["embedding_workflow"]["mode"] == "none"
    wp = out["repro"].get("workflow_preview_v1")
    assert isinstance(wp, dict) and wp.get("schema") == "workflow_preview_v1"
    snap = out["repro"]["parity_snapshot"]
    assert snap["pauli_grouping"] == "tensor_product"
    assert snap["hamiltonian_meta"]["fermion_to_qubit_map"] == "jordan_wigner"
    assert snap["hamiltonian_meta"]["n_active_orbitals"] == 2
    pd = snap["hamiltonian_meta"].get("pyscf_driver") or {}
    assert pd.get("active_space_strategy") == "cas"
    assert str(pd.get("active_space_recipe", "")).startswith("cas:")
    rs = out["resource_summary"]
    assert rs["n_circuits"] >= 1
    assert rs["n_pauli_terms"] is not None and rs["n_pauli_terms"] >= 1
    assert rs["n_pauli_groups"] is not None and rs["n_pauli_groups"] >= 0
    assert rs.get("pauli_averaging_protocol_ran") is True
    assert "excited_stages" not in rs
    ar = out.get("algorithm_report")
    assert isinstance(ar, dict)
    assert ar.get("schema") == "algorithm_vqe_report_v1"
    assert out["repro"]["run_summary"].get("algorithm_report_schema") == "algorithm_vqe_report_v1"


def test_run_pipeline_sync_h2_with_classical_benchmarks(tmp_path) -> None:
    cfg_path = write_h2_pipeline_yaml(
        tmp_path / "h2_bench.yaml",
        experiment_id="orch_test_bench",
        backend={"shots_per_circuit": 256},
        quantum={"vqe": {"maxiter": 20}, "pauli": {"use_protocol": False}},
        chemistry_extended={"benchmarks": {"enabled": True}},
    )
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    cb = out.get("classical_benchmarks")
    assert isinstance(cb, dict)
    assert cb.get("schema") == "qchem_classical_post_hf_benchmarks_v1"
    assert isinstance(cb.get("hf"), dict)
    assert cb["hf"].get("status") == "ok"
    cbs = out.get("classical_benchmark_summary")
    assert isinstance(cbs, dict)
    assert cbs.get("schema") == "classical_benchmark_summary_v1"
    assert cbs.get("recommended_baseline_policy") == "prefer_ccsd_else_mp2_else_hf"
    assert cbs.get("recommended_baseline_method") in ("ccsd", "mp2", "hf", None)
    assert cbs.get("reference_hf_energy_au") is not None
    assert isinstance(cbs.get("method_deltas_vs_hf_au"), dict)
    rsum = out["repro"]["run_summary"]
    assert rsum.get("classical_benchmarks_present") is True
    assert rsum.get("classical_benchmarks_schema") == "qchem_classical_post_hf_benchmarks_v1"
    assert rsum.get("classical_benchmark_summary_present") is True
    assert rsum.get("classical_benchmark_summary_schema") == "classical_benchmark_summary_v1"
    if cbs.get("recommended_baseline_method") is not None:
        assert (
            rsum.get("classical_benchmark_recommended_baseline_method")
            == cbs["recommended_baseline_method"]
        )


def test_qpe_dual_track_yaml_runs_via_pipeline() -> None:
    p = configs_path("qpe_dual_track_demo.yaml")
    cfg = load_experiment_config(p)
    assert cfg.quantum.demos.qpe.pipeline_integration is True
    out = run_pipeline_sync(cfg, cfg_path=p)
    qdt = out["qpe_demo_track"]
    assert qdt["schema"] == "qpe_qec_demo_track_v1"
    pec = qdt.get("phase_estimation_contract_v1") or {}
    assert pec.get("schema") == "phase_estimation_contract_v1"
    assert "kitaev_ground_energy_dense" in qdt
    assert isinstance(qdt.get("bayesian_phase_map_toy"), dict)
    assert math.isfinite(float(out["energy_after_variational"]))
    assert out["repro"]["run_summary"].get("qpe_demo_track_ran") is True
    qp = out["repro"].get("workflow_preview_qpe_track_v1")
    assert isinstance(qp, dict) and qp.get("schema") == "workflow_preview_qpe_track_v1"
    assert qp.get("qpe_pipeline_integration") is True
    wp = out["repro"].get("workflow_preview_v1") or {}
    assert wp.get("qpe_track_execution") == qp


def _run_adapt_pool_yaml(pool_yaml: str, expected_pool_id: str) -> None:
    p = configs_path(pool_yaml)
    if not p.is_file():
        pytest.skip(f"configs/{pool_yaml} missing")
    cfg = load_experiment_config(p)
    assert cfg.quantum.adapt.pool_id == expected_pool_id
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert isinstance(out["repro"]["run_summary"].get("adapt_pool_id_yaml"), str)
    assert math.isfinite(float(out["energy_after_variational"]))


@pytest.mark.parametrize(
    ("pool_yaml", "expected_pool_id"),
    [
        ("example_h2_adapt_singles_pool.yaml", "fermionic_uccsd_singles"),
        ("example_h2_adapt_doubles_pool.yaml", "fermionic_uccsd_doubles_only"),
    ],
)
def test_adapt_pool_yaml_runs_via_pipeline(pool_yaml: str, expected_pool_id: str) -> None:
    _run_adapt_pool_yaml(pool_yaml, expected_pool_id)


@pytest.mark.parametrize(
    ("pool_yaml", "pool_field", "expected_pool_id", "algorithm"),
    [
        (
            "example_h2_adapt_uccsd_jw_alias.yaml",
            "adapt",
            "uccsd_jw",
            "adapt",
        ),
        (
            "example_h2_iqeb_fermionic_doubles_pool.yaml",
            "iqeb",
            "fermionic_uccsd_doubles_only",
            "iqeb",
        ),
        (
            "example_h2_iqeb_qubit_excitation_alias.yaml",
            "iqeb",
            "qubit_excitation",
            "iqeb",
        ),
    ],
)
def test_adapt_iqeb_pool_alias_yaml_runs_via_pipeline(
    pool_yaml: str,
    pool_field: str,
    expected_pool_id: str,
    algorithm: str,
) -> None:
    p = configs_path(pool_yaml)
    if not p.is_file():
        pytest.skip(f"configs/{pool_yaml} missing")
    cfg = load_experiment_config(p)
    if pool_field == "adapt":
        assert cfg.quantum.adapt.pool_id == expected_pool_id
    else:
        assert cfg.quantum.iqeb.pool_id == expected_pool_id
    out = run_pipeline_sync(cfg, cfg_path=p)
    rsum = out["repro"]["run_summary"]
    if pool_field == "adapt":
        assert rsum.get("adapt_pool_id_yaml") == expected_pool_id
    else:
        assert rsum.get("iqeb_pool_id_yaml") == expected_pool_id
    assert math.isfinite(float(out["energy_after_variational"]))
    ar = out.get("algorithm_report")
    assert isinstance(ar, dict)
    assert ar.get("algorithm") == algorithm


def test_vqs_track_yaml_runs_via_pipeline() -> None:
    p = configs_path("example_h2_vqs_track.yaml")
    if not p.is_file():
        pytest.skip("configs/example_h2_vqs_track.yaml missing")
    cfg = load_experiment_config(p)
    assert cfg.quantum.demos.vqs.pipeline_integration is True
    out = run_pipeline_sync(cfg, cfg_path=p)
    vt = out["vqs_track"]
    assert vt["schema"] == "vqs_track_v1"
    vic = vt.get("vqs_integration_contract_v1") or {}
    assert vic.get("schema") == "vqs_integration_contract_v1"
    assert vt["times"]
    assert len(vt["final_parameters"]) == len(vt["initial_parameters"])
    assert int(vt.get("n_steps", 0)) >= 1
    rsum = out["repro"]["run_summary"]
    assert rsum.get("vqs_track_ran") is True
    vcon = rsum.get("vqs_open_stack_contract_v1")
    assert isinstance(vcon, dict) and vcon.get("schema") == "vqs_open_stack_contract_v1"
    uni = build_methods_resource_unified_v1(out)
    assert uni.get("schema") == "methods_resource_unified_v1"
    assert uni.get("run_summary_vqs_track_ran") is True
    assert isinstance(uni.get("vqs_open_stack_contract_v1"), dict)


def test_run_pipeline_sync_h2_qpe_demo_track(tmp_path) -> None:
    cfg_path = write_h2_pipeline_yaml(
        tmp_path / "h2qpe.yaml",
        experiment_id="orch_qpe",
        quantum={
            "vqe": {"maxiter": 40},
            "pauli": {"use_protocol": True},
            "demos": {"qpe": {"track_after_variational": True}},
        },
    )
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    assert "qpe_demo_track" in out
    assert out["qpe_demo_track"]["schema"] == "qpe_qec_demo_track_v1"
    assert out["repro"]["run_summary"].get("qpe_demo_track_ran") is True
    assert "kitaev_ground_energy_dense" in out["qpe_demo_track"]


def test_run_pipeline_sync_h2_vqd_yaml_shots(tmp_path) -> None:
    cfg_path = write_h2_pipeline_yaml(
        tmp_path / "h2_vqd.yaml",
        experiment_id="orch_vqd",
        random_seed=3,
        backend={"shots_per_circuit": 256},
        quantum={
            "vqe": {"maxiter": 80},
            "pauli": {"use_protocol": False},
            "excited": {
                "vqd": {
                    "after_variational": True,
                    "n_states": 2,
                    "shots_objective": 100,
                    "shots_overlap": 80,
                    "shots_weight": 80,
                }
            },
        },
    )
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    assert "vqd" in out
    assert out["vqd"].get("schema") == "excited_vqd_bundle_v1"
    assert len(out["vqd"]["energies"]) == 2
    assert out["vqd"]["meta"].get("reused_pipeline_ground") is True
    assert out["vqd"]["energies"][0] == pytest.approx(out["energy_after_variational"])
    assert out["excited_resource_summary"]["vqd"]["n_states"] == 2
    epc = out["excited_resource_summary"].get("excited_protocol_contract_v1") or {}
    assert epc.get("schema") == "excited_protocol_contract_v1"
    snap = out["repro"]["parity_snapshot"]
    assert snap["vqd_shots_objective"] == 100
    assert snap["vqd_shots_overlap"] == 80
    tp = out["vqd"]["meta"]["vqd_channels"][1]["three_protocol"]
    assert tp["objective"].get("energy_shot_mean") is not None
    rs = out["resource_summary"]
    assert rs["pauli_averaging_protocol_ran"] is False
    assert rs["excited_stages"]["vqd"]["n_states"] == 2
    assert rs["excited_shots_upper_bound"] > 0
    assert rs["sum_shots_total_with_excited_upper_bound"] == rs["excited_shots_upper_bound"]
    rsum = out["repro"]["run_summary"]
    assert rsum.get("vqd_three_protocol_present") is True
    assert rsum.get("vqd_n_energies_recorded") == 2
    assert rsum.get("vqd_deflation_levels_completed") == 1
    assert rsum.get("vqd_channels_count") == 2
    assert rsum.get("vqd_shots_objective_yaml") == 100


def test_run_pipeline_sync_h2_qse_sceom_yaml(tmp_path) -> None:
    cfg_path = write_h2_pipeline_yaml(
        tmp_path / "h2_excited.yaml",
        experiment_id="orch_qse_sceom",
        random_seed=7,
        backend={"shots_per_circuit": 256},
        quantum={
            "vqe": {"maxiter": 60},
            "pauli": {"use_protocol": False},
            "excited": {
                "qse": {
                    "after_variational": True,
                    "subspace_dim": 4,
                    "shot_mode": "exact",
                },
                "sceom": {
                    "after_variational": True,
                    "subspace_dim": 2,
                    "shots_per_matrix_element": 0,
                },
            },
        },
    )
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    assert "qse" in out
    assert out["qse"]["schema"] == "excited_qse_bundle_v1"
    assert out["qse"]["excitation_energies"]
    assert out["qse"]["meta"].get("K", 0) >= 1
    assert "sceom" in out
    assert len(out["sceom"]["energies"]) >= 1
    assert out["sceom"]["schema"] == "excited_sceom_bundle_v1"
    snap = out["repro"]["parity_snapshot"]
    assert snap["qse_after_variational"] is True
    assert snap["qse_shot_mode"] == "exact"
    assert snap["sceom_after_variational"] is True
    assert "qse" in out["excited_resource_summary"]
    assert "sceom" in out["excited_resource_summary"]
    rs = out["resource_summary"]
    assert rs["pauli_averaging_protocol_ran"] is False
    assert "qse" in rs["excited_stages"] and "sceom" in rs["excited_stages"]
    rsum = out["repro"]["run_summary"]
    assert rsum.get("qse_shot_mode") == "exact"
    assert rsum.get("sceom_shot_noise_model") == "none"
    assert rsum.get("sceom_shots_per_matrix_element") == 0
    assert out["qse"]["meta"].get("qse_shot_mode") == "exact"
    assert rsum.get("qse_n_excitation_energies") == len(out["qse"]["excitation_energies"])
    assert rsum.get("qse_basis_dimension_K") == out["qse"]["meta"].get("K")
    assert rsum.get("sceom_n_energies_recorded") == len(out["sceom"]["energies"])
    assert rsum.get("sceom_active_generator_count") == 2
    assert rsum.get("sceom_matrix_construction") is not None


def test_run_pipeline_sync_h2_qse_pauli_transitions_run_summary(tmp_path) -> None:
    cfg_path = write_h2_pipeline_yaml(
        tmp_path / "h2_qse_pauli.yaml",
        experiment_id="orch_qse_pauli",
        random_seed=7,
        backend={"shots_per_circuit": 256},
        quantum={
            "vqe": {"maxiter": 60},
            "pauli": {"use_protocol": False},
            "excited": {
                "qse": {
                    "after_variational": True,
                    "subspace_dim": 4,
                    "shot_mode": "pauli_transitions",
                    "shots_per_ij_term": 32,
                }
            },
        },
    )
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    assert "qse" in out
    rsum = out["repro"]["run_summary"]
    assert rsum.get("qse_shot_mode") == "pauli_transitions"
    assert rsum.get("qse_shot_noise_model") == "grouped_statevector_shot_simulation_per_ij_term"
    assert out["qse"]["meta"].get("qse_shot_mode") == "pauli_transitions"


def test_run_pipeline_sync_h2_adapt_then_vqd(tmp_path) -> None:
    cfg_path = write_h2_pipeline_yaml(
        tmp_path / "h2_adapt_vqd.yaml",
        experiment_id="orch_adapt_vqd",
        random_seed=11,
        backend={"shots_per_circuit": 256},
        quantum={
            "algorithm": "adapt",
            "adapt": {"max_iter": 2},
            "vqe": {"depth": 1},
            "pauli": {"use_protocol": False},
            "excited": {"vqd": {"after_variational": True, "n_states": 2}},
        },
    )
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    assert out["algorithm"] == "adapt"
    assert "adapt_meta" in out
    ar = out.get("algorithm_report")
    assert isinstance(ar, dict)
    assert ar.get("algorithm") == "adapt"
    assert out["repro"]["run_summary"].get("algorithm_report_algorithm") == "adapt"
    assert out["vqd"]["meta"].get("reused_pipeline_ground") is True
    assert out["vqd"]["energies"][0] == pytest.approx(out["energy_after_variational"])


def test_run_pipeline_sync_h2_vqd_and_pauli_protocol(tmp_path) -> None:
    cfg_path = write_h2_pipeline_yaml(
        tmp_path / "h2_vqd_pauli.yaml",
        experiment_id="orch_vqd_pauli",
        random_seed=5,
        backend={"shots_per_circuit": 400},
        quantum={
            "vqe": {"maxiter": 100},
            "pauli": {"use_protocol": True},
            "excited": {
                "vqd": {
                    "after_variational": True,
                    "n_states": 2,
                    "shots_objective": 50,
                    "shots_overlap": 40,
                }
            },
        },
    )
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    assert "energy_pauli_protocol" in out
    rs = out["resource_summary"]
    assert rs["pauli_averaging_protocol_ran"] is True
    assert rs["excited_stages"]["vqd"]["n_states"] == 2
    assert rs["excited_shots_upper_bound"] > 0
    assert rs["sum_shots_total_with_excited_upper_bound"] >= rs["sum_shots"]


def test_run_pipeline_with_job_db(tmp_path) -> None:
    cfg_path = write_h2_pipeline_yaml(
        tmp_path / "h2b.yaml",
        experiment_id="job_orch",
        random_seed=2,
        backend={"shots_per_circuit": 256},
        quantum={"pauli": {"use_protocol": True}},
    )
    db = tmp_path / "jobs.sqlite"
    out = run_pipeline_from_config(cfg_path, job_db=db)
    assert "job_result" in out
    assert out["job_result"]["expectation"] is not None
    rsum = out["repro"]["run_summary"]
    assert rsum.get("async_job_id") == out["job"]["job_id"]
    assert rsum.get("protocol_hash_prefix") == out["job"]["protocol_hash"]
    assert rsum.get("protocol_total_shots_budget") is not None
    assert rsum.get("job_async_expectation") is not None


def test_tutorial_chain_h2_yaml_runs() -> None:
    p = configs_path("tutorial_chain_h2.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert out.get("embedding_workflow", {}).get("mode") == "dmet"
    assert len(out["embedding_workflow"]["fragment_labels"]) == 1
    snap = out["repro"]["parity_snapshot"]
    assert snap.get("compiler_bundle_signature")
    assert snap.get("compiler_preoptimize_passes") == ["qubit_reuse_hint"]
    assert snap.get("mitigation_execution_class") == "shot_postselect"
    assert snap.get("open_stack_contract_schema") == "parity_open_stack_contract_v1"
    assert snap.get("dmet_open_loop_architecture", {}).get("schema") == "dmet_open_architecture_v1"
    assert snap.get("dmet_one_shot_open_ledger", {}).get("schema") == "dmet_one_shot_v1"
    assert snap.get("dmet_solver_mode") == "parity_stub"
    rsum = out["repro"]["run_summary"]
    assert rsum.get("dmet_one_shot_open_ledger_present") is True
    assert rsum.get("dmet_embedding_active") is True
    assert rsum.get("dmet_hamiltonian_source_yaml") == "parity_stub"
    assert "energy_pauli_protocol" in out
    pc = out["protocol_counts"]
    assert pc.get("hamiltonian_pauli_term_records")


def test_dmet_whole_active_system_impurity_vqe_matches_global_vqe() -> None:
    from qchem_stack.config import (
        ActiveSpaceSpec,
        BackendSpecConfig,
        ExperimentConfig,
        MoleculeSpec,
        QuantumSpec,
        SCFSpec,
    )
    from tests.embedding_nested import embedding_dmet

    cfg = ExperimentConfig(
        schema_version="2",
        experiment_id="dmet_whole_h2",
        random_seed=7,
        molecule=MoleculeSpec(
            symbols=["H", "H"], coordinates=[[0, 0, 0], [0, 0, 1.4]], coordinate_unit="bohr"
        ),
        scf=SCFSpec(method="RHF"),
        active_space=ActiveSpaceSpec.model_validate(
            {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
        ),
        backend=BackendSpecConfig(provider="statevector"),
        quantum=QuantumSpec(
            algorithm="vqe",
            vqe={"depth": 1, "maxiter": 120},
            pauli={"use_protocol": False},
        ),
        embedding=embedding_dmet(
            fragment_labels=["impurity"],
            hamiltonian_source="whole_active_system",
            n_scf_cycles_embedding=1,
        ),
    )
    out = run_pipeline_sync(cfg)
    e0 = float(out["energy_after_variational"])
    row = out["dmet_fragment_solve"]["fragments"][0]
    assert row["solver"] == "QubitHamiltonianFragmentSolverVQE"
    assert float(row["energy"]) == pytest.approx(e0, rel=1e-10, abs=1e-10)
    assert out["embedding_workflow"]["dmet_hamiltonian_source"] == "whole_active_system"
    assert out["repro"]["parity_snapshot"]["dmet_solver_mode"] == "whole_active_system"
    rsum = out["repro"]["run_summary"]
    assert rsum.get("dmet_embedding_active") is True
    assert rsum.get("dmet_fragment_solve_present") is True
    assert rsum.get("dmet_fragment_solve_schema") == "dmet_one_shot_v1"
    assert rsum.get("dmet_hamiltonian_source_yaml") == "whole_active_system"


def test_run_pipeline_sync_packaged_h2_vqd_uccsd_yaml() -> None:
    """UCCSD ground + VQD deflation on the same UCCSD parameterization (open-stack P3 path)."""
    p = configs_path("example_h2_vqd_uccsd.yaml")
    if not p.is_file():
        pytest.skip("configs/example_h2_vqd_uccsd.yaml missing")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert out["vqe_meta"].get("variational_ansatz") == "uccsd"
    vqd = out.get("vqd") or {}
    assert vqd.get("schema") == "excited_vqd_bundle_v1"
    assert len(vqd["energies"]) == 2
    meta = vqd["meta"]
    assert meta.get("vqd_variety_yaml") == "uccsd"
    assert meta.get("reused_pipeline_ground") is True
    assert meta.get("vqd_overlap_mode_yaml") == cfg.quantum.excited.vqd.overlap_mode
    assert isinstance(meta.get("tangelo_deflation_analogy_v1"), dict)
    assert isinstance(meta.get("vqd_cross_stack_semantics_v1"), dict)
    assert vqd["energies"][0] == pytest.approx(float(out["energy_after_variational"]))
    rsum = out["repro"]["run_summary"]
    assert rsum.get("vqd_variety_yaml") == "uccsd"
    assert rsum.get("vqd_overlap_mode_yaml") == cfg.quantum.excited.vqd.overlap_mode


def test_run_pipeline_sync_packaged_h2_uccsd_yaml() -> None:
    p = configs_path("example_h2_uccsd.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert out["algorithm"] == "vqe"
    vm = out.get("vqe_meta")
    assert isinstance(vm, dict)
    assert vm.get("variational_ansatz") == "uccsd"
    assert vm.get("jw_fixed_electron_sector_projection") is True
    assert int(vm["uccsd_n_parameters"]) >= 1
    ev = float(out["energy_after_variational"])
    assert math.isfinite(ev)
    scf_e = float(out["scf_energy"])
    assert scf_e < -1.0
    # UCCSD on Tangelo-aligned Hamiltonian: between sto-3g FCI and RHF for H₂(2e, CAS(2,2)).
    assert ev <= scf_e + 1e-3
    assert ev >= H2_STO3G_FCI_ENERGY - 5e-3
    snap = out["repro"]["parity_snapshot"]
    assert snap["variational_ansatz"] == "uccsd"
    assert snap["uccsd_n_parameters"] == int(vm["uccsd_n_parameters"])
    rsum = out["repro"]["run_summary"]
    assert rsum["variational_ansatz_yaml"] == "uccsd"
    assert rsum["uccsd_n_parameters"] == int(vm["uccsd_n_parameters"])
    ar = out.get("algorithm_report")
    assert isinstance(ar, dict)
    assert ar.get("schema") == "algorithm_uccsd_report_v1"
    assert rsum.get("algorithm_report_schema") == "algorithm_uccsd_report_v1"
    rs = out["resource_summary"]
    assert rs["pauli_averaging_protocol_ran"] is False
    assert "energy_pauli_protocol" not in out


def test_run_pipeline_sync_packaged_h2_uccsd_pauli_protocol_yaml() -> None:
    p = configs_path("example_h2_uccsd_pauli_protocol.yaml")
    if not p.is_file():
        pytest.skip("configs/example_h2_uccsd_pauli_protocol.yaml missing")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert out["vqe_meta"].get("variational_ansatz") == "uccsd"
    ev = float(out["energy_after_variational"])
    assert math.isfinite(ev)
    rs = out["resource_summary"]
    assert rs["pauli_averaging_protocol_ran"] is True
    epp = out.get("energy_pauli_protocol")
    assert epp is not None
    assert math.isfinite(float(epp))
    snap = out["repro"]["parity_snapshot"]
    assert snap.get("pauli_protocol_expectation_path") == "statevector_grouped_shot_simulation"
    prep = out["protocol_counts"].get("ansatz_prep") or {}
    assert prep.get("ansatz_kind") == "uccsd"


def test_run_pipeline_sync_classical_shadows_stub_e2e() -> None:
    p = configs_path("example_h2_classical_shadows_stub.yaml")
    if not p.is_file():
        pytest.skip("configs/example_h2_classical_shadows_stub.yaml missing")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    dex = out.get("mitigation_dag_execution")
    assert isinstance(dex, dict)
    trace = dex.get("trace") or []
    assert trace and trace[0].get("node") == "classical_shadows_expectation_stub"
    assert trace[0].get("computable_runtime") == "classical_shadows_hamiltonian_expectation"
    assert out.get("classical_shadows_computable_runtime") is not None


def test_run_pipeline_sync_packaged_h2_vqd_three_computable_yaml() -> None:
    p = configs_path("example_h2_vqd_uccsd_three_computable.yaml")
    if not p.is_file():
        pytest.skip("configs/example_h2_vqd_uccsd_three_computable.yaml missing")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    vqd = out.get("vqd") or {}
    meta = vqd.get("meta") or {}
    assert meta.get("vqd_optimizer_mode") == "three_computable"
    assert len(meta.get("vqd_optimizer_trace") or []) >= 1


def test_run_pipeline_sync_packaged_h2_uccsd_qse_pauli_qiskit_yaml() -> None:
    pytest.importorskip("qiskit")
    p = configs_path("example_h2_uccsd_qse_pauli_qiskit.yaml")
    if not p.is_file():
        pytest.skip("configs/example_h2_uccsd_qse_pauli_qiskit.yaml missing")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    qse = out.get("qse") or {}
    meta = qse.get("meta") or {}
    assert meta.get("qse_shot_mode") == "pauli_transitions_qiskit"
    assert meta.get("computable_runtime") == "QSEMatricesComputable"
    assert len(qse.get("excitation_energies") or []) >= 1


def test_run_pipeline_sync_packaged_h2_vqd_deflation_circuit_yaml() -> None:
    pytest.importorskip("qiskit")
    p = configs_path("example_h2_vqd_deflation_circuit.yaml")
    if not p.is_file():
        pytest.skip("configs/example_h2_vqd_deflation_circuit.yaml missing")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    vqd = out.get("vqd") or {}
    meta = vqd.get("meta") or {}
    assert meta.get("vqd_overlap_mode_yaml") == "deflation_circuit"
    tda = meta.get("tangelo_deflation_analogy_v1") or {}
    recipe = tda.get("deflation_circuit_recipe_v1") or {}
    assert recipe.get("qiskit_export_v1", {}).get("twoq_gate_count", 0) >= 1


def test_run_pipeline_sync_packaged_h2_uccsd_trotter_yaml() -> None:
    p = configs_path("example_h2_uccsd_trotter.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    vm = out["vqe_meta"]
    assert vm.get("uccsd_trotter_steps") == 2
    assert vm.get("uccsd_product_formula") == "first_order_layer_repeat"
    assert vm.get("jw_fixed_electron_sector_projection") is True
    snap = out["repro"]["parity_snapshot"]
    assert snap["uccsd_trotter_steps"] == 2


def test_run_pipeline_sync_fe_helike_sto3g_cas22_smoke_yaml() -> None:
    p = configs_path("example_fe_sto3g_helike_rhf_cas22.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert out["hamiltonian_meta"]["n_qubits"] == 4
    assert math.isfinite(float(out["scf_energy"]))
    assert math.isfinite(float(out["energy_after_variational"]))


def test_run_pipeline_sync_oniom_toy_yaml_sets_embedding_layers() -> None:
    p = configs_path("example_oniom_toy.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    wf = out.get("embedding_workflow") or {}
    ot = wf.get("oniom_toy_v1")
    assert isinstance(ot, dict)
    assert ot.get("schema") == "oniom_toy_v1"
    assert len(ot.get("layers") or []) == 2


def test_run_pipeline_sync_h2_casscf_audit_yaml() -> None:
    p = configs_path("example_h2_casscf_audit.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    hm = out.get("hamiltonian_meta") or {}
    pd = hm.get("pyscf_driver") or {}
    audit = pd.get("casscf_orbital_audit_v1")
    assert isinstance(audit, dict)
    assert audit.get("schema") == "casscf_orbital_audit_v1"
    assert "casscf_energy_au" in audit
    assert audit.get("mo_coeff_rotated_into_casscf") is False


def test_run_pipeline_sync_packaged_h2_iqeb_yaml() -> None:
    p = configs_path("example_h2_iqeb.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert out["algorithm"] == "iqeb"
    assert isinstance(out.get("iqeb_meta"), dict)
    assert out["iqeb_meta"].get("rounds") == 2
    assert isinstance(out.get("iqeb_selected_pauli_strings"), list)
    rsum = out["repro"]["run_summary"]
    assert rsum["quantum_algorithm"] == "iqeb"
    assert rsum.get("iqeb_implementation_path") == "qchem_stack.quantum.algorithms.iqeb.IQEBVQE"
    assert rsum.get("iqeb_max_rounds_yaml") == 2
    snap = out["repro"]["parity_snapshot"]
    assert snap["quantum_algorithm"] == "iqeb"
    assert snap["iqeb_max_rounds"] == 2


def test_run_pipeline_sync_packaged_projection_trace_yaml() -> None:
    p = configs_path("example_h2_projection_trace.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    wf = out.get("embedding_workflow", {})
    assert wf.get("mode") == "projection"
    assert wf.get("schema") == "projection_embedding_workflow_v1"
    assert wf.get("projection_quantum_hamiltonian") == "global_active_space"
    assert "projection_low_level" in wf
    snap = out["repro"]["parity_snapshot"]
    pet = snap.get("projection_embedding_open_trace")
    assert isinstance(pet, dict)
    assert pet.get("schema") == "projection_embedding_open_trace_v1"
    assert pet.get("projection_hamiltonian_source") == "global_active_space"
    blob = str(pet)
    assert "not wired" not in blob.lower()
    stages = out["repro"]["run_summary"]["stages_completed"]
    assert "projection_embedding_trace" in stages
    assert "energy_pauli_protocol" in out


def test_run_pipeline_sync_projection_mulliken_h4_yaml() -> None:
    p = configs_path("example_h4_projection_mulliken.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert out["hamiltonian_meta"].get("integral_source") == "pyscf_projection_fragment_mulliken_v1"
    wf = out.get("embedding_workflow", {})
    assert wf.get("projection_quantum_hamiltonian") == "fragment_mulliken_mo"
    assert wf.get("projection_selected_mo_indices")
    stages = out["repro"]["run_summary"]["stages_completed"]
    assert "projection_embedding_trace" in stages
    snap = out["repro"]["parity_snapshot"]
    pet = snap.get("projection_embedding_open_trace")
    assert pet.get("projection_hamiltonian_source") == "fragment_mulliken_mo_v1"
    assert "not wired" not in json.dumps(snap).lower()
