"""Computable-style abstract list (InQuanto-analog)."""

from __future__ import annotations

from qchem_stack.config import MoleculeSpec, ActiveSpaceSpec, ExperimentConfig, QuantumSpec
from qchem_stack.protocols.computable import list_computables_for_config


def test_list_computables_names() -> None:
    cfg = ExperimentConfig(
        experiment_id="c",
        random_seed=0,
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates_bohr=[[0, 0, 0], [0, 0, 1.4]]),
        active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
        quantum=QuantumSpec(use_pauli_protocol=True, qpe_demo_track_after_variational=True),
    )
    names = {c.name for c in list_computables_for_config(cfg)}
    assert "hamiltonian_expectation_pauli_protocol" in names
    assert "qpe_demo_track" in names
