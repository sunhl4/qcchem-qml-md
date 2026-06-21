"""ZNE circuit_scale_fold: per-scale energies, expanded shot rows, mitigation trace alignment."""

from __future__ import annotations

import pytest

from tests.helpers.paths import configs_path

pyscf = pytest.importorskip("pyscf")

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync


def test_zne_circuit_fold_protocol_counts_and_shots() -> None:
    p = configs_path("example_h2_zne_circuit_fold.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    pc = out["protocol_counts"]
    scales = [float(x) for x in cfg.mitigation.zne.scales]
    assert pc.get("zne_mode") == "circuit_scale_fold"
    assert isinstance(pc.get("zne_curve"), list)
    assert len(pc["zne_curve"]) == len(scales)
    assert pc.get("zne_extrapolated_energy") is not None
    rs = out["resource_summary"]
    base_rows = len(out["resource_rows"]) // len(scales)
    assert base_rows * len(scales) == len(out["resource_rows"])
    assert int(rs["sum_shots"]) > 0
    snap = out["repro"]["parity_snapshot"]
    assert snap.get("mitigation_zne_mode") == "circuit_scale_fold"


def test_zne_circuit_fold_mitigation_dag_uses_protocol_curve() -> None:
    p = configs_path("example_h2_zne_circuit_fold.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    dex = out.get("mitigation_dag_execution")
    assert isinstance(dex, dict)
    znodes = [
        t
        for t in dex.get("trace", [])
        if isinstance(t, dict) and t.get("node") == "ZNE_extrapolation_stub"
    ]
    assert len(znodes) == 1
    zn = znodes[0]
    pc = out["protocol_counts"]
    assert zn["zne_energies"] == pc["zne_curve"]
    assert zn["zne_extrapolated_energy"] == pytest.approx(float(pc["zne_extrapolated_energy"]))


def test_zne_circuit_fold_qiskit_shots_path() -> None:
    pytest.importorskip("qiskit")
    pytest.importorskip("qiskit_aer")
    p = configs_path("example_h2_zne_qiskit_fold.yaml")
    if not p.is_file():
        pytest.skip("example_h2_zne_qiskit_fold.yaml missing")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    pc = out["protocol_counts"]
    scales = [float(x) for x in cfg.mitigation.zne.scales]
    assert pc.get("zne_mode") == "circuit_scale_fold"
    assert len(pc.get("zne_curve") or []) == len(scales)
    dex = out.get("mitigation_dag_execution")
    assert isinstance(dex, dict)
    znodes = [
        t
        for t in dex.get("trace", [])
        if isinstance(t, dict) and t.get("node") == "ZNE_extrapolation_stub"
    ]
    assert len(znodes) == 1
    assert znodes[0]["zne_energies"] == pc["zne_curve"]
    snap = out["repro"]["parity_snapshot"]
    assert snap.get("mitigation_zne_mode") == "circuit_scale_fold"
    uni = snap.get("zne_qiskit_unification_v1")
    assert isinstance(uni, dict)
    assert uni.get("protocol_counts_zne_mode") == "circuit_scale_fold"
