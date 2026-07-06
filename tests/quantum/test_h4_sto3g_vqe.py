"""H4 linear chain VQE test with PySCF and STO-3G basis.

This test validates the VQE pipeline on a larger molecule (H4) compared to
the typical H2 tests, ensuring the stack can handle 4-qubit active spaces.
"""

from __future__ import annotations

import pytest

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync
from tests.helpers.paths import configs_path

pyscf = pytest.importorskip("pyscf")


@pytest.mark.slow
@pytest.mark.pyscf
def test_h4_linear_chain_vqe_pipeline() -> None:
    """Run VQE on H4 linear chain with 4-qubit active space."""
    cfg_path = configs_path("example_h4_dmet_fragment_exact_small.yaml")
    cfg = load_experiment_config(cfg_path)

    out = run_pipeline_sync(cfg, cfg_path=cfg_path)

    # Validate pipeline completed successfully
    assert "schema" in out
    assert out["schema"] == "pipeline_result_v1"

    # Check that we have a variational energy
    assert "energy_after_variational" in out
    e_var = out["energy_after_variational"]
    assert e_var is not None
    assert e_var < 0.0  # Should be negative (bound state)

    # Validate active space configuration (n_qubits lives under pre_quantum_input)
    assert out["pre_quantum_input"]["n_qubits"] >= 4

    # Check reproducibility snapshot
    assert "repro" in out
    repro = out["repro"]
    assert "parity_snapshot" in repro

    # Hamiltonian handoff fingerprint (stable parity field)
    assert out["pre_quantum_input"]["hamiltonian_fingerprint"]


@pytest.mark.slow
@pytest.mark.pyscf
def test_h4_schmidt_multifragment_smoke() -> None:
    """Smoke test for H4 Schmidt multifragment pipeline."""
    cfg_path = configs_path("example_h4_schmidt_multifragment.yaml")
    cfg = load_experiment_config(cfg_path)

    out = run_pipeline_sync(cfg, cfg_path=cfg_path)

    # Basic validation
    assert out["schema"] == "pipeline_result_v1"
    assert out["pre_quantum_input"]["source"] == "schmidt_atomic_production"
    assert out["pre_quantum_input"]["hamiltonian_branch"] == "schmidt_atomic_production"

    # Check that DMET was applied
    assert "schmidt_per_fragment_vqe" in out or "dmet_summary" in out
