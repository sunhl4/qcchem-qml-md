from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

import numpy as np
from openfermion.measurements import group_into_tensor_product_basis_sets

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator


def _term_to_xz(term: tuple[tuple[int, str], ...], n_qubits: int) -> tuple[np.ndarray, np.ndarray]:
    """Binary symplectic pair ``(x, z)`` per qubit: X→(1,0), Z→(0,1), Y→(1,1), I→(0,0)."""
    x = np.zeros(n_qubits, dtype=np.uint8)
    z = np.zeros(n_qubits, dtype=np.uint8)
    for i, p in term:
        if p == "X":
            x[i] = 1
        elif p == "Z":
            z[i] = 1
        elif p == "Y":
            x[i] = 1
            z[i] = 1
        elif p != "I":
            raise ValueError(f"Unknown Pauli {p!r}")
    return x, z


def _symplectic_inner(
    xz1: tuple[np.ndarray, np.ndarray], xz2: tuple[np.ndarray, np.ndarray]
) -> int:
    x1, z1 = xz1
    x2, z2 = xz2
    return int(
        (np.dot(x1.astype(int), z2.astype(int)) + np.dot(z1.astype(int), x2.astype(int))) % 2
    )


def pauli_terms_commute(term_a: tuple, term_b: tuple, n_qubits: int) -> bool:
    if term_a == term_b:
        return True
    xa, za = _term_to_xz(term_a, n_qubits)
    xb, zb = _term_to_xz(term_b, n_qubits)
    return _symplectic_inner((xa, za), (xb, zb)) == 0


def greedy_commuting_groups(terms: list[tuple], n_qubits: int) -> list[list[tuple]]:
    """Partition Pauli terms into mutually commuting subsets (pairwise within each subset)."""
    if not terms:
        return []
    xz_cache = {t: _term_to_xz(t, n_qubits) for t in terms}
    groups: list[list[tuple]] = []
    for term in terms:
        xz_t = xz_cache[term]
        placed = False
        for g in groups:
            if all(_symplectic_inner(xz_t, xz_cache[u]) == 0 for u in g):
                g.append(term)
                placed = True
                break
        if not placed:
            groups.append([term])
    return groups


def terms_from_qubit_operator(h: QubitOperator) -> list[tuple]:
    out: list[tuple] = []
    for term in h.terms:
        if len(term) == 0:
            continue
        out.append(term)
    return out


@dataclass
class PauliMeasurementPlan:
    """Grouped Pauli strings: one shot budget / circuit row per group (same measurement basis per group)."""

    n_qubits: int
    groups: list[list[tuple]] = field(default_factory=list)
    """Each group lists OpenFermion-style Pauli terms (non-identity)."""
    basis_keys: list[tuple[tuple[int, str], ...] | None] = field(default_factory=list)
    """Per group, tensor-product measurement basis (OpenFermion key); ``None`` if unknown / not synthesizable."""
    grouping_method: Literal["tensor_product", "greedy_commuting"] = "tensor_product"
    identity_coeff: complex = 0j

    @property
    def n_circuits(self) -> int:
        return max(1, len(self.groups))

    def to_circuit_metas(self) -> list[dict[str, Any]]:
        """Metadata for :class:`CircuitIR` / resource tables (not full gate synthesis)."""
        from qchem_stack.backends.pauli_measure_expand import serialize_basis_key

        metas: list[dict[str, Any]] = []
        if not self.groups:
            return [
                {"group_id": 0, "terms": [], "n_terms": 0, "support_qubits": [], "basis_key": None}
            ]
        for gid, g in enumerate(self.groups):
            qubits = sorted({i for t in g for i, _ in t})
            bk = self.basis_keys[gid] if gid < len(self.basis_keys) else None
            metas.append(
                {
                    "group_id": gid,
                    "terms": [str(t) for t in g],
                    "n_terms": len(g),
                    "support_qubits": qubits,
                    "basis_key": serialize_basis_key(bk),
                    "synthesized": bk is not None,
                }
            )
        return metas


def build_measurement_plan(
    h: QubitOperator,
    n_qubits: int,
    grouping: Literal["tensor_product", "greedy_commuting"] = "tensor_product",
) -> PauliMeasurementPlan:
    id_coeff = complex(h.terms.get((), 0.0))
    if grouping == "greedy_commuting":
        terms = terms_from_qubit_operator(h)
        groups = greedy_commuting_groups(terms, n_qubits) if terms else []
        basis_keys: list[tuple[tuple[int, str], ...] | None] = [None] * len(groups)
        return PauliMeasurementPlan(
            n_qubits=n_qubits,
            groups=groups,
            basis_keys=basis_keys,
            grouping_method=grouping,
            identity_coeff=id_coeff,
        )

    subops = group_into_tensor_product_basis_sets(h)
    tp_groups: list[list[tuple]] = []
    basis_keys = []
    for basis_key, sub in subops.items():
        ts = [t for t in sub.terms if len(t) > 0]
        if not ts:
            continue
        if basis_key == () or not basis_key:
            continue
        tp_groups.append(ts)
        basis_keys.append(tuple((int(i), str(p)) for i, p in basis_key))

    return PauliMeasurementPlan(
        n_qubits=n_qubits,
        groups=tp_groups,
        basis_keys=basis_keys,
        grouping_method="tensor_product",
        identity_coeff=id_coeff,
    )
