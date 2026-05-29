"""Golden parity export (config-only) + optional --results merge keys."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tests.helpers.paths import configs_path, fixtures_path, repo_root, scripts_path

_ROOT = repo_root()
_FIXTURE = fixtures_path("parity_export_example_h2_config_only.json")
_RESULTS_FIXTURE = fixtures_path("pipeline_results_minimal_export_merge.json")


def _export_json(cfg_rel: str, *, results: Path | None = None) -> dict:
    env = {
        **os.environ,
        "PYTHONPATH": str(_ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""),
    }
    cmd = [
        sys.executable,
        str(scripts_path("export_parity_criteria_table.py")),
        str(_ROOT / cfg_rel),
    ]
    if results is not None:
        cmd.extend(["--results", str(results)])
    proc = subprocess.run(cmd, cwd=str(_ROOT), capture_output=True, text=True, env=env, check=False)
    assert proc.returncode == 0, proc.stderr or proc.stdout
    return json.loads(proc.stdout)


def _normalize_export(d: dict) -> dict:
    """Normalize path separators for cross-platform comparison."""
    out = json.loads(json.dumps(d))
    sc = out.get("source_config")
    if isinstance(sc, str):
        p = Path(sc)
        if len(p.parts) >= 2 and p.parts[-2:] == ("configs", "example_h2.yaml"):
            out["source_config"] = "configs/example_h2.yaml"
        else:
            out["source_config"] = str(p).replace("\\", "/")
    return out


def test_export_example_h2_matches_golden_fixture() -> None:
    assert _FIXTURE.is_file()
    golden = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    fresh = _normalize_export(_export_json("configs/example_h2.yaml"))
    # Keep the historical fixture as a backwards-compatible baseline while allowing additive export keys.
    for key, value in golden.items():
        if key == "parity_export_schema_version":
            assert int(str(fresh.get(key))) >= int(str(value))
            continue
        if key == "registered_solvers":
            assert isinstance(fresh.get(key), list)
            assert set(value).issubset(set(fresh[key]))
            continue
        if key == "computable_abstract":
            assert isinstance(fresh.get(key), dict)
            for sub_k, sub_v in value.items():
                if sub_k == "evaluate_note":
                    assert "evaluate" in str(fresh[key].get(sub_k, "")).lower()
                    continue
                assert fresh[key].get(sub_k) == sub_v
            continue
        if key in ("capability_gap_categories",):
            assert isinstance(fresh.get("capability_gap_categories"), list)
            continue
        assert fresh.get(key) == value
    assert isinstance(fresh.get("capability_gap_categories"), list)
    assert fresh.get("scf_driver") == "pyscf"
    assert isinstance(fresh.get("registered_solvers"), list)
    assert "pyscf" in fresh["registered_solvers"]
    assert isinstance(fresh.get("solver_capabilities_snapshot"), dict)
    assert fresh["solver_capabilities_snapshot"].get("backend_id") == "pyscf"
    assert fresh.get("geometry_source") == "cartesian"


def test_export_zmatrix_yaml_geometry_source_parity() -> None:
    zm = configs_path("example_h2_zmatrix_sto3g.yaml")
    if not zm.is_file():
        pytest.skip("example_h2_zmatrix_sto3g.yaml missing")
    fresh = _normalize_export(_export_json("configs/example_h2_zmatrix_sto3g.yaml"))
    assert fresh.get("geometry_source") == "zmatrix"


@pytest.mark.skipif(
    not (configs_path("example_h2_echo_variational_plugin.yaml")).is_file(),
    reason="echo plugin example config missing",
)
def test_export_echo_variational_plugin_config_only_yaml_factory_dispatch() -> None:
    fresh = _normalize_export(_export_json("configs/example_h2_echo_variational_plugin.yaml"))
    fac = "qchem_stack.quantum.variational_plugins.examples.echo_runner:echo_runner_factory"
    assert fresh.get("quantum_algorithm") == "echo_reference_plugin"
    assert fresh.get("quantum_algorithm_factory") == fac
    abstract = fresh.get("computable_abstract")
    assert isinstance(abstract, dict)
    items = abstract.get("items") or []
    assert (
        items
        and items[0].get("details", {}).get("variational_dispatch") == "yaml_algorithm_factory_v1"
    )
    wpex = fresh.get("workflow_preview_variational_execution_v1")
    assert isinstance(wpex, dict) and wpex.get("algorithm_factory") == fac


@pytest.mark.skipif(
    not (configs_path("example_h2_micro_vqe_plugin.yaml")).is_file(),
    reason="micro vqe plugin example config missing",
)
def test_export_micro_vqe_variational_plugin_config_only() -> None:
    fresh = _normalize_export(_export_json("configs/example_h2_micro_vqe_plugin.yaml"))
    fac = (
        "qchem_stack.quantum.variational_plugins.examples.vqe_micro_plugin:micro_vqe_runner_factory"
    )
    assert fresh.get("quantum_algorithm_factory") == fac
    assert fresh.get("quantum_algorithm") == "micro_vqe_yaml_plugin_demo"


@pytest.mark.skipif(
    not (configs_path("example_h2_psi4_rhf_sto3g.yaml")).is_file(),
    reason="repo psi4 sample yaml missing",
)
def test_export_repo_psi4_example_yaml_capabilities_snapshot() -> None:
    data = _normalize_export(_export_json("configs/example_h2_psi4_rhf_sto3g.yaml"))
    assert data.get("scf_driver") == "psi4"
    rs = data.get("registered_solvers")
    assert isinstance(rs, list) and "psi4" in rs and "pyscf" in rs
    caps = data.get("solver_capabilities_snapshot")
    assert isinstance(caps, dict) and caps.get("backend_id") == "psi4"


def test_export_parity_psi4_config_only_row_present() -> None:
    cfg = fixtures_path("_tmp_psi4_export.yaml")
    cfg.write_text(
        """
schema_version: "2"
experiment_id: psi4_export
random_seed: 0
molecule:
  symbols: ["H", "H"]
  coordinates:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  coordinate_unit: bohr
  basis: sto-3g
scf:
  driver: psi4
  method: RHF
active_space:
  strategy: cas
  cas:
    n_orbitals: 2
    n_electrons: 2
""",
        encoding="utf-8",
    )
    try:
        data = _export_json("tests/fixtures/_tmp_psi4_export.yaml")
        assert data.get("scf_driver") == "psi4"
        caps = data.get("solver_capabilities_snapshot")
        assert isinstance(caps, dict)
        assert caps.get("backend_id") == "psi4"
        assert caps.get("supports_restricted_active_space_qubit_hamiltonian") is True
    finally:
        cfg.unlink(missing_ok=True)


def test_export_results_merge_includes_algorithm_sidecars() -> None:
    out = _export_json("configs/example_h2.yaml", results=_RESULTS_FIXTURE)
    assert out.get("qpe_demo_track_ran_from_run_summary") is True
    assert out.get("embedding_workflow_from_run", {}).get("mode") == "none"
    assert out.get("adapt_meta_from_run", {}).get("total_gradient_evals") == 3
    assert out.get("tensornet_engine_resolved_from_parity_snapshot") == "stub"
    assert out.get("vqd_three_protocol_present_from_run") is True
    assert out.get("qse_shot_mode_from_run_meta") == "dense_reference_only"
    assert out.get("sceom_shot_noise_model_from_run") == "none"
    assert out.get("sceom_shots_per_matrix_element_from_run") == 0
    pqi = out.get("pre_quantum_input_from_run") or {}
    assert pqi.get("source") == "canonical_active_space_integral_pack"
    assert pqi.get("backend_tag") == "pyscf"
    assert out.get("pre_quantum_build_cache_from_run", {}).get("pack_builds") == 1
    assert (
        out.get("pre_quantum_source_mirror_run_summary") == "canonical_active_space_integral_pack"
    )
    ph = out.get("pre_quantum_handoff_v1_from_parity_snapshot") or {}
    assert ph.get("hamiltonian_branch") == "canonical_active_space_integral_pack"
    assert out.get("pre_quantum_build_cache_v1_from_parity_snapshot", {}).get("pack_builds") == 1


@pytest.mark.parametrize(
    "cfg_rel",
    (
        "configs/example_h2.yaml",
        "configs/tutorial_chain_h2.yaml",
        "configs/example_h2_excited_smoke.yaml",
        "configs/example_h2_iqeb.yaml",
        "configs/example_h2_adapt_singles_pool.yaml",
        "configs/example_h2_adapt_doubles_pool.yaml",
        "configs/example_h2_iqeb_fermionic_doubles_pool.yaml",
        "configs/example_h2_iqeb_qubit_excitation_alias.yaml",
        "configs/example_h2_adapt_uccsd_jw_alias.yaml",
        "configs/example_h2_uccsd.yaml",
        "configs/example_h2_uccsd_trotter.yaml",
        "configs/example_h2_vqd_uccsd.yaml",
        "configs/example_h2_uccsd_bk.yaml",
        "configs/example_h2_uccsd_pauli_protocol.yaml",
        "configs/example_h2_uccsd_qse_pauli_qiskit.yaml",
        "configs/example_h2_vqd_uccsd_three_computable.yaml",
        "configs/example_h2_sa_vqe.yaml",
        "configs/example_h2_vqd_deflation_circuit.yaml",
        "configs/example_h2_zne_circuit_fold.yaml",
        "configs/example_decomposition_plugin_toy.yaml",
        "configs/example_decomposition_plugin_two_fragment.yaml",
        "configs/example_h2_projection_trace.yaml",
        "configs/example_h4_projection_mulliken.yaml",
        "configs/example_oniom_toy.yaml",
        "configs/example_h2_avas_stub.yaml",
        "configs/example_h2_avas.yaml",
        "configs/example_h2_classical_shadows_stub.yaml",
        "configs/example_decomposition_plugin_contract.yaml",
        "configs/example_h2_precomputed_bundle.yaml",
        "configs/example_h4_schmidt_multifragment.yaml",
    ),
)
def test_m2_config_only_export_stable_keys(cfg_rel: str) -> None:
    from qchem_stack.protocols.product_contract import PARITY_EXPORT_V3_STABLE_KEYS

    cfg_path = _ROOT / cfg_rel
    if not cfg_path.is_file():
        pytest.skip(f"missing {cfg_rel}")
    data = _normalize_export(_export_json(cfg_rel))
    assert not (PARITY_EXPORT_V3_STABLE_KEYS - set(data.keys()))
    assert data.get("parity_export_schema_version") == "3"


@pytest.mark.skipif(
    not configs_path("example_h2.yaml").is_file(),
    reason="configs",
)
def test_m2_pipeline_then_export_documented_keys() -> None:
    try:
        import pyscf  # noqa: F401
    except ImportError:
        pytest.skip("PySCF not installed")
    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    cfg_path = configs_path("example_h2.yaml")
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    ec = out.get("energy_components")
    assert isinstance(ec, dict) and ec.get("schema") == "energy_components_v1"
    tmp = fixtures_path("_m2_tmp_pipeline_out.json")
    try:
        tmp.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
        exp = _export_json("configs/example_h2.yaml", results=tmp)
        assert "parity_snapshot_from_run" in exp
        assert isinstance(exp.get("run_summary_from_repro"), dict)
    finally:
        tmp.unlink(missing_ok=True)


def test_export_results_merge_includes_plugin_and_zne_run_summary_mirrors() -> None:
    try:
        import pyscf  # noqa: F401
    except ImportError:
        pytest.skip("PySCF not installed")
    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    # Plugin path: decomposition summary mirrors.
    cfg_plugin_rel = "configs/example_decomposition_plugin_two_fragment.yaml"
    cfg_plugin_path = _ROOT / cfg_plugin_rel
    out_plugin = run_pipeline_sync(
        load_experiment_config(cfg_plugin_path), cfg_path=cfg_plugin_path
    )
    tmp_plugin = fixtures_path("_tmp_plugin_export_merge.json")
    try:
        tmp_plugin.write_text(json.dumps(out_plugin, indent=2) + "\n", encoding="utf-8")
        exp_plugin = _export_json(cfg_plugin_rel, results=tmp_plugin)
    finally:
        tmp_plugin.unlink(missing_ok=True)
    assert exp_plugin.get("decomposition_fragment_count_mirror_run_summary") == 2
    assert exp_plugin.get("decomposition_total_pauli_terms_mirror_run_summary") == 9

    # ZNE path: mitigation mirrors include yaml and protocol zne_mode.
    cfg_zne_rel = "configs/example_h2_zne_circuit_fold.yaml"
    cfg_zne_path = _ROOT / cfg_zne_rel
    out_zne = run_pipeline_sync(load_experiment_config(cfg_zne_path), cfg_path=cfg_zne_path)
    tmp_zne = fixtures_path("_tmp_zne_export_merge.json")
    try:
        tmp_zne.write_text(json.dumps(out_zne, indent=2) + "\n", encoding="utf-8")
        exp_zne = _export_json(cfg_zne_rel, results=tmp_zne)
    finally:
        tmp_zne.unlink(missing_ok=True)
    assert exp_zne.get("mitigation_zne_mode_yaml_mirror_run_summary") == "circuit_scale_fold"
    assert isinstance(exp_zne.get("mitigation_zne_scales_yaml_mirror_run_summary"), list)
    assert exp_zne.get("protocol_zne_mode_mirror_run_summary") in (
        "circuit_scale_fold",
        "scalar_stub",
    )
