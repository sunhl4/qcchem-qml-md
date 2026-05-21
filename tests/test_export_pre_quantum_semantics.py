"""Config-only parity export includes pre-quantum semantics slice."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def _export(cfg_rel: str) -> dict:
    root = Path(__file__).resolve().parents[1]
    env = {
        **os.environ,
        "PYTHONPATH": str(root / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""),
    }
    proc = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "export_parity_criteria_table.py"),
            str(root / cfg_rel),
        ],
        cwd=str(root),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    return json.loads(proc.stdout)


def test_export_h2_pre_quantum_semantics_canonical() -> None:
    data = _export("configs/example_h2.yaml")
    sem = data.get("pre_quantum_semantics_from_config") or {}
    assert sem.get("hamiltonian_branch") == "canonical_active_space_integral_pack"
    assert sem.get("post_variational_embedding_audit_only") is True


def test_export_h4_schmidt_semantics() -> None:
    data = _export("configs/example_h4_schmidt_multifragment.yaml")
    sem = data.get("pre_quantum_semantics_from_config") or {}
    assert sem.get("hamiltonian_branch") == "schmidt_atomic_production"
    assert sem.get("post_variational_embedding_audit_only") is True


def test_export_precomputed_bundle_semantics() -> None:
    data = _export("configs/example_h2_precomputed_bundle.yaml")
    sem = data.get("pre_quantum_semantics_from_config") or {}
    assert sem.get("hamiltonian_branch") == "precomputed_bundle"
    assert data.get("scf_driver") == "precomputed"
    assert sem.get("post_variational_embedding_audit_only") is True
