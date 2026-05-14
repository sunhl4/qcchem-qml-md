"""WorkflowCoordinator attaches methods_sidecar."""

from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.orchestration.workflow import WorkflowCoordinator

pytest.importorskip("pyscf")


def test_workflow_coordinator_runs_and_has_sidecar() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = root / "configs" / "example_h2.yaml"
    wf = WorkflowCoordinator(cfg, job_db=None)
    out = wf.run()
    assert "methods_sidecar" in out
    sc = out["methods_sidecar"]
    assert sc["computable_abstract"]["schema"] == "qchem_computable_abstract_v2"
    assert isinstance(out.get("hamiltonian_meta"), dict)
    assert out["hamiltonian_meta"].get("hamiltonian_fingerprint")
    assert sc.get("hamiltonian_fingerprint") == out["hamiltonian_meta"].get(
        "hamiltonian_fingerprint"
    )
    if out.get("protocol_counts"):
        assert sc["computable_abstract"].get("support_set_exported_from_protocol") is True
