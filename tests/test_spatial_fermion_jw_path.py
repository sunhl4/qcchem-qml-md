"""Restricted spatial → :class:`openfermion.FermionOperator` → JW parity vs InteractionOperator path."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from openfermion import InteractionOperator, jordan_wigner
from openfermion.chem.molecular_data import spinorb_from_spatial
from openfermion.linalg import get_sparse_operator
from openfermion.transforms.opconversions.conversions import get_fermion_operator

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.drivers.pyscf_driver import PySCFDriver
from qchem_stack.chem.fermion import FermionSpace
from qchem_stack.chem.hamiltonian import (
    molecular_hamiltonian_from_classical_reference,
    qubit_hamiltonian_from_compact_restricted_active_space,
    qubit_hamiltonian_from_spatial_chemist_integrals,
)
from qchem_stack.chem.integral_convention import spatial_mo_eri_pyscf_to_openfermion_mo_ordering
from qchem_stack.chem.jordan_wigner_sparse import jordan_wigner_interaction_operator_sparse
from qchem_stack.chem.molecular_problem import build_restricted_active_space_quantum_problem
from qchem_stack.chem.restricted_integral_operator import (
    RestrictedActiveSpaceIntegralOperatorCompact,
)
from qchem_stack.chem.spatial_restricted_fermion import (
    restricted_spatial_integrals_to_fermion_operator,
)
from qchem_stack.config import ActiveSpaceSpec, load_experiment_config

pytest.importorskip("pyscf")

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


def _dense_max_diff(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.max(np.abs(a - b)))


def test_restricted_spatial_fermion_equals_get_fermion_operator_h2_cas() -> None:
    cfg = load_experiment_config(_CFG_H2)
    rhf = PySCFDriver.from_config(cfg).run_rhf()
    compact = RestrictedActiveSpaceIntegralOperatorCompact.from_pyscf_rhf(
        rhf,
        n_active_orbitals=cfg.active_space.n_active_orbitals,
        n_active_electrons=cfg.active_space.n_active_electrons,
    )
    h2_of = spatial_mo_eri_pyscf_to_openfermion_mo_ordering(compact.dense_h2_chemist_spatial())
    h1 = np.asarray(compact.h1_active_mo, dtype=float)
    mol_op = compact.to_interaction_operator()

    fo_ref = get_fermion_operator(mol_op)
    fo_sp = restricted_spatial_integrals_to_fermion_operator(float(compact.constant), h1, h2_of)
    assert fo_ref.isclose(fo_sp, tol=1e-12)

    n = int(mol_op.n_qubits)
    m1 = get_sparse_operator(jordan_wigner(fo_sp), n_qubits=n).toarray()
    m2 = get_sparse_operator(jordan_wigner(fo_ref), n_qubits=n).toarray()
    assert _dense_max_diff(m1, m2) < 1e-10


def test_compact_restricted_qubit_hamiltonian_matches_interaction_operator_path() -> None:
    cfg = load_experiment_config(_CFG_H2)
    rhf = PySCFDriver.from_config(cfg).run_rhf()
    compact = RestrictedActiveSpaceIntegralOperatorCompact.from_pyscf_rhf(
        rhf,
        n_active_orbitals=cfg.active_space.n_active_orbitals,
        n_active_electrons=cfg.active_space.n_active_electrons,
    )
    mol_op = compact.to_interaction_operator()
    n_so = int(mol_op.one_body_tensor.shape[0])
    fs = FermionSpace(n_spin_orbitals=n_so, n_electrons=cfg.active_space.n_active_electrons)

    from qchem_stack.chem.hamiltonian import qubit_hamiltonian_from_active_space_fermionic_operator

    qh_ref = qubit_hamiltonian_from_active_space_fermionic_operator(
        mol_op,
        fs,
        n_active_orbitals=cfg.active_space.n_active_orbitals,
        n_active_electrons=cfg.active_space.n_active_electrons,
        fermion_qubit_mapping="jordan_wigner",
        rhf=_as_reference(rhf),
    )
    qh_sp = qubit_hamiltonian_from_compact_restricted_active_space(
        compact,
        fs,
        n_active_orbitals=cfg.active_space.n_active_orbitals,
        n_active_electrons=cfg.active_space.n_active_electrons,
        fermion_qubit_mapping="jordan_wigner",
        rhf=_as_reference(rhf),
    )
    n = qh_ref.n_qubits
    d = _dense_max_diff(
        get_sparse_operator(qh_ref.operator, n_qubits=n).toarray(),
        get_sparse_operator(qh_sp.operator, n_qubits=n).toarray(),
    )
    assert d < 1e-10
    assert qh_sp.meta.get("jw_build") == "restricted_spatial_fermion_operator"


def test_build_problem_prefer_spatial_matches_default() -> None:
    cfg = load_experiment_config(_CFG_H2)
    rhf = PySCFDriver.from_config(cfg).run_rhf()
    ref = _as_reference(rhf)
    p0 = build_restricted_active_space_quantum_problem(
        ref,
        n_active_orbitals=cfg.active_space.n_active_orbitals,
        n_active_electrons=cfg.active_space.n_active_electrons,
        fermion_qubit_mapping="jordan_wigner",
    )
    p1 = build_restricted_active_space_quantum_problem(
        ref,
        n_active_orbitals=cfg.active_space.n_active_orbitals,
        n_active_electrons=cfg.active_space.n_active_electrons,
        fermion_qubit_mapping="jordan_wigner",
        prefer_restricted_spatial_fermion_for_jordan_wigner=True,
    )
    n = p0.qubit_hamiltonian.n_qubits
    d = _dense_max_diff(
        get_sparse_operator(p0.qubit_hamiltonian.operator, n_qubits=n).toarray(),
        get_sparse_operator(p1.qubit_hamiltonian.operator, n_qubits=n).toarray(),
    )
    assert d < 1e-10
    assert p1.meta.get("jw_build") == "restricted_spatial_fermion_operator"


def test_spatial_chemist_prefer_fermion_matches_spinorb_path() -> None:
    pytest.importorskip("pyscf")
    from pyscf import ao2mo, gto, mcscf, scf

    mol = gto.M(atom="H 0 0 0; H 0 0 1.4", unit="Bohr", basis="sto-3g")
    mf = scf.RHF(mol).run()
    cas = mcscf.CASCI(mf, 2, 2)
    h1, e_core = cas.get_h1eff(mf.mo_coeff)
    h2 = cas.get_h2eff(mf.mo_coeff)
    if h2.ndim != 4:
        h2 = ao2mo.restore(1, h2, 2)
    qh_def = qubit_hamiltonian_from_spatial_chemist_integrals(
        float(e_core), np.asarray(h1, dtype=float), np.asarray(h2, dtype=float), 2
    )
    qh_sp = qubit_hamiltonian_from_spatial_chemist_integrals(
        float(e_core),
        np.asarray(h1, dtype=float),
        np.asarray(h2, dtype=float),
        2,
        prefer_restricted_spatial_fermion_for_jordan_wigner=True,
    )
    n = qh_def.n_qubits
    d = _dense_max_diff(
        get_sparse_operator(qh_def.operator, n_qubits=n).toarray(),
        get_sparse_operator(qh_sp.operator, n_qubits=n).toarray(),
    )
    assert d < 1e-10


def test_jordan_wigner_sparse_zero_atol_matches_openfermion() -> None:
    norb = 2
    rng = np.random.default_rng(0)
    h1 = rng.standard_normal((norb, norb))
    h1 = 0.5 * (h1 + h1.T)
    h2 = rng.standard_normal((norb,) * 4)
    h2 = 0.5 * (h2 + np.transpose(h2, (3, 2, 1, 0)))
    h2_of = spatial_mo_eri_pyscf_to_openfermion_mo_ordering(np.asarray(h2, dtype=float))
    h1_so, h2_so = spinorb_from_spatial(np.asarray(h1, dtype=float), h2_of)
    mol_op = InteractionOperator(0.1, h1_so, 0.5 * h2_so)
    q0 = jordan_wigner(mol_op)
    q1 = jordan_wigner_interaction_operator_sparse(mol_op, atol=None)
    q2 = jordan_wigner_interaction_operator_sparse(mol_op, atol=0.0)
    n = int(mol_op.n_qubits)
    m0 = get_sparse_operator(q0, n_qubits=n).toarray()
    assert _dense_max_diff(m0, get_sparse_operator(q1, n_qubits=n).toarray()) < 1e-12
    assert _dense_max_diff(m0, get_sparse_operator(q2, n_qubits=n).toarray()) < 1e-12


def test_driver_from_config_inherits_prefer_spatial_fermion_from_yaml() -> None:
    cfg = load_experiment_config(_CFG_H2)
    cx = cfg.active_space.model_copy(
        update={"prefer_restricted_spatial_fermion_for_jordan_wigner": True}
    )
    cfg2 = cfg.model_copy(update={"active_space": cx})
    drv = PySCFDriver.from_config(cfg2)
    prob = drv.get_restricted_active_space_quantum_problem(
        cfg2.active_space.n_active_orbitals,
        cfg2.active_space.n_active_electrons,
        fermion_qubit_mapping="jordan_wigner",
    )
    assert prob.meta.get("jw_build") == "restricted_spatial_fermion_operator"
    assert prob.qubit_hamiltonian.meta.get("jw_build") == "restricted_spatial_fermion_operator"


def test_driver_explicit_false_overrides_yaml_prefer_spatial() -> None:
    cfg = load_experiment_config(_CFG_H2)
    cx = cfg.active_space.model_copy(
        update={"prefer_restricted_spatial_fermion_for_jordan_wigner": True}
    )
    cfg2 = cfg.model_copy(update={"active_space": cx})
    drv = PySCFDriver.from_config(cfg2)
    prob = drv.get_restricted_active_space_quantum_problem(
        cfg2.active_space.n_active_orbitals,
        cfg2.active_space.n_active_electrons,
        fermion_qubit_mapping="jordan_wigner",
        prefer_restricted_spatial_fermion_for_jordan_wigner=False,
    )
    assert prob.qubit_hamiltonian.meta.get("jw_build") == "interaction_operator"


def test_driver_from_config_inherits_jordan_wigner_coeff_atol() -> None:
    cfg = load_experiment_config(_CFG_H2)
    cx = cfg.active_space.model_copy(update={"jordan_wigner_coeff_atol": 1e-15})
    cfg2 = cfg.model_copy(update={"active_space": cx})
    drv = PySCFDriver.from_config(cfg2)
    prob = drv.get_restricted_active_space_quantum_problem(
        cfg2.active_space.n_active_orbitals,
        cfg2.active_space.n_active_electrons,
        fermion_qubit_mapping="jordan_wigner",
    )
    assert prob.qubit_hamiltonian.meta.get("jordan_wigner_coeff_atol") == pytest.approx(1e-15)


def test_raises_when_spatial_fermion_path_with_jw_atol() -> None:
    cfg = load_experiment_config(_CFG_H2)
    rhf = PySCFDriver.from_config(cfg).run_rhf()
    ref = _as_reference(rhf)
    with pytest.raises(ValueError, match="jordan_wigner_coeff_atol"):
        build_restricted_active_space_quantum_problem(
            ref,
            n_active_orbitals=cfg.active_space.n_active_orbitals,
            n_active_electrons=cfg.active_space.n_active_electrons,
            prefer_restricted_spatial_fermion_for_jordan_wigner=True,
            jordan_wigner_coeff_atol=1e-9,
        )


def test_molecular_hamiltonian_from_classical_reference_prefers_spatial_matches_default() -> None:
    cfg = load_experiment_config(_CFG_H2)
    rhf = PySCFDriver.from_config(cfg).run_rhf()
    ref = _as_reference(rhf)
    qh0 = molecular_hamiltonian_from_classical_reference(
        ref,
        cfg.active_space.n_active_orbitals,
        cfg.active_space.n_active_electrons,
        fermion_qubit_mapping="jordan_wigner",
    )
    qh1 = molecular_hamiltonian_from_classical_reference(
        ref,
        cfg.active_space.n_active_orbitals,
        cfg.active_space.n_active_electrons,
        fermion_qubit_mapping="jordan_wigner",
        prefer_restricted_spatial_fermion_for_jordan_wigner=True,
    )
    n = qh0.n_qubits
    assert (
        _dense_max_diff(
            get_sparse_operator(qh0.operator, n_qubits=n).toarray(),
            get_sparse_operator(qh1.operator, n_qubits=n).toarray(),
        )
        < 1e-10
    )
    assert qh1.meta.get("jw_build") == "restricted_spatial_fermion_operator"


def test_active_space_spec_validates_jw_optimizer_combo() -> None:
    ActiveSpaceSpec(
        strategy="cas",
        ncas=2,
        nelecas=2,
        prefer_restricted_spatial_fermion_for_jordan_wigner=True,
        fermion_qubit_mapping="jordan_wigner",
    )
    with pytest.raises(ValueError, match="prefer_restricted_spatial_fermion_for_jordan_wigner"):
        ActiveSpaceSpec(
            strategy="cas",
            ncas=2,
            nelecas=2,
            prefer_restricted_spatial_fermion_for_jordan_wigner=True,
            fermion_qubit_mapping="bravyi_kitaev",
        )
    with pytest.raises(ValueError, match="jordan_wigner_coeff_atol"):
        ActiveSpaceSpec(
            strategy="cas",
            ncas=2,
            nelecas=2,
            prefer_restricted_spatial_fermion_for_jordan_wigner=True,
            jordan_wigner_coeff_atol=1e-9,
            fermion_qubit_mapping="jordan_wigner",
        )
