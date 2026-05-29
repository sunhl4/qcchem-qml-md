"""Behavior tests for ``qchem_stack.quantum.runtime`` helpers."""

from __future__ import annotations

from openfermion.ops import QubitOperator

from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.config import (
    ActiveSpaceSpec,
    BackendSpecConfig,
    ExperimentConfig,
    MoleculeSpec,
    QuantumSpec,
    SCFSpec,
)
from qchem_stack.quantum.runtime import vqe_from_experiment_config


def _minimal_cfg() -> ExperimentConfig:
    return ExperimentConfig(
        schema_version="2",
        experiment_id="runtime_toy",
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.74]]),
        scf=SCFSpec(),
        active_space=ActiveSpaceSpec.model_validate(
            {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
        ),
        backend=BackendSpecConfig(provider="statevector", shots_per_circuit=512),
        quantum=QuantumSpec(algorithm="vqe", vqe={"depth": 1, "maxiter": 2}),
    )


def _tiny_qh() -> QubitHamiltonian:
    op = QubitOperator(((0, "Z"), (1, "Z")), 1.0)
    return QubitHamiltonian(operator=op, n_qubits=2)


def test_vqe_from_experiment_config_toy() -> None:
    result = vqe_from_experiment_config(
        _minimal_cfg(),
        _tiny_qh(),
        depth=1,
        maxiter=2,
        seed=0,
    )
    assert isinstance(result.energy, float)
    assert result.nfev >= 1
