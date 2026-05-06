from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

import numpy as np
from openfermion import (
    InteractionOperator,
    bravyi_kitaev,
    count_qubits,
    get_fermion_operator,
    jordan_wigner,
    symmetry_conserving_bravyi_kitaev,
)
from openfermion.chem.molecular_data import spinorb_from_spatial
from openfermion.linalg import get_sparse_operator
from openfermion.ops import QubitOperator

from qchem_stack.chem.fermion import FermionSpace
from qchem_stack.chem.pauli_term_codec import canonical_pauli_string_from_term

if TYPE_CHECKING:
    from qchem_stack.chem.drivers.pyscf_driver import PySCFRHFResult

FermionQubitMappingName = Literal[
    "jordan_wigner",
    "bravyi_kitaev",
    "symmetry_conserving_bravyi_kitaev",
]


def _interaction_operator_to_qubits(
    mol_op: InteractionOperator,
    mapping: FermionQubitMappingName,
    *,
    n_spin_orbitals: int | None = None,
    n_active_fermions: int | None = None,
) -> QubitOperator:
    if mapping == "jordan_wigner":
        return jordan_wigner(mol_op)
    if mapping == "bravyi_kitaev":
        return bravyi_kitaev(mol_op)
    if mapping == "symmetry_conserving_bravyi_kitaev":
        if n_spin_orbitals is None or n_active_fermions is None:
            raise ValueError(
                "symmetry_conserving_bravyi_kitaev requires n_spin_orbitals and n_active_fermions "
                "(OpenFermion SCBK removes two qubits vs JW on the same active space)."
            )
        fo = get_fermion_operator(mol_op)
        return symmetry_conserving_bravyi_kitaev(fo, int(n_spin_orbitals), int(n_active_fermions))
    raise ValueError(f"Unknown fermion_qubit_mapping: {mapping!r}")


def hamiltonian_fingerprint_from_qubit_operator(
    qop: QubitOperator,
    *,
    max_terms: int | None = None,
) -> tuple[str, bool]:
    """
    Deterministic SHA-256 digest (hex, first 32 chars) over sorted Pauli labels and coefficients.

    Identity term is labeled ``\"I\"``. Coefficients are serialized with ``:.16g``.
    If ``max_terms`` is set, only the first *max_terms* items after sorting are hashed
    and the second return value is ``True`` (truncated fingerprint).
    """
    rows: list[tuple[str, str]] = []
    for term, coeff in sorted(
        qop.terms.items(),
        key=lambda tv: (canonical_pauli_string_from_term(tv[0]), float(tv[1])),
    ):
        label = canonical_pauli_string_from_term(term) if term else "I"
        rows.append((label, f"{float(coeff):.16g}"))
    truncated = False
    if max_terms is not None and len(rows) > max_terms:
        rows = rows[:max_terms]
        truncated = True
    payload = ";".join(f"{a}:{b}" for a, b in rows)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]
    return digest, truncated


@dataclass
class QubitHamiltonian:
    """Qubit operator from a molecular :class:`InteractionOperator` + sparse cache.

    ``meta['fermion_to_qubit_map']`` records the mapping used (e.g. Jordan–Wigner, Bravyi–Kitaev, or SCBK).
    """

    operator: QubitOperator
    n_qubits: int
    fermion_space: FermionSpace | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    def sparse_matrix(self) -> Any:
        return get_sparse_operator(self.operator, n_qubits=self.n_qubits)


def molecular_hamiltonian_from_pyscf(
    rhf: PySCFRHFResult,
    n_active_orbitals: int,
    n_active_electrons: int,
    *,
    fermion_qubit_mapping: FermionQubitMappingName = "jordan_wigner",
) -> QubitHamiltonian:
    """Build active-space molecular Hamiltonian (MO integrals) and map to qubits."""
    from qchem_stack.chem.drivers.pyscf_driver import active_space_integrals

    constant, h1_sp, h2_sp = active_space_integrals(
        rhf, n_active_orbitals=n_active_orbitals, n_active_electrons=n_active_electrons
    )
    h1_so, h2_so = spinorb_from_spatial(h1_sp, h2_sp)
    n_spin = int(h1_so.shape[0])
    mol_op = InteractionOperator(float(constant), h1_so, h2_so)
    qop = _interaction_operator_to_qubits(
        mol_op,
        fermion_qubit_mapping,
        n_spin_orbitals=n_spin,
        n_active_fermions=n_active_electrons,
    )
    n_phys = int(count_qubits(qop))
    fs = FermionSpace(n_spin_orbitals=n_spin, n_electrons=n_active_electrons)
    fp, fp_trunc = hamiltonian_fingerprint_from_qubit_operator(qop)
    meta = {
        "fermion_to_qubit_map": fermion_qubit_mapping,
        "integral_source": "pyscf_active_space",
        "n_active_orbitals": n_active_orbitals,
        "n_active_electrons": n_active_electrons,
        "n_qubits": n_phys,
        "hamiltonian_fingerprint": fp,
    }
    if fp_trunc:
        meta["hamiltonian_fingerprint_truncated"] = True
    if getattr(rhf, "driver_meta", None):
        meta["pyscf_driver"] = dict(rhf.driver_meta)
    return QubitHamiltonian(operator=qop, n_qubits=n_phys, fermion_space=fs, meta=meta)


def qubit_hamiltonian_from_spatial_chemist_integrals(
    constant: float,
    h1: np.ndarray,
    h2: np.ndarray,
    n_electrons: int,
    *,
    fermion_qubit_mapping: FermionQubitMappingName = "jordan_wigner",
    integral_source: str = "spatial_chemist_integrals",
    meta_extra: dict[str, Any] | None = None,
    pyscf_driver_meta: dict[str, Any] | None = None,
) -> QubitHamiltonian:
    """Map spatial MO integrals (chemists' ``h2[p,q,r,s] = (pq|rs)``) to qubits via OpenFermion."""
    h1a = np.asarray(h1, dtype=float)
    h2a = np.asarray(h2, dtype=float)
    norb = int(h1a.shape[0])
    if h1a.shape != (norb, norb):
        raise ValueError("h1 must be (norb, norb)")
    if h2a.shape != (norb, norb, norb, norb):
        raise ValueError("h2 must be (norb, norb, norb, norb)")
    if n_electrons < 0 or n_electrons > 2 * norb or n_electrons % 2 != 0:
        raise ValueError("n_electrons must be even and fit in 2*norb spin orbitals")

    h1_so, h2_so = spinorb_from_spatial(h1a, h2a)
    n_spin = int(h1_so.shape[0])
    mol_op = InteractionOperator(float(constant), h1_so, h2_so)
    qop = _interaction_operator_to_qubits(
        mol_op,
        fermion_qubit_mapping,
        n_spin_orbitals=n_spin,
        n_active_fermions=n_electrons,
    )
    n_phys = int(count_qubits(qop))
    fs = FermionSpace(n_spin_orbitals=n_spin, n_electrons=n_electrons)
    fp, fp_trunc = hamiltonian_fingerprint_from_qubit_operator(qop)
    meta: dict[str, Any] = {
        "fermion_to_qubit_map": fermion_qubit_mapping,
        "integral_source": integral_source,
        "n_active_orbitals": norb,
        "n_active_electrons": n_electrons,
        "n_qubits": n_phys,
        "hamiltonian_fingerprint": fp,
    }
    if fp_trunc:
        meta["hamiltonian_fingerprint_truncated"] = True
    if pyscf_driver_meta:
        meta["pyscf_driver"] = dict(pyscf_driver_meta)
    if meta_extra:
        meta.update(meta_extra)
    return QubitHamiltonian(operator=qop, n_qubits=n_phys, fermion_space=fs, meta=meta)
