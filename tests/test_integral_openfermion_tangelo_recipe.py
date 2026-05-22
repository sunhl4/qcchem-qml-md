"""Molecular integral bridge: PySCF + Tangelo/OpenFermion reordering + InteractionOperator ½.

Reference procedure (SandboxAQ Tangelo ``SecondQuantizedMolecule._get_fermionic_hamiltonian``):

1. Spatial MO ERIs from PySCF ``ao2mo`` / CASCI ``get_h2eff`` (chemist, restored 4-index).
2. ``numpy.transpose(h2, (0, 2, 3, 1))``.
3. :func:`openfermion.chem.molecular_data.spinorb_from_spatial`.
4. :class:`openfermion.InteractionOperator` with ``two_body = 0.5 *`` spin-orbital tensor.

See ``src/qchem_stack/chem/integral_convention.py`` and ``active_space_integrals``.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from openfermion import InteractionOperator, jordan_wigner, jw_hartree_fock_state
from openfermion.chem.molecular_data import spinorb_from_spatial
from openfermion.linalg import get_sparse_operator
from openfermion.linalg.sparse_tools import jw_number_indices
from pyscf import ao2mo, fci, gto, mcscf, scf

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.integral_convention import spatial_mo_eri_pyscf_to_openfermion_mo_ordering
from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input
from qchem_stack.config import load_experiment_config
from tests.fixtures.classical_reference import pyscf_rhf_from_config

pyscf = pytest.importorskip("pyscf")

_ROOT = Path(__file__).resolve().parents[1]
_CFG_H2 = _ROOT / "configs" / "example_h2.yaml"


def _as_reference(rhf) -> ClassicalMeanFieldReference:
    return ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy,
        molecular_system=rhf.molecular_system,
        driver_meta=dict(rhf.driver_meta),
    )


def test_h2_sector_ground_matches_pyscf_fci() -> None:
    mol = gto.M(atom="H 0 0 0; H 0 0 1.4", unit="Bohr", basis="sto-3g")
    mf = scf.RHF(mol).run()
    e_fci = float(fci.FCI(mol, mf.mo_coeff).kernel()[0])

    cfg = load_experiment_config(_CFG_H2)
    rhf = pyscf_rhf_from_config(cfg)
    qh = build_pre_quantum_input(cfg, _as_reference(rhf)).hamiltonian
    H = get_sparse_operator(qh.operator, n_qubits=qh.n_qubits).toarray()
    ne = int(qh.fermion_space.n_electrons)
    nq = int(qh.n_qubits)
    idx = sorted(jw_number_indices(ne, nq))
    P = np.zeros((2**nq, len(idx)), dtype=np.complex128)
    for j, i in enumerate(idx):
        P[i, j] = 1.0
    Hsub = P.conj().T @ H @ P
    emin = float(np.linalg.eigvalsh((Hsub + Hsub.conj().T) / 2)[0])
    assert emin == pytest.approx(e_fci, abs=1e-6)
    psi = np.asarray(jw_hartree_fock_state(ne, nq), dtype=np.complex128).ravel()
    e_hf = float(np.vdot(psi, H @ psi).real)
    assert e_hf == pytest.approx(float(rhf.e_tot), abs=1e-8)


def test_transpose_matches_explicit_tangelo_recipe() -> None:
    """Dense JW Hamiltonian equals manual Tangelo recipe on CAS(2,2) integrals."""
    mol = gto.M(atom="H 0 0 0; H 0 0 1.4", unit="Bohr", basis="sto-3g")
    mf = scf.RHF(mol).run()
    cas = mcscf.CASCI(mf, 2, 2)
    h1, e_core = cas.get_h1eff(mf.mo_coeff)
    h2 = cas.get_h2eff(mf.mo_coeff)
    if h2.ndim != 4:
        h2 = ao2mo.restore(1, h2, 2)
    h2 = np.asarray(h2, dtype=float)
    h2_t = spatial_mo_eri_pyscf_to_openfermion_mo_ordering(h2)
    h1_so, h2_so = spinorb_from_spatial(h1, h2_t)
    mol_op = InteractionOperator(float(e_core), h1_so, 0.5 * h2_so)
    qop_ref = jordan_wigner(mol_op)

    cfg = load_experiment_config(_CFG_H2)
    rhf = pyscf_rhf_from_config(cfg)
    qh = build_pre_quantum_input(cfg, _as_reference(rhf)).hamiltonian
    m1 = get_sparse_operator(qh.operator, n_qubits=4).toarray()
    m2 = get_sparse_operator(qop_ref, n_qubits=4).toarray()
    assert float(np.max(np.abs(m1 - m2))) < 1e-10


def test_optional_tangelo_package_matches_if_installed() -> None:
    """When ``tangelo`` imports, ``SecondQuantizedMolecule`` JW Hamiltonian matches ours (H₂)."""
    try:
        from tangelo import SecondQuantizedMolecule  # type: ignore[import-not-found]
        from tangelo.toolboxes.qubit_mappings import (
            jordan_wigner as tangelo_jw,  # type: ignore[import-not-found]
        )
    except Exception:
        pytest.skip("tangelo not installed (optional upstream parity)")

    bohr_to_ang = 0.529177210903
    z_ang = 1.4 * bohr_to_ang
    h2_list = [("H", (0.0, 0.0, 0.0)), ("H", (0.0, 0.0, z_ang))]
    mol_t = SecondQuantizedMolecule(h2_list, q=0, spin=0, basis="sto-3g")
    q_t = tangelo_jw(mol_t.fermionic_hamiltonian)

    cfg = load_experiment_config(_CFG_H2)
    rhf = pyscf_rhf_from_config(cfg)
    qh = build_pre_quantum_input(cfg, _as_reference(rhf)).hamiltonian
    m1 = get_sparse_operator(qh.operator, n_qubits=4).toarray()
    m2 = get_sparse_operator(q_t, n_qubits=4).toarray()
    assert float(np.max(np.abs(m1 - m2))) < 1e-5
