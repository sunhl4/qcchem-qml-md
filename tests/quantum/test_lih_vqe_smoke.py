"""LiH VQE smoke test with PySCF and STO-3G basis.

This test validates the VQE pipeline on lithium hydride (LiH), a heteronuclear
diatomic molecule, ensuring the stack can handle molecules beyond simple H2/H4.
"""

from __future__ import annotations

import pytest

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync
from tests.helpers.h2_yaml import write_experiment_yaml

pyscf = pytest.importorskip("pyscf")


def _lih_vqe_dict(*, experiment_id: str, maxiter: int, depth: int) -> dict:
    return {
        "schema_version": "2",
        "experiment_id": experiment_id,
        "molecule": {
            "symbols": ["Li", "H"],
            "coordinates": [[0.0, 0.0, 0.0], [0.0, 0.0, 1.595]],
            "coordinate_unit": "angstrom",
            "charge": 0,
            "multiplicity": 1,
            "basis": "sto-3g",
        },
        "active_space": {
            "strategy": "cas",
            "cas": {"n_orbitals": 2, "n_electrons": 2},
        },
        "scf": {"driver": "pyscf", "method": "RHF"},
        "embedding": {"mode": "none"},
        "backend": {"provider": "statevector", "shots_per_circuit": 512},
        "quantum": {
            "algorithm": "vqe",
            "vqe": {"depth": depth, "maxiter": maxiter},
            "pauli": {"use_protocol": False},
        },
    }


@pytest.mark.slow
@pytest.mark.pyscf
def test_lih_sto3g_vqe_smoke(tmp_path) -> None:
    """Smoke test for LiH VQE with minimal basis set."""
    cfg_path = write_experiment_yaml(
        tmp_path / "lih_sto3g_vqe_smoke.yaml",
        _lih_vqe_dict(
            experiment_id="lih_sto3g_vqe_smoke",
            maxiter=100,
            depth=2,
        ),
    )
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)

    assert out["schema"] == "pipeline_result_v1"
    e_var = out["energy_after_variational"]
    assert e_var is not None and e_var < 0.0
    e_scf = out["scf_energy"]
    assert e_scf is not None and e_scf < 0.0
    assert e_var <= e_scf + 0.1
    assert "parity_snapshot" in out["repro"]


@pytest.mark.slow
@pytest.mark.pyscf
def test_lih_active_space_2e_2o(tmp_path) -> None:
    """Test LiH with 2-electron, 2-orbital active space."""
    cfg_path = write_experiment_yaml(
        tmp_path / "lih_cas_2e_2o.yaml",
        _lih_vqe_dict(
            experiment_id="lih_cas_2e_2o",
            maxiter=50,
            depth=2,
        ),
    )
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)

    assert out["schema"] == "pipeline_result_v1"
    assert "energy_after_variational" in out
    n_qubits = out["pre_quantum_input"]["n_qubits"]
    assert n_qubits == 4, f"Expected 4 qubits for 2e/2o, got {n_qubits}"
