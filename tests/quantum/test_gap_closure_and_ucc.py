"""Open gap-closure bundle, UCC commuting layers, dense expectation reference."""

from __future__ import annotations

import numpy as np
import pytest
from openfermion.ops import QubitOperator

from qchem_stack.chem.kernels.spin_ucc import (
    GreedyCommutingFermionicLayers,
    build_spin_uccsd_fermion_generators,
)
from qchem_stack.config import (
    ActiveSpaceSpec,
    BackendSpecConfig,
    ExperimentConfig,
    MoleculeSpec,
    QuantumSpec,
    SCFSpec,
)
from qchem_stack.integrations.gap_closure_bundle import build_open_gap_closure_reference
from qchem_stack.orchestration.pipeline import collect_repro_metadata
from qchem_stack.tensornet.dense_expectation_reference import expectation_qubit_operator_dense
from tests.embedding_nested import embedding_dmet
from tests.fixtures.classical_reference import pyscf_rhf_from_config
from tests.helpers.paths import configs_path


def test_open_gap_closure_reference_has_schemas() -> None:
    cfg = ExperimentConfig(
        experiment_id="gap",
        random_seed=0,
        molecule=MoleculeSpec(
            symbols=["H", "H"], coordinates=[[0, 0, 0], [0, 0, 1.4]], coordinate_unit="bohr"
        ),
        active_space=ActiveSpaceSpec.model_validate(
            {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
        ),
    )
    g = build_open_gap_closure_reference(cfg)
    assert g["schema"] == "open_gap_closure_reference_v1"
    assert g["ucc"]["chemically_aware_ucc_policy_protocol"].endswith("ChemicallyAwareUCCPolicy")
    assert "build_spin_uccsd_fermion_generators_policy_param" in g["ucc"]
    assert g["ucc"]["n_greedy_commuting_trotter_layers"] >= 1
    assert g["nexus"]["schema"] == "nexus_public_workflow_blueprint_v1"
    assert g["l3_statistics"]["schema"] == "l3_energy_bootstrap_stub_v1"
    assert g["driver_surface"]["schema"] == "open_driver_surface_v1"


def test_parity_snapshot_includes_gap_bundle_by_default() -> None:
    cfg = ExperimentConfig(
        experiment_id="x",
        random_seed=0,
        molecule=MoleculeSpec(
            symbols=["H", "H"], coordinates=[[0, 0, 0], [0, 0, 1.4]], coordinate_unit="bohr"
        ),
        active_space=ActiveSpaceSpec.model_validate(
            {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
        ),
    )
    snap = collect_repro_metadata(cfg)["parity_snapshot"]
    assert "open_gap_closure_reference" in snap
    assert snap["open_gap_closure_reference"]["schema"] == "open_gap_closure_reference_v1"


def test_greedy_commuting_layers_partition_uccsd() -> None:
    gens = build_spin_uccsd_fermion_generators(4, 2)
    layers = GreedyCommutingFermionicLayers().regroup_into_layers(gens)
    assert sum(len(L) for L in layers) == len(gens)
    assert len(layers) >= 1


def test_uccsd_vqe_h2_energy_between_fci_and_rhf() -> None:
    """Dense UCCSD matches PySCF FCI window on Tangelo-aligned JW Hamiltonian."""
    pytest.importorskip("pyscf")

    from qchem_stack.backends.executor_base import StatevectorHeaExecutor
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input
    from qchem_stack.config import load_experiment_config
    from qchem_stack.quantum.algorithms.uccsd_vqe import UCCSDVQE

    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    rhf = pyscf_rhf_from_config(cfg)
    ref = ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy,
        molecular_system=rhf.molecular_system,
        driver_meta=dict(rhf.driver_meta),
    )
    qh = build_pre_quantum_input(cfg, ref).hamiltonian
    ur = UCCSDVQE(qh, executor=StatevectorHeaExecutor()).run(maxiter=400, seed=42)
    assert ur.meta.get("jw_fixed_electron_sector_projection") is True
    e = float(ur.energy)
    assert e <= float(rhf.e_tot) + 1e-3
    e_fci = -1.1372759436170443
    assert e >= e_fci - 5e-3


def test_uccsd_vqe_h2_bravyi_kitaev_energy_window() -> None:
    """Dense BK UCCSD reaches the same physical window as JW (ground state is encoding-invariant)."""
    pytest.importorskip("pyscf")

    from qchem_stack.backends.executor_base import StatevectorHeaExecutor
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input
    from qchem_stack.config import load_experiment_config
    from qchem_stack.quantum.algorithms.uccsd_vqe import UCCSDVQE

    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    rhf = pyscf_rhf_from_config(cfg)
    ref = ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy,
        molecular_system=rhf.molecular_system,
        driver_meta=dict(rhf.driver_meta),
    )
    cfg_bk = cfg.model_copy(
        update={
            "active_space": cfg.active_space.model_copy(
                update={
                    "mapping": cfg.active_space.mapping.model_copy(
                        update={"fermion_qubit": "bravyi_kitaev"}
                    )
                }
            )
        }
    )
    qh = build_pre_quantum_input(cfg_bk, ref).hamiltonian
    ur = UCCSDVQE(qh, executor=StatevectorHeaExecutor()).run(maxiter=400, seed=7)
    assert ur.meta.get("fermion_to_qubit_map") == "bravyi_kitaev"
    assert ur.meta.get("jw_fixed_electron_sector_projection") is False
    e = float(ur.energy)
    assert e <= float(rhf.e_tot) + 1e-3
    e_fci = -1.1372759436170443
    assert e >= e_fci - 6e-3


def test_expectation_qubit_operator_dense_Z0() -> None:
    op = QubitOperator("Z0", 1.0)
    psi = np.array([1.0, 0.0], dtype=np.complex128)
    assert expectation_qubit_operator_dense(op, psi) == pytest.approx(1.0)


def test_dmet_uniform_multifragment_toy_pipeline_smoke() -> None:
    pytest.importorskip("pyscf")
    cfg = ExperimentConfig(
        schema_version="2",
        experiment_id="multi_toy",
        random_seed=1,
        molecule=MoleculeSpec(
            symbols=["H", "H"], coordinates=[[0, 0, 0], [0, 0, 1.4]], coordinate_unit="bohr"
        ),
        scf=SCFSpec(method="RHF"),
        active_space=ActiveSpaceSpec.model_validate(
            {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
        ),
        backend=BackendSpecConfig(provider="statevector"),
        quantum=QuantumSpec(
            algorithm="vqe",
            vqe={"depth": 1, "maxiter": 30},
            pauli={"use_protocol": False},
        ),
        embedding=embedding_dmet(
            fragment_labels=["A", "B"],
            uniform_multifragment_toy=True,
        ),
    )
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    out = run_pipeline_sync(cfg)
    toy = out.get("dmet_uniform_multifragment_toy")
    assert toy is not None
    assert toy.get("schema") == "dmet_uniform_multifragment_toy_v1"
    assert toy.get("converged") is True
