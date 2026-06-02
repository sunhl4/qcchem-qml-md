from __future__ import annotations

import math

import pytest

pyscf = pytest.importorskip("pyscf")

from qchem_stack.config import load_experiment_config
from qchem_stack.integrations.methods_resource_unified import build_methods_resource_unified_v1
from qchem_stack.orchestration.pipeline import run_pipeline_from_config, run_pipeline_sync
from tests.helpers.h2_yaml import write_h2_pipeline_yaml
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
