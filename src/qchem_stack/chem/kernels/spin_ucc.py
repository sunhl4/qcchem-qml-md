"""Spin-UCC fermionic generator kernels (chemistry-aware regrouping hooks).

L3 shared kernel: used by quantum operator pools and UCCSD variational ansätze.
"""

from __future__ import annotations

import itertools
from typing import Any, Protocol, runtime_checkable

from openfermion.ops import FermionOperator

from qchem_stack.chem.tolerances import SPIN_UCC_COMMUTATOR_TOLERANCE


@runtime_checkable
class ChemicallyAwareUCCPolicy(Protocol):
    """Published-regrouping hook (implement with algorithms from the literature only)."""

    def regroup_generators(self, ops: list[FermionOperator]) -> list[FermionOperator]:
        """Return reordered or merged fermionic generators (same algebra up to Trotter error)."""
        ...


class IdentityRegrouping:
    """No regrouping: baseline for comparing gate counts against future policies."""

    def regroup_generators(self, ops: list[FermionOperator]) -> list[FermionOperator]:
        return list(ops)


class SinglesBeforeDoublesLexicographic:
    """
    **Open** chemically-motivated ordering: singles (two fermionic indices) before doubles (four).

    Lexicographic tie-break on the term tuple. Not identical to proprietary vendor regrouping.
    """

    def regroup_generators(self, ops: list[FermionOperator]) -> list[FermionOperator]:
        def sort_key(op: FermionOperator) -> tuple[int, tuple[Any, ...]]:
            terms = list(op.terms.items())
            if len(terms) != 1:
                return (99, ())
            ((t, _c),) = terms
            rank = 0 if len(t) == 2 else 1
            return (rank, t)

        return sorted(ops, key=sort_key)


class GreedyCommutingFermionicLayers:
    """
    Partition generators into layers of mutually **commuting** fermionic operators (OpenFermion commutator).

    Flattened order is layer-by-layer; Trotter depth lower bound proxy = number of layers.
    """

    tol: float = SPIN_UCC_COMMUTATOR_TOLERANCE

    def _commutes(self, a: FermionOperator, b: FermionOperator) -> bool:
        from openfermion import commutator

        c = commutator(a, b)
        if not c.terms:
            return True
        n = float(sum(abs(v) ** 2 for v in c.terms.values()) ** 0.5)
        return n < self.tol

    def regroup_into_layers(self, ops: list[FermionOperator]) -> list[list[FermionOperator]]:
        layers: list[list[FermionOperator]] = []
        for op in ops:
            placed = False
            for layer in layers:
                if all(self._commutes(op, exist) for exist in layer):
                    layer.append(op)
                    placed = True
                    break
            if not placed:
                layers.append([op])
        return layers

    def regroup_generators(self, ops: list[FermionOperator]) -> list[FermionOperator]:
        return [g for layer in self.regroup_into_layers(ops) for g in layer]


def count_uccsd_excitations(n_spin_orbitals: int, n_electrons: int) -> dict[str, int]:
    """Closed-shell-style spin counts: indices ``0..ne-1`` occupied, ``ne..n_so-1`` virtual."""
    if n_electrons > n_spin_orbitals or n_electrons < 0:
        raise ValueError("invalid n_electrons vs n_spin_orbitals")
    n_virt = n_spin_orbitals - n_electrons
    n_singles = n_electrons * n_virt
    n_occ_pairs = n_electrons * (n_electrons - 1) // 2
    n_virt_pairs = n_virt * (n_virt - 1) // 2
    n_doubles = n_occ_pairs * n_virt_pairs
    return {"n_single_excitations": n_singles, "n_double_excitations": n_doubles}


def build_spin_ucc_doubles_only_fermion_generators(
    n_spin_orbitals: int,
    n_electrons: int,
    *,
    policy: ChemicallyAwareUCCPolicy | None = None,
) -> list[FermionOperator]:
    """Doubles-only fermionic raising operators — spin-orbital paired excitations ``ij→ab``."""
    occ = list(range(n_electrons))
    virt = list(range(n_electrons, n_spin_orbitals))
    ops: list[FermionOperator] = []
    for i, j in itertools.combinations(occ, 2):
        for a, b in itertools.combinations(virt, 2):
            ops.append(FermionOperator(((b, 1), (a, 1), (j, 0), (i, 0)), 1.0))
    pol = policy or IdentityRegrouping()
    return pol.regroup_generators(ops)


def build_spin_ucc_singles_only_fermion_generators(
    n_spin_orbitals: int,
    n_electrons: int,
    *,
    policy: ChemicallyAwareUCCPolicy | None = None,
) -> list[FermionOperator]:
    """Singles-only (UCCS-style) fermionic raising operators — doubles omitted."""
    occ = list(range(n_electrons))
    virt = list(range(n_electrons, n_spin_orbitals))
    ops: list[FermionOperator] = []
    for i in occ:
        for a in virt:
            ops.append(FermionOperator(((a, 1), (i, 0)), 1.0))
    pol = policy or IdentityRegrouping()
    return pol.regroup_generators(ops)


def build_spin_uccsd_fermion_generators(
    n_spin_orbitals: int,
    n_electrons: int,
    *,
    policy: ChemicallyAwareUCCPolicy | None = None,
) -> list[FermionOperator]:
    """Build spin-orbital UCCSD excitation (raising) operators as :class:`FermionOperator` terms."""
    occ = list(range(n_electrons))
    virt = list(range(n_electrons, n_spin_orbitals))
    ops: list[FermionOperator] = []
    for i in occ:
        for a in virt:
            ops.append(FermionOperator(((a, 1), (i, 0)), 1.0))
    for i, j in itertools.combinations(occ, 2):
        for a, b in itertools.combinations(virt, 2):
            ops.append(FermionOperator(((b, 1), (a, 1), (j, 0), (i, 0)), 1.0))
    pol = policy or IdentityRegrouping()
    return pol.regroup_generators(ops)


def build_spin_uccgd_fermion_generators(
    n_spin_orbitals: int,
    n_electrons: int,
    *,
    policy: ChemicallyAwareUCCPolicy | None = None,
) -> list[FermionOperator]:
    """UCCGD-style generators: singles plus **generalized** doubles (all i≠j, a≠b)."""
    occ = list(range(n_electrons))
    virt = list(range(n_electrons, n_spin_orbitals))
    ops: list[FermionOperator] = []
    for i in occ:
        for a in virt:
            ops.append(FermionOperator(((a, 1), (i, 0)), 1.0))
    for i in occ:
        for j in occ:
            if i == j:
                continue
            for a in virt:
                for b in virt:
                    if a == b:
                        continue
                    ops.append(FermionOperator(((b, 1), (a, 1), (j, 0), (i, 0)), 1.0))
    pol = policy or IdentityRegrouping()
    return pol.regroup_generators(ops)


__all__ = [
    "ChemicallyAwareUCCPolicy",
    "GreedyCommutingFermionicLayers",
    "IdentityRegrouping",
    "SinglesBeforeDoublesLexicographic",
    "build_spin_ucc_doubles_only_fermion_generators",
    "build_spin_ucc_singles_only_fermion_generators",
    "build_spin_uccgd_fermion_generators",
    "build_spin_uccsd_fermion_generators",
    "count_uccsd_excitations",
]
