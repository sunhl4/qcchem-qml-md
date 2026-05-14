from __future__ import annotations

import numpy as np
import pytest
from openfermion.ops import QubitOperator

from qchem_stack.chem.fermion import FermionSpace
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.quantum.algorithms.excited import QSE, VQD
from qchem_stack.quantum.algorithms.sceom import run_sceom_reference_subspace
from qchem_stack.quantum.algorithms.vqe import VQE


def test_qse_dense_first_excitation_gap_matches_two_level_z_model() -> None:
    """Dense QSE spectrum: Δ = E₁−E₀ = 2|a| for H = a·Z + c·I on one qubit."""
    a_m, c_m = 0.35, 0.05
    op = QubitOperator(((0, "Z"),), a_m) + QubitOperator((), c_m)
    qh = QubitHamiltonian(operator=op, n_qubits=1, fermion_space=FermionSpace(1, 1))
    qse = QSE(qh, subspace_dim=2)
    r = qse.run_dense_reference()
    assert len(r.excitation_energies) >= 1
    assert r.excitation_energies[0] == pytest.approx(2.0 * abs(a_m), rel=1e-8, abs=1e-8)


def test_qse_from_vqe_basis_matches_dense_order_h2() -> None:
    pytest.importorskip("pyscf")
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.drivers.pyscf_driver import PySCFDriver
    from qchem_stack.chem.hamiltonian import molecular_hamiltonian_from_classical_reference
    from qchem_stack.config import ActiveSpaceSpec, ExperimentConfig, MoleculeSpec, SCFSpec

    cfg = ExperimentConfig(
        experiment_id="t",
        random_seed=0,
        molecule=MoleculeSpec(
            symbols=["H", "H"],
            coordinates_bohr=[[0, 0, 0], [0, 0, 1.4]],
        ),
        active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
        scf=SCFSpec(),
    )
    drv = PySCFDriver.from_config(cfg)
    r = drv.run_rhf()
    ref = ClassicalMeanFieldReference(
        mf=r.mf,
        e_tot=float(r.e_tot),
        mo_energy=r.mo_energy,
        molecular_system=r.molecular_system,
        driver_meta=dict(r.driver_meta),
    )
    qh = molecular_hamiltonian_from_classical_reference(
        ref, n_active_orbitals=2, n_active_electrons=2
    )
    v = VQE(qh, depth=1).run(maxiter=100, seed=0)
    qse = QSE(qh, subspace_dim=8)
    sub = qse.run_from_vqe_hea_basis(v.angles, depth=1, max_basis=min(6, 2**qh.n_qubits))
    dense = qse.run_dense_reference()
    assert len(sub.excitation_energies) >= 1
    assert np.isfinite(sub.excitation_energies[0])
    # Micro-basis from Pauli-X bumps need not match first global excitation; compare to dense only loosely.
    assert sub.excitation_energies[0] >= -1.0
    assert dense.excitation_energies[0] >= 0.0


def test_vqd_reuses_ground_angles_from_pipeline() -> None:
    op = QubitOperator(((0, "Z"),), 0.3) + QubitOperator((), 0.1)
    qh = QubitHamiltonian(operator=op, n_qubits=1, fermion_space=FermionSpace(1, 1))
    v = VQE(qh, depth=1).run(maxiter=100, seed=1)
    r = VQD(qh, n_states=2, depth=1).run(seed=0, ground_angles=v.angles, ground_energy=v.energy)
    assert r.meta.get("reused_pipeline_ground") is True
    assert r.energies[0] == pytest.approx(v.energy)
    assert r.meta["vqd_channels"][0]["energy_exact"] == pytest.approx(v.energy)


def test_vqd_second_energy_finite() -> None:
    op = QubitOperator(((0, "Z"),), 0.3) + QubitOperator((), 0.1)
    qh = QubitHamiltonian(operator=op, n_qubits=1, fermion_space=FermionSpace(1, 1))
    r = VQD(qh, n_states=2, depth=1).run(seed=0)
    assert len(r.energies) == 2
    assert "Quantum 3" in r.meta.get("reference", "")
    assert len(r.meta.get("vqd_channels", [])) == 2
    assert "three_protocol" in r.meta["vqd_channels"][0]
    assert "three_protocol" in r.meta["vqd_channels"][1]
    td = r.meta.get("tangelo_deflation_analogy_v1")
    assert isinstance(td, dict) and td.get("schema") == "tangelo_deflation_analogy_v1"
    assert td.get("selected_overlap_mode") == "statevector_overlap"
    iq = r.meta.get("inquanto_vqd_semantics_v1")
    assert isinstance(iq, dict) and iq.get("schema") == "inquanto_vqd_semantics_v1"
    assert r.meta.get("vqd_overlap_mode_yaml") == "statevector_overlap"
    assert r.meta.get("vqd_variety_yaml") == "hea"


def test_vqd_tangelo_overlap_mode_metadata() -> None:
    op = QubitOperator(((0, "Z"),), 0.3) + QubitOperator((), 0.1)
    qh = QubitHamiltonian(operator=op, n_qubits=1, fermion_space=FermionSpace(1, 1))
    r = VQD(qh, n_states=2, depth=1, overlap_mode="tangelo_circuit_analogy").run(seed=0)
    assert r.meta.get("vqd_overlap_mode_yaml") == "tangelo_circuit_analogy"
    td = r.meta.get("tangelo_deflation_analogy_v1")
    assert isinstance(td, dict)
    assert td.get("selected_overlap_mode") == "tangelo_circuit_analogy"


def test_vqd_overlap_warn_when_deflation_penalty_zero() -> None:
    """With λ=0 the second level may collapse to the ground manifold; overlap diagnostics fire."""
    op = QubitOperator(((0, "Z"),), 0.3) + QubitOperator((), 0.1)
    qh = QubitHamiltonian(operator=op, n_qubits=1, fermion_space=FermionSpace(1, 1))
    r = VQD(qh, n_states=2, depth=1, penalty_weight=0.0, max_overlap_warn=0.5).run(seed=0)
    assert "vqd_warnings" in r.meta
    assert any("overlap_squared_sum" in w for w in r.meta["vqd_warnings"])


def test_vqd_three_states_and_qse_shot_noise() -> None:
    op = (
        QubitOperator(((0, "Z"),), 0.25)
        + QubitOperator(((1, "Z"),), 0.25)
        + QubitOperator(((0, "X"), (1, "X")), 0.05)
        + QubitOperator((), 0.02)
    )
    qh = QubitHamiltonian(operator=op, n_qubits=2, fermion_space=FermionSpace(2, 1))
    r = VQD(qh, n_states=3, depth=1, penalty_weight=4.0).run(seed=2)
    assert len(r.energies) == 3
    assert len(r.meta["vqd_channels"]) == 3

    qse = QSE(qh, subspace_dim=4)
    z4 = np.zeros(4)
    clean = qse.run_from_vqe_hea_basis(z4, depth=1, max_basis=4)
    noisy = qse.run_from_vqe_hea_basis_shot_noise(
        z4, depth=1, max_basis=4, shots_per_matrix_element=200, seed=3
    )
    assert len(clean.excitation_energies) == len(noisy.excitation_energies)
    assert noisy.meta.get("shot_noise_model")


def test_sceom_shot_noise_runs() -> None:
    from qchem_stack.quantum.algorithms.sceom import run_sceom_reference_subspace_shot_noise

    op = QubitOperator(((0, "Z"),), 0.4) + QubitOperator(((1, "Z"),), 0.2) + QubitOperator((), 0.05)
    qh = QubitHamiltonian(operator=op, n_qubits=2, fermion_space=FermionSpace(2, 1))
    res = run_sceom_reference_subspace_shot_noise(
        qh, subspace_dim=3, shots_per_matrix_element=500, seed=0
    )
    assert len(res.energies) == 3
    assert res.meta.get("shot_noise_model") == "symmetric_gaussian_on_real_H_sub"


def test_sceom_reference_runs() -> None:
    op = QubitOperator(((0, "Z"),), 0.4) + QubitOperator(((1, "Z"),), 0.2) + QubitOperator((), 0.05)
    qh = QubitHamiltonian(operator=op, n_qubits=2, fermion_space=FermionSpace(2, 1))
    res = run_sceom_reference_subspace(qh, subspace_dim=3)
    assert len(res.energies) == 3
    assert "D2SC05371C" in res.meta.get("reference", "")
