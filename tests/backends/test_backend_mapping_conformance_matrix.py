"""Parametrized backend × fermion mapping conformance (P1-R04 / N-03)."""

from __future__ import annotations

import pytest

from qchem_stack.config import load_experiment_config
from tests.helpers.paths import configs_path


@pytest.mark.parametrize(
    ("mapping", "provider"),
    [
        ("jordan_wigner", "statevector"),
        ("bravyi_kitaev", "statevector"),
        ("symmetry_conserving_bravyi_kitaev", "statevector"),
        ("jordan_wigner", "qiskit"),
        ("bravyi_kitaev", "qiskit"),
        ("symmetry_conserving_bravyi_kitaev", "qiskit"),
        ("jordan_wigner", "qulacs"),
        ("bravyi_kitaev", "qulacs"),
        ("jordan_wigner", "cirq"),
        ("bravyi_kitaev", "cirq"),
        ("jordan_wigner", "braket"),
        ("bravyi_kitaev", "braket"),
    ],
)
def test_backend_mapping_hea_conformance_matrix(mapping: str, provider: str) -> None:
    """Same H2 HEA YAML: schema-stable pipeline keys across backend × mapping grid."""
    if provider == "qiskit":
        pytest.importorskip("qiskit")
    if provider == "qulacs":
        pytest.importorskip("qulacs")
    if provider == "cirq":
        pytest.importorskip("cirq")
    if provider == "braket":
        pytest.importorskip("braket")

    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    object.__setattr__(cfg.active_space.mapping, "fermion_qubit", mapping)
    object.__setattr__(cfg.backend, "provider", provider)
    object.__setattr__(cfg.quantum.variational, "ansatz", "hea")

    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    pytest.importorskip("pyscf")
    cfg_path = configs_path("example_h2.yaml")
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    assert out.get("scf_energy") is not None
    repro = out.get("repro")
    assert isinstance(repro, dict)
    snap = repro.get("parity_snapshot")
    assert isinstance(snap, dict)
    assert snap.get("fermion_qubit_mapping") == mapping
    assert snap.get("backend_provider") == provider
