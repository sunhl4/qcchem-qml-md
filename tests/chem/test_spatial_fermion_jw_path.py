"""Restricted spatial → :class:`openfermion.FermionOperator` → JW parity vs InteractionOperator path."""

from __future__ import annotations

import numpy as np
import pytest
from openfermion import InteractionOperator, jordan_wigner
from openfermion.chem.molecular_data import spinorb_from_spatial
from openfermion.linalg import get_sparse_operator
from openfermion.transforms.opconversions.conversions import get_fermion_operator

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.fermion import FermionSpace
from qchem_stack.chem.hamiltonian import (
    qubit_hamiltonian_from_compact_restricted_active_space,
    qubit_hamiltonian_from_spatial_chemist_integrals,
)
from qchem_stack.chem.integral_convention import spatial_mo_eri_pyscf_to_openfermion_mo_ordering
from qchem_stack.chem.jordan_wigner_sparse import jordan_wigner_interaction_operator_sparse
from qchem_stack.chem.molecular_problem import build_restricted_active_space_quantum_problem
from qchem_stack.chem.molecular_problem_build import (
    restricted_active_space_quantum_problem_from_config,
)
from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input
from qchem_stack.chem.restricted_integral_operator import (
    RestrictedActiveSpaceIntegralOperatorCompact,
)
from qchem_stack.chem.spatial_restricted_fermion import (
    restricted_spatial_integrals_to_fermion_operator,
)
from qchem_stack.config import ActiveSpaceSpec, load_experiment_config
from qchem_stack.config.active_space_mapping_specs import ActiveSpaceMappingSpec
from qchem_stack.config.active_space_specs import ActiveSpaceCasSpec, ActiveSpaceJwSpec
from tests.helpers.paths import configs_path, repo_root

pytest.importorskip("pyscf")
from tests.fixtures.classical_reference import pyscf_rhf_from_config

_ROOT = repo_root()
_CFG_H2 = configs_path("example_h2.yaml")


def _as_reference(rhf) -> ClassicalMeanFieldReference:
    return ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy,
        molecular_system=rhf.molecular_system,
        driver_meta=dict(rhf.driver_meta),
    )


def _cfg_with_jw_flags(
    cfg,
    *,
    prefer_restricted_spatial: bool | None = None,
    coeff_atol: float | None = None,
):
    jw_updates: dict[str, object] = {}
    if prefer_restricted_spatial is not None:
        jw_updates["prefer_restricted_spatial"] = prefer_restricted_spatial
    if coeff_atol is not None:
        jw_updates["coeff_atol"] = coeff_atol
    jw = cfg.active_space.jw.model_copy(update=jw_updates)
    active = cfg.active_space.model_copy(update={"jw": jw})
    return cfg.model_copy(update={"active_space": active})


def _dense_max_diff(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.max(np.abs(a - b)))


def test_restricted_spatial_fermion_equals_get_fermion_operator_h2_cas() -> None:
    cfg = load_experiment_config(_CFG_H2)
    rhf = pyscf_rhf_from_config(cfg)
    compact = RestrictedActiveSpaceIntegralOperatorCompact.from_pyscf_rhf(
        rhf,
        n_active_orbitals=cfg.active_space.cas.n_orbitals,
        n_active_electrons=cfg.active_space.cas.n_electrons,
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
    rhf = pyscf_rhf_from_config(cfg)
    compact = RestrictedActiveSpaceIntegralOperatorCompact.from_pyscf_rhf(
        rhf,
        n_active_orbitals=cfg.active_space.cas.n_orbitals,
        n_active_electrons=cfg.active_space.cas.n_electrons,
    )
    mol_op = compact.to_interaction_operator()
    n_so = int(mol_op.one_body_tensor.shape[0])
    fs = FermionSpace(n_spin_orbitals=n_so, n_electrons=cfg.active_space.cas.n_electrons)

    from qchem_stack.chem.hamiltonian import qubit_hamiltonian_from_active_space_fermionic_operator

    qh_ref = qubit_hamiltonian_from_active_space_fermionic_operator(
        mol_op,
        fs,
        n_active_orbitals=cfg.active_space.cas.n_orbitals,
        n_active_electrons=cfg.active_space.cas.n_electrons,
        fermion_qubit_mapping="jordan_wigner",
        rhf=_as_reference(rhf),
    )
    qh_sp = qubit_hamiltonian_from_compact_restricted_active_space(
        compact,
        fs,
        n_active_orbitals=cfg.active_space.cas.n_orbitals,
        n_active_electrons=cfg.active_space.cas.n_electrons,
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
    rhf = pyscf_rhf_from_config(cfg)
    ref = _as_reference(rhf)
    p0 = build_restricted_active_space_quantum_problem(
        ref,
        n_active_orbitals=cfg.active_space.cas.n_orbitals,
        n_active_electrons=cfg.active_space.cas.n_electrons,
        fermion_qubit_mapping="jordan_wigner",
    )
    p1 = build_restricted_active_space_quantum_problem(
        ref,
        n_active_orbitals=cfg.active_space.cas.n_orbitals,
        n_active_electrons=cfg.active_space.cas.n_electrons,
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


def test_factory_from_config_inherits_prefer_spatial_fermion_from_yaml() -> None:
    cfg = load_experiment_config(_CFG_H2)
    cfg2 = _cfg_with_jw_flags(cfg, prefer_restricted_spatial=True)
    prob = restricted_active_space_quantum_problem_from_config(
        cfg2,
        fermion_qubit_mapping="jordan_wigner",
    )
    assert prob.meta.get("jw_build") == "restricted_spatial_fermion_operator"
    assert prob.qubit_hamiltonian.meta.get("jw_build") == "restricted_spatial_fermion_operator"


def test_factory_explicit_false_overrides_yaml_prefer_spatial() -> None:
    cfg = load_experiment_config(_CFG_H2)
    cfg2 = _cfg_with_jw_flags(cfg, prefer_restricted_spatial=True)
    prob = restricted_active_space_quantum_problem_from_config(
        cfg2,
        fermion_qubit_mapping="jordan_wigner",
        prefer_restricted_spatial_fermion_for_jordan_wigner=False,
    )
    assert prob.qubit_hamiltonian.meta.get("jw_build") == "interaction_operator"


def test_factory_from_config_inherits_jordan_wigner_coeff_atol() -> None:
    cfg = load_experiment_config(_CFG_H2)
    cfg2 = _cfg_with_jw_flags(cfg, coeff_atol=1e-15)
    prob = restricted_active_space_quantum_problem_from_config(
        cfg2,
        fermion_qubit_mapping="jordan_wigner",
    )
    assert prob.qubit_hamiltonian.meta.get("jordan_wigner_coeff_atol") == pytest.approx(1e-15)


def test_raises_when_spatial_fermion_path_with_jw_atol() -> None:
    cfg = load_experiment_config(_CFG_H2)
    rhf = pyscf_rhf_from_config(cfg)
    ref = _as_reference(rhf)
    with pytest.raises(ValueError, match="coeff_atol"):
        build_restricted_active_space_quantum_problem(
            ref,
            n_active_orbitals=cfg.active_space.cas.n_orbitals,
            n_active_electrons=cfg.active_space.cas.n_electrons,
            prefer_restricted_spatial_fermion_for_jordan_wigner=True,
            jordan_wigner_coeff_atol=1e-9,
        )


def test_molecular_hamiltonian_from_classical_reference_prefers_spatial_matches_default() -> None:
    cfg = load_experiment_config(_CFG_H2)
    rhf = pyscf_rhf_from_config(cfg)
    ref = _as_reference(rhf)
    qh0 = build_pre_quantum_input(cfg, ref).qubit_hamiltonian
    cfg_spatial = _cfg_with_jw_flags(cfg, prefer_restricted_spatial=True)
    qh1 = build_pre_quantum_input(cfg_spatial, ref).qubit_hamiltonian
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
        cas=ActiveSpaceCasSpec(n_orbitals=2, n_electrons=2),
        jw=ActiveSpaceJwSpec(prefer_restricted_spatial=True),
        mapping=ActiveSpaceMappingSpec(fermion_qubit="jordan_wigner"),
    )
    with pytest.raises(ValueError, match="prefer_restricted_spatial"):
        ActiveSpaceSpec(
            strategy="cas",
            cas=ActiveSpaceCasSpec(n_orbitals=2, n_electrons=2),
            jw=ActiveSpaceJwSpec(prefer_restricted_spatial=True),
            mapping=ActiveSpaceMappingSpec(fermion_qubit="bravyi_kitaev"),
        )
    with pytest.raises(ValueError, match="coeff_atol"):
        ActiveSpaceSpec(
            strategy="cas",
            cas=ActiveSpaceCasSpec(n_orbitals=2, n_electrons=2),
            jw=ActiveSpaceJwSpec(prefer_restricted_spatial=True, coeff_atol=1e-9),
            mapping=ActiveSpaceMappingSpec(fermion_qubit="jordan_wigner"),
        )
