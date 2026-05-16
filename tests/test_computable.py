"""Computable-style abstract list (workflow-parity analog)."""

from __future__ import annotations

from pathlib import Path

from qchem_stack.config import (
    ActiveSpaceSpec,
    ExperimentConfig,
    MoleculeSpec,
    QuantumSpec,
    load_experiment_config,
)
from qchem_stack.protocols.computable import (
    assert_computable_workflow_graph_roundtrip,
    list_computables_for_config,
)


def test_qpe_pipeline_integration_adds_qpe_computable() -> None:
    cfg = ExperimentConfig(
        experiment_id="c2",
        random_seed=0,
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates_bohr=[[0, 0, 0], [0, 0, 1.4]]),
        active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
        quantum=QuantumSpec(use_pauli_protocol=False, qpe_pipeline_integration=True),
    )
    names = {c.name for c in list_computables_for_config(cfg)}
    assert "qpe_demo_track" in names


def test_vqs_pipeline_integration_adds_vqs_computable() -> None:
    cfg = ExperimentConfig(
        experiment_id="c_vqs",
        random_seed=0,
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates_bohr=[[0, 0, 0], [0, 0, 1.4]]),
        active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
        quantum=QuantumSpec(use_pauli_protocol=False, vqs_pipeline_integration=True),
    )
    names = {c.name for c in list_computables_for_config(cfg)}
    assert "vqs_track" in names


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


def test_computable_workflow_graph_roundtrip_example_configs() -> None:
    root = Path(__file__).resolve().parents[1]
    for rel in (
        "configs/example_h2.yaml",
        "configs/qpe_dual_track_demo.yaml",
        "configs/example_h2_vqs_track.yaml",
        "configs/example_h2_echo_variational_plugin.yaml",
    ):
        cfg = load_experiment_config(root / rel)
        assert_computable_workflow_graph_roundtrip(cfg)
