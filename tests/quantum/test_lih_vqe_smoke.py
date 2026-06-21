"""LiH VQE smoke test with PySCF and STO-3G basis.

This test validates the VQE pipeline on lithium hydride (LiH), a heteronuclear
diatomic molecule, ensuring the stack can handle molecules beyond simple H2/H4.
"""

from __future__ import annotations

import pytest

from qchem_stack.backends.spec import BackendSpec
from qchem_stack.config import ExperimentConfig
from qchem_stack.config.active_space import ActiveSpaceSpec
from qchem_stack.config.molecule import MoleculeSpec
from qchem_stack.config.quantum import QuantumSpec
from qchem_stack.config.scf import SCFSpec
from qchem_stack.orchestration.pipeline import run_pipeline_sync

pyscf = pytest.importorskip("pyscf")


@pytest.mark.slow
@pytest.mark.pyscf
def test_lih_sto3g_vqe_smoke() -> None:
    """Smoke test for LiH VQE with minimal basis set."""
    # Create LiH configuration programmatically
    cfg = ExperimentConfig(
        schema_version="2",
        experiment_id="lih_sto3g_vqe_smoke",
        molecule=MoleculeSpec(
            symbols=["Li", "H"],
            coordinates=[[0.0, 0.0, 0.0], [0.0, 0.0, 1.595]],  # Li-H bond length in Angstrom
            basis="sto-3g",
            charge=0,
            spin=0,
        ),
        scf=SCFSpec(
            driver="pyscf",
            method="rhf",
        ),
        active_space=ActiveSpaceSpec(
            n_electrons=2,
            n_orbitals=2,
            freeze_core=True,
        ),
        backend=BackendSpec(
            name="statevector",
            provider="qiskit",
        ),
        quantum=QuantumSpec(
            algorithm="vqe",
            ansatz="uccsd",
            optimizer="cobyla",
            max_iterations=100,
        ),
    )

    out = run_pipeline_sync(cfg)

    # Validate pipeline completed successfully
    assert "schema" in out
    assert out["schema"] == "pipeline_result_v1"

    # Check that we have a variational energy
    assert "energy_after_variational" in out
    e_var = out["energy_after_variational"]
    assert e_var is not None
    assert e_var < 0.0  # Should be negative (bound state)

    # Validate that SCF converged
    assert "scf_energy" in out
    e_scf = out["scf_energy"]
    assert e_scf is not None
    assert e_scf < 0.0

    # VQE energy should be lower than or close to SCF energy
    # (within 0.1 Ha tolerance for this smoke test)
    assert e_var <= e_scf + 0.1

    # Check reproducibility snapshot
    assert "repro" in out
    repro = out["repro"]
    assert "parity_snapshot" in repro


@pytest.mark.slow
@pytest.mark.pyscf
def test_lih_active_space_2e_2o() -> None:
    """Test LiH with 2-electron, 2-orbital active space."""
    cfg = ExperimentConfig(
        schema_version="2",
        experiment_id="lih_cas_2e_2o",
        molecule=MoleculeSpec(
            symbols=["Li", "H"],
            coordinates=[[0.0, 0.0, 0.0], [0.0, 0.0, 1.595]],
            basis="sto-3g",
            charge=0,
            spin=0,
        ),
        scf=SCFSpec(
            driver="pyscf",
            method="rhf",
        ),
        active_space=ActiveSpaceSpec(
            n_electrons=2,
            n_orbitals=2,
            freeze_core=True,
        ),
        backend=BackendSpec(
            name="statevector",
            provider="qiskit",
        ),
        quantum=QuantumSpec(
            algorithm="vqe",
            ansatz="hea",
            depth=2,
            optimizer="cobyla",
            max_iterations=50,
        ),
    )

    out = run_pipeline_sync(cfg)

    # Validate basic structure
    assert out["schema"] == "pipeline_result_v1"
    assert "energy_after_variational" in out

    # Check that we have the expected number of qubits for 2e/2o
    # With Jordan-Wigner: 2 orbitals = 4 qubits
    n_qubits = out.get("n_qubits", 0)
    assert n_qubits == 4, f"Expected 4 qubits for 2e/2o, got {n_qubits}"
