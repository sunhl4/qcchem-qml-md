"""Open gap-closure bundle, UCC commuting layers, dense expectation reference."""

from __future__ import annotations

import numpy as np
import pytest
from openfermion.ops import QubitOperator

from qchem_stack.config import (
    ActiveSpaceSpec,
    BackendSpecConfig,
    EmbeddingSpec,
    ExperimentConfig,
    MoleculeSpec,
    QuantumSpec,
    SCFSpec,
)
from qchem_stack.integrations.gap_closure_bundle import build_open_gap_closure_reference
from qchem_stack.integrations.ucc_reference import (
    GreedyCommutingFermionicLayers,
    build_spin_uccsd_fermion_generators,
)
from qchem_stack.orchestration.pipeline import collect_repro_metadata
from qchem_stack.tensornet.dense_expectation_reference import expectation_qubit_operator_dense


def test_open_gap_closure_reference_has_schemas() -> None:
    cfg = ExperimentConfig(
        experiment_id="gap",
        random_seed=0,
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates_bohr=[[0, 0, 0], [0, 0, 1.4]]),
        active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
    )
    g = build_open_gap_closure_reference(cfg)
    assert g["schema"] == "open_gap_closure_reference_v1"
    assert g["ucc"]["n_greedy_commuting_trotter_layers"] >= 1
    assert g["nexus"]["schema"] == "nexus_public_workflow_blueprint_v1"
    assert g["l3_statistics"]["schema"] == "l3_energy_bootstrap_stub_v1"
    assert g["driver_surface"]["schema"] == "open_driver_surface_v1"


def test_parity_snapshot_includes_gap_bundle_by_default() -> None:
    cfg = ExperimentConfig(
        experiment_id="x",
        random_seed=0,
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates_bohr=[[0, 0, 0], [0, 0, 1.4]]),
        active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
    )
    snap = collect_repro_metadata(cfg)["parity_snapshot"]
    assert "open_gap_closure_reference" in snap
    assert snap["open_gap_closure_reference"]["schema"] == "open_gap_closure_reference_v1"


def test_greedy_commuting_layers_partition_uccsd() -> None:
    gens = build_spin_uccsd_fermion_generators(4, 2)
    layers = GreedyCommutingFermionicLayers().regroup_into_layers(gens)
    assert sum(len(L) for L in layers) == len(gens)
    assert len(layers) >= 1


def test_expectation_qubit_operator_dense_Z0() -> None:
    op = QubitOperator("Z0", 1.0)
    psi = np.array([1.0, 0.0], dtype=np.complex128)
    assert expectation_qubit_operator_dense(op, psi) == pytest.approx(1.0)


def test_dmet_uniform_multifragment_toy_pipeline_smoke() -> None:
    pytest.importorskip("pyscf")
    cfg = ExperimentConfig(
        experiment_id="multi_toy",
        random_seed=1,
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates_bohr=[[0, 0, 0], [0, 0, 1.4]]),
        scf=SCFSpec(method="RHF"),
        active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
        backend=BackendSpecConfig(provider="statevector"),
        quantum=QuantumSpec(algorithm="vqe", vqe_depth=1, vqe_maxiter=30, use_pauli_protocol=False),
        embedding=EmbeddingSpec(
            mode="dmet",
            fragment_labels=["A", "B"],
            dmet_uniform_multifragment_toy=True,
        ),
    )
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    out = run_pipeline_sync(cfg)
    toy = out.get("dmet_uniform_multifragment_toy")
    assert toy is not None
    assert toy.get("schema") == "dmet_uniform_multifragment_toy_v1"
    assert toy.get("converged") is True
