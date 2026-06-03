"""Wave D: ``methods_resource_unified_v1`` / preview in parity export."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tests.helpers.paths import configs_path, fixtures_path, repo_root, scripts_path

_ROOT = repo_root()


def _export_with_results(cfg_rel: str, results_path: Path) -> dict:
    env = {
        **os.environ,
        "PYTHONPATH": str(_ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""),
    }
    cmd = [
        sys.executable,
        str(scripts_path("export_parity_criteria_table.py")),
        str(_ROOT / cfg_rel),
        "--results",
        str(results_path),
    ]
    proc = subprocess.run(cmd, cwd=str(_ROOT), capture_output=True, text=True, env=env, check=False)
    assert proc.returncode == 0, proc.stderr or proc.stdout
    return json.loads(proc.stdout)


def test_methods_resource_preview_in_config_only_export() -> None:
    import importlib.util

    ep_path = scripts_path("export_parity_criteria_table.py")
    spec = importlib.util.spec_from_file_location("export_parity_criteria_table", ep_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    d = mod._table_from_config(configs_path("qpe_dual_track_demo.yaml"))
    prev = d.get("methods_resource_preview_v1")
    assert isinstance(prev, dict)
    assert prev.get("schema") == "methods_resource_preview_v1"
    assert prev.get("qpe_pipeline_integration") is True
    assert prev.get("qpe_demo_track_n_bits") == 4
    wq = d.get("workflow_preview_qpe_track_v1")
    assert isinstance(wq, dict) and wq.get("schema") == "workflow_preview_qpe_track_v1"
    assert wq.get("qpe_demo_track_n_bits") == 4


def test_methods_resource_preview_includes_vqs_flags() -> None:
    import importlib.util

    p_yaml = configs_path("example_h2_vqs_track.yaml")
    if not p_yaml.is_file():
        pytest.skip("example_h2_vqs_track.yaml missing")
    ep_path = scripts_path("export_parity_criteria_table.py")
    spec = importlib.util.spec_from_file_location("export_parity_criteria_table", ep_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    d = mod._table_from_config(p_yaml)
    prev = d.get("methods_resource_preview_v1")
    assert isinstance(prev, dict)
    assert prev.get("vqs_pipeline_integration") is True
    assert prev.get("vqs_track_after_variational") is False
    wvq = d.get("workflow_preview_vqs_track_v1")
    assert isinstance(wvq, dict) and wvq.get("schema") == "workflow_preview_vqs_track_v1"


@pytest.mark.skipif(
    not (configs_path("qpe_dual_track_demo.yaml")).is_file(),
    reason="config missing",
)
def test_methods_resource_unified_from_qpe_dual_track_pipeline() -> None:
    try:
        import pyscf  # noqa: F401
    except ImportError:
        pytest.skip("PySCF not installed")

    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    cfg_rel = "configs/qpe_dual_track_demo.yaml"
    cfg_path = _ROOT / cfg_rel
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    tmp = fixtures_path("_tmp_qpe_dual_methods_resource.json")
    try:
        tmp.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
        exp = _export_with_results(cfg_rel, tmp)
    finally:
        tmp.unlink(missing_ok=True)

    uni = exp.get("methods_resource_unified_v1")
    assert isinstance(uni, dict)
    assert uni.get("schema") == "methods_resource_unified_v1"
    assert uni.get("classical_backend_id") == "pyscf"
    assert isinstance(uni.get("resource_summary"), dict)
    assert uni.get("run_summary_qpe_demo_track_ran") is True
    qp_wf = exp.get("workflow_preview_qpe_track_v1")
    assert isinstance(qp_wf, dict) and qp_wf.get("schema") == "workflow_preview_qpe_track_v1"
    qcontr = uni.get("qpe_open_stack_contract_v1")
    assert isinstance(qcontr, dict) and qcontr.get("schema") == "qpe_open_stack_contract_v1"
    qpeb = uni.get("qpe_demo_track")
    assert isinstance(qpeb, dict)
    assert qpeb.get("schema")


@pytest.mark.skipif(
    not (configs_path("example_h2_qpe_track_parity_integrations.yaml")).is_file(),
    reason="config missing",
)
def test_methods_resource_unified_qpe_plus_tket_probe_schema() -> None:
    pytest.importorskip("pyscf")
    pytest.importorskip("pytket")

    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    cfg_rel = "configs/example_h2_qpe_track_parity_integrations.yaml"
    cfg_path = _ROOT / cfg_rel
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    tmp = fixtures_path("_tmp_methods_resource_qpe_tket.json")
    try:
        tmp.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
        exp = _export_with_results(cfg_rel, tmp)
    finally:
        tmp.unlink(missing_ok=True)

    uni = exp.get("methods_resource_unified_v1")
    assert isinstance(uni, dict)
    assert uni.get("schema") == "methods_resource_unified_v1"
    assert uni.get("classical_backend_id") == "pyscf"
    assert uni.get("run_summary_qpe_demo_track_ran") is True
    qcontr = uni.get("qpe_open_stack_contract_v1")
    assert isinstance(qcontr, dict) and qcontr.get("schema") == "qpe_open_stack_contract_v1"
    rs = uni.get("resource_summary")
    assert isinstance(rs, dict)
    assert rs.get("pauli_averaging_protocol_ran") is True
    qpeb = uni.get("qpe_demo_track")
    assert isinstance(qpeb, dict)
    assert qpeb.get("schema")
    assert uni.get("tket_first_compiled_circuit_probe_schema") == "tket_stats_attempt_v1"
    rev = exp.get("resource_estimation_preview_v1")
    assert isinstance(rev, dict)
    assert rev.get("schema") == "resource_estimation_preview_v1"
    assert rev.get("mode") == "pipeline"
    assert rev.get("qpe_demo_track_n_bits") == 4
    rs_run = out.get("resource_summary")
    assert isinstance(rs_run, dict)
    for k in (
        "n_circuits",
        "n_qubits",
        "sum_shots",
        "max_depth",
        "sum_twoq",
        "n_pauli_terms",
        "n_pauli_groups",
    ):
        if rs_run.get(k) is not None:
            assert rev.get(f"resource_summary_{k}") == rs_run.get(k)


def test_resource_estimation_preview_v1_config_only_export() -> None:
    env = {
        **os.environ,
        "PYTHONPATH": str(_ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""),
    }
    cfg = configs_path("example_h2_qpe_track_parity_integrations.yaml")
    proc = subprocess.run(
        [sys.executable, str(scripts_path("export_parity_criteria_table.py")), str(cfg)],
        cwd=str(_ROOT),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    exp = json.loads(proc.stdout)
    rev = exp.get("resource_estimation_preview_v1")
    assert isinstance(rev, dict)
    assert rev.get("schema") == "resource_estimation_preview_v1"
    assert rev.get("mode") == "config_only"
    assert rev.get("parity_integrations_tket_first_circuit_stats") is True
    assert rev.get("qpe_demo_track_n_bits") == 4
    assert rev.get("qpe_three_pack_time_yaml") == 1.0
    assert rev.get("vqs_rhs_mode_yaml") == "linear_damping"
    assert rev.get("classical_shadows_stub_enabled_yaml") is False
    assert rev.get("classical_benchmark_enabled_yaml") is False
    assert rev.get("mitigation_zne_mode_yaml") == "scalar_stub"
    assert rev.get("mitigation_zne_scales_yaml") == [1.0, 1.5, 2.0]
    assert rev.get("quantum_algorithm_yaml") == "vqe"
    assert rev.get("backend_provider_yaml") == "statevector"
    assert rev.get("fermion_qubit_mapping_yaml") == "jordan_wigner"
    assert rev.get("zne_enabled_yaml") is False
    assert rev.get("pmsv_enabled_yaml") is False
    assert rev.get("pauli_protocol_expectation_path_yaml") == "exact_executor"
    assert "compiler_pass_bundle_yaml" in rev
    assert rev.get("tket_probe_requested") is True


def test_resource_estimation_preview_depth_proxies_from_results() -> None:
    from qchem_stack.config import load_experiment_config
    from qchem_stack.integrations.resource_estimation_preview import (
        build_resource_estimation_preview_v1,
    )

    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    row = {
        "resource_summary": {
            "sum_shots": 4096,
            "n_pauli_groups": 4,
            "max_depth": 12,
            "n_qubits": 4,
            "sum_twoq": 8,
        },
        "repro": {"run_summary": {}},
    }
    prev = build_resource_estimation_preview_v1(cfg=cfg, pipeline_row=row)
    assert prev.get("ft_total_measurement_shots_proxy") == 4096
    assert prev.get("ft_shots_per_circuit_effective_proxy") == 1024
    assert prev.get("ft_t_gate_count_proxy") == 48


def test_registry_and_mdml_blocks_in_config_only_export() -> None:
    env = {
        **os.environ,
        "PYTHONPATH": str(_ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""),
    }
    cfg = configs_path("example_h2_qpe_track_parity_integrations.yaml")
    proc = subprocess.run(
        [sys.executable, str(scripts_path("export_parity_criteria_table.py")), str(cfg)],
        cwd=str(_ROOT),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    exp = json.loads(proc.stdout)
    reg = exp.get("algorithm_registry_alignment_v1")
    assert isinstance(reg, dict)
    assert reg.get("schema") == "algorithm_registry_alignment_v1"
    assert "vqe" in (reg.get("algorithm_registry_ids") or [])
    vre = reg.get("variational_registry_export_v1")
    assert isinstance(vre, dict) and "vqe" in vre
    assert isinstance(vre["vqe"], dict) and vre["vqe"].get("has_materialization") is True
    ere = reg.get("excited_registry_export_v1")
    assert isinstance(ere, dict) and set(ere.keys()) >= {"vqd", "qse", "sceom"}
    pre = reg.get("operator_pool_registry_export_v1")
    assert isinstance(pre, dict)
    assert pre.get("schema") == "operator_pool_registry_export_v1"
    assert "fermionic_uccsd" in (pre.get("registered_ids") or [])
    assert "fermionic_uccsd_doubles_only" in (pre.get("registered_ids") or [])
    assert "qubit_excitation" in (pre.get("registered_ids") or [])
    assert "uccsd_jw" in (pre.get("registered_ids") or [])
    assert "hea" in (reg.get("ansatz_registry_ids") or [])
    mdml = exp.get("md_ml_repro_freeze_fields_v1")
    assert isinstance(mdml, dict)
    assert mdml.get("schema") == "md_ml_repro_freeze_fields_v1"
    assert "protocol_hash" in (mdml.get("qmframe_fields") or [])


def test_methods_resource_unified_v1_includes_classical_benchmark_fields_when_enabled(
    tmp_path,
) -> None:
    pytest.importorskip("pyscf")

    from qchem_stack.config import load_experiment_config
    from qchem_stack.integrations.methods_resource_unified import build_methods_resource_unified_v1
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    cfg_path = tmp_path / "h2_methods_uni_bench.yaml"
    cfg_path.write_text(
        """
schema_version: "2"
experiment_id: methods_uni_bench
random_seed: 1
molecule:
  symbols: ["H", "H"]
  coordinates:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  coordinate_unit: bohr
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: pyscf
  method: RHF
active_space:
  strategy: cas
  cas:
    n_orbitals: 2
    n_electrons: 2
backend:
  provider: statevector
  shots_per_circuit: 256
quantum:
  algorithm: vqe
  vqe:
    depth: 1
    maxiter: 10
  pauli:
    use_protocol: false
chemistry_extended:
  benchmarks:
    enabled: true
""",
        encoding="utf-8",
    )
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    uni = build_methods_resource_unified_v1(out)
    assert uni.get("schema") == "methods_resource_unified_v1"
    assert uni.get("classical_benchmark_active") is True
    from qchem_stack.integrations.resource_estimation_preview import (
        build_resource_estimation_preview_v1,
    )

    prv = build_resource_estimation_preview_v1(cfg=cfg, pipeline_row=out)
    for ck in (
        "classical_benchmark_active",
        "classical_benchmark_summary_schema",
        "classical_benchmark_recommended_baseline_policy",
        "classical_benchmark_recommended_baseline_method",
        "classical_benchmark_recommended_baseline_energy_au",
        "classical_benchmark_best_method",
        "classical_benchmark_best_energy_au",
    ):
        assert prv.get(ck) == uni.get(ck), ck
    assert uni.get("classical_benchmark_summary_schema") == "classical_benchmark_summary_v1"
    assert (
        uni.get("classical_benchmark_recommended_baseline_policy") == "prefer_ccsd_else_mp2_else_hf"
    )
    assert uni.get("classical_benchmark_recommended_baseline_method") in ("ccsd", "mp2", "hf")
    assert uni.get("classical_benchmark_recommended_baseline_energy_au") is not None


def test_resource_estimation_preview_pipeline_merges_qpe_three_from_run_summary() -> None:
    from qchem_stack.config import load_experiment_config
    from qchem_stack.integrations.resource_estimation_preview import (
        build_resource_estimation_preview_v1,
    )

    cfg_path = configs_path("example_h2_qpe_track_parity_integrations.yaml")
    if not cfg_path.is_file():
        pytest.skip("configs/example_h2_qpe_track_parity_integrations.yaml missing")
    cfg = load_experiment_config(cfg_path)
    row = {
        "resource_summary": {"n_circuits": 42, "pauli_averaging_protocol_ran": True},
        "repro": {
            "run_summary": {
                "qpe_three_pack_ran": True,
                "qpe_three_pack_deterministic_energy_est": -1.23,
                "qpe_three_pack_kitaev_energy_est": -1.22,
                "qpe_three_pack_info_theory_energy_est": -1.21,
                "protocol_total_shots_budget": 999,
                "protocol_expectation_source": "executor_exact_or_device_mean",
            }
        },
    }
    p = build_resource_estimation_preview_v1(cfg=cfg, pipeline_row=row)
    assert p["mode"] == "pipeline"
    assert p["resource_summary_n_circuits"] == 42
    assert p["resource_summary_pauli_averaging_protocol_ran"] is True
    assert p["run_summary_protocol_total_shots_budget"] == 999
    assert p["run_summary_protocol_expectation_source"] == "executor_exact_or_device_mean"
    assert p["run_summary_qpe_three_pack_ran"] is True
    assert p["qpe_three_pack_deterministic_energy_est_from_run"] == -1.23
    assert p["qpe_three_pack_kitaev_energy_est_from_run"] == -1.22
    assert p["qpe_three_pack_info_theory_energy_est_from_run"] == -1.21


def test_methods_resource_unified_includes_qpe_three_pack_energy_fields() -> None:
    from qchem_stack.integrations.methods_resource_unified import build_methods_resource_unified_v1

    uni = build_methods_resource_unified_v1(
        {
            "resource_summary": {},
            "repro": {
                "run_summary": {
                    "classical_backend_id": "pyscf",
                    "qpe_three_pack_ran": True,
                    "qpe_three_pack_deterministic_energy_est": -2.5,
                    "qpe_three_pack_kitaev_energy_est": -2.4,
                    "qpe_three_pack_info_theory_energy_est": -2.3,
                }
            },
        }
    )
    assert uni["run_summary_qpe_three_pack_ran"] is True
    assert uni["qpe_three_pack_deterministic_energy_est"] == -2.5
    assert uni["qpe_three_pack_kitaev_energy_est"] == -2.4
    assert uni["qpe_three_pack_info_theory_energy_est"] == -2.3
