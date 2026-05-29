"""Minimal tests for open-stack CuTensorNet protocol stub and engine resolution."""

from __future__ import annotations

from qchem_stack.config import load_experiment_config
from qchem_stack.config.quantum_helpers import resolve_tensornet_contraction_engine
from qchem_stack.tensornet.cutensornet_protocol_stub import run_cutensornet_expectation_stub
from tests.helpers.paths import configs_path


def test_cutensornet_stub_default_status() -> None:
    row = run_cutensornet_expectation_stub(2, requested_backend="stub")
    assert row["schema"] == "cutensornet_protocol_stub_v1"
    assert row["status"] == "stub_no_contraction"
    assert row["n_qubits"] == 2


def test_cutensornet_opt_einsum_demo_resolves_engine() -> None:
    row = run_cutensornet_expectation_stub(4, requested_backend="opt_einsum")
    assert row["status"] == "opt_einsum_demo_ok"
    assert row["engine_resolved"] == "opt_einsum"
    assert "contraction_value" in row


def test_resolve_tensornet_engine_from_example_h2() -> None:
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    resolved = resolve_tensornet_contraction_engine(cfg)
    assert resolved in ("stub", "opt_einsum", "cupy_if_available", "cuquantum_if_available")
