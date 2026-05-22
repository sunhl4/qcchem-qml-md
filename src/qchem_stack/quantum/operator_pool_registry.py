"""Executable operator-pool registry for ADAPT/IQEB style algorithms."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Final

from openfermion import bravyi_kitaev, jordan_wigner
from openfermion.ops import QubitOperator

from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.chem.kernels.spin_ucc import (
    build_spin_ucc_doubles_only_fermion_generators,
    build_spin_ucc_singles_only_fermion_generators,
    build_spin_uccsd_fermion_generators,
)
from qchem_stack.contracts.schema_ids import OPERATOR_POOL_REGISTRY_EXPORT_V1

OperatorPoolFactory = Callable[[QubitHamiltonian], list[QubitOperator]]


@dataclass(frozen=True)
class OperatorPoolRegistryEntry:
    summary: str
    factory: OperatorPoolFactory
    capabilities: dict[str, bool] = field(default_factory=dict)


def _toy_pair_xx_pool(hamiltonian: QubitHamiltonian) -> list[QubitOperator]:
    n = int(hamiltonian.n_qubits)
    out: list[QubitOperator] = []
    for i in range(n):
        for j in range(i + 1, n):
            out.append(QubitOperator(((i, "X"), (j, "X")), 1.0))
    return out


def _fermionic_uccsd_pool(hamiltonian: QubitHamiltonian) -> list[QubitOperator]:
    fs = hamiltonian.fermion_space
    if fs is None:
        return _toy_pair_xx_pool(hamiltonian)
    ferm_ops = build_spin_uccsd_fermion_generators(int(fs.n_spin_orbitals), int(fs.n_electrons))
    out: list[QubitOperator] = []
    for op in ferm_ops:
        qop = jordan_wigner(op)
        if not isinstance(qop, QubitOperator):
            continue
        out.append(qop)
    return out or _toy_pair_xx_pool(hamiltonian)


def _fermionic_uccsd_doubles_pool(hamiltonian: QubitHamiltonian) -> list[QubitOperator]:
    fs = hamiltonian.fermion_space
    if fs is None:
        return _toy_pair_xx_pool(hamiltonian)
    ferm_ops = build_spin_ucc_doubles_only_fermion_generators(
        int(fs.n_spin_orbitals), int(fs.n_electrons)
    )
    out: list[QubitOperator] = []
    for op in ferm_ops:
        qop = jordan_wigner(op)
        if not isinstance(qop, QubitOperator):
            continue
        out.append(qop)
    return out or _toy_pair_xx_pool(hamiltonian)


def _fermionic_uccsd_singles_pool(hamiltonian: QubitHamiltonian) -> list[QubitOperator]:
    fs = hamiltonian.fermion_space
    if fs is None:
        return _toy_pair_xx_pool(hamiltonian)
    ferm_ops = build_spin_ucc_singles_only_fermion_generators(
        int(fs.n_spin_orbitals), int(fs.n_electrons)
    )
    out: list[QubitOperator] = []
    for op in ferm_ops:
        qop = jordan_wigner(op)
        if not isinstance(qop, QubitOperator):
            continue
        out.append(qop)
    return out or _toy_pair_xx_pool(hamiltonian)


def _iqeb_qubit_excitation_pool(hamiltonian: QubitHamiltonian) -> list[QubitOperator]:
    n = int(hamiltonian.n_qubits)
    out: list[QubitOperator] = []
    for i in range(n):
        for j in range(i + 1, n):
            # Anti-hermitian one-body qubit excitation analog.
            out.append(
                0.5j * QubitOperator(((i, "X"), (j, "Y")), 1.0)
                - 0.5j * QubitOperator(((i, "Y"), (j, "X")), 1.0)
            )
    return out or _toy_pair_xx_pool(hamiltonian)


def _fermionic_uccsd_bravyi_kitaev_pool(hamiltonian: QubitHamiltonian) -> list[QubitOperator]:
    fs = hamiltonian.fermion_space
    if fs is None:
        return _toy_pair_xx_pool(hamiltonian)
    ferm_ops = build_spin_uccsd_fermion_generators(int(fs.n_spin_orbitals), int(fs.n_electrons))
    out: list[QubitOperator] = []
    for fer in ferm_ops:
        qop = bravyi_kitaev(fer)
        if not isinstance(qop, QubitOperator):
            continue
        out.append(qop)
    return out or _toy_pair_xx_pool(hamiltonian)


def _fermionic_uccsd_singles_bravyi_kitaev_pool(
    hamiltonian: QubitHamiltonian,
) -> list[QubitOperator]:
    fs = hamiltonian.fermion_space
    if fs is None:
        return _toy_pair_xx_pool(hamiltonian)
    ferm_ops = build_spin_ucc_singles_only_fermion_generators(
        int(fs.n_spin_orbitals), int(fs.n_electrons)
    )
    out: list[QubitOperator] = []
    for fer in ferm_ops:
        qop = bravyi_kitaev(fer)
        if not isinstance(qop, QubitOperator):
            continue
        out.append(qop)
    return out or _toy_pair_xx_pool(hamiltonian)


def _fermionic_uccsd_doubles_bravyi_kitaev_pool(
    hamiltonian: QubitHamiltonian,
) -> list[QubitOperator]:
    fs = hamiltonian.fermion_space
    if fs is None:
        return _toy_pair_xx_pool(hamiltonian)
    ferm_ops = build_spin_ucc_doubles_only_fermion_generators(
        int(fs.n_spin_orbitals), int(fs.n_electrons)
    )
    out: list[QubitOperator] = []
    for fer in ferm_ops:
        qop = bravyi_kitaev(fer)
        if not isinstance(qop, QubitOperator):
            continue
        out.append(qop)
    return out or _toy_pair_xx_pool(hamiltonian)


def _combined_bk_single_double_slices(hamiltonian: QubitHamiltonian) -> list[QubitOperator]:
    s = _fermionic_uccsd_singles_bravyi_kitaev_pool(hamiltonian)
    d = _fermionic_uccsd_doubles_bravyi_kitaev_pool(hamiltonian)
    out = [*s, *d]
    return out or _toy_pair_xx_pool(hamiltonian)


OPERATOR_POOL_ID_ALIASES: Final[dict[str, str]] = {
    "qubit_excitation": "iqeb_qubit_excitation",
    "uccsd_jw": "fermionic_uccsd",
    "uccsd_singles": "fermionic_uccsd_singles",
    "uccsd_doubles_only": "fermionic_uccsd_doubles_only",
    "uccsd_bravyi_kitaev": "fermionic_uccsd_bravyi_kitaev",
    "uccsd_bk": "fermionic_uccsd_bravyi_kitaev",
    "uccsd_bk_singles": "fermionic_uccsd_singles_bravyi_kitaev",
    "uccsd_bk_doubles_only": "fermionic_uccsd_doubles_bravyi_kitaev_only",
    "uccsd_bk_singles_then_doubles": "fermionic_uccsd_singles_then_doubles_bk_concat",
}


def resolve_operator_pool_id(pool_id: str) -> str:
    """Map alias ids (e.g. literature ``qubit_excitation``) to canonical registry keys."""
    return OPERATOR_POOL_ID_ALIASES.get(pool_id, pool_id)


OPERATOR_POOL_REGISTRY: Final[dict[str, OperatorPoolRegistryEntry]] = {
    "toy_pair_xx": OperatorPoolRegistryEntry(
        summary="Toy pool with pair XX generators.",
        factory=_toy_pair_xx_pool,
        capabilities={"smoke_only": True},
    ),
    "fermionic_uccsd": OperatorPoolRegistryEntry(
        summary="UCCSD fermionic generators mapped to qubit operators.",
        factory=_fermionic_uccsd_pool,
        capabilities={"chemistry_aware": True},
    ),
    "fermionic_uccsd_singles": OperatorPoolRegistryEntry(
        summary=(
            "JW-mapped spin-orbital singles only (UCCS-style subspace); doubles excluded. "
            "Smaller ADAPT/IQEB pool — not vendor full taxonomy."
        ),
        factory=_fermionic_uccsd_singles_pool,
        capabilities={"chemistry_aware": True, "singles_only": True},
    ),
    "fermionic_uccsd_doubles_only": OperatorPoolRegistryEntry(
        summary=(
            "JW-mapped paired doubles only (`ij→ab` fermionic generators); singles excluded. "
            "Use with singles pools in separate YAML experiments or future staged registry — "
            "not vendor full taxonomy."
        ),
        factory=_fermionic_uccsd_doubles_pool,
        capabilities={"chemistry_aware": True, "doubles_only": True},
    ),
    "iqeb_qubit_excitation": OperatorPoolRegistryEntry(
        summary="Qubit-excitation pool for IQEB-like outer selection loops.",
        factory=_iqeb_qubit_excitation_pool,
        capabilities={"iqeb_style": True},
    ),
    "fermionic_uccsd_bravyi_kitaev": OperatorPoolRegistryEntry(
        summary="BK-matched spin-UCCSD fermionic pool (OpenFermion bravyi_kitaev(map)).",
        factory=_fermionic_uccsd_bravyi_kitaev_pool,
        capabilities={"chemistry_aware": True, "bravyi_kitaev": True},
    ),
    "fermionic_uccsd_singles_bravyi_kitaev": OperatorPoolRegistryEntry(
        summary="BK-mapped fermionic singles only (UCCS-style chemistry slice).",
        factory=_fermionic_uccsd_singles_bravyi_kitaev_pool,
        capabilities={"chemistry_aware": True, "singles_only": True, "bravyi_kitaev": True},
    ),
    "fermionic_uccsd_doubles_bravyi_kitaev_only": OperatorPoolRegistryEntry(
        summary="BK-mapped paired doubles fermionic generators only.",
        factory=_fermionic_uccsd_doubles_bravyi_kitaev_pool,
        capabilities={"chemistry_aware": True, "doubles_only": True, "bravyi_kitaev": True},
    ),
    "fermionic_uccsd_singles_then_doubles_bk_concat": OperatorPoolRegistryEntry(
        summary="Flattened BK singles pool followed by BK doubles pool (explicit registry sequencing).",
        factory=_combined_bk_single_double_slices,
        capabilities={"chemistry_aware": True, "sequenced_slices": True, "bravyi_kitaev": True},
    ),
}


def list_registered_operator_pool_ids() -> tuple[str, ...]:
    return tuple(sorted(set(OPERATOR_POOL_REGISTRY) | set(OPERATOR_POOL_ID_ALIASES)))


def is_registered_operator_pool_id(pool_id: str) -> bool:
    """Return True when ``pool_id`` (or a known alias) maps to a registry entry."""
    canonical = resolve_operator_pool_id(str(pool_id).strip())
    return canonical in OPERATOR_POOL_REGISTRY


def build_registered_operator_pool(
    pool_id: str, hamiltonian: QubitHamiltonian
) -> list[QubitOperator]:
    requested = pool_id
    pool_id = resolve_operator_pool_id(pool_id)
    try:
        entry = OPERATOR_POOL_REGISTRY[pool_id]
    except KeyError as exc:
        raise ValueError(f"Unknown operator pool id: {requested!r}") from exc
    return entry.factory(hamiltonian)


def operator_pool_registry_export_v1() -> dict[str, Any]:
    """Machine-readable pool metadata for parity / Methods export (W5-aligned)."""

    pools: dict[str, Any] = {}
    for pid, entry in sorted(OPERATOR_POOL_REGISTRY.items()):
        pools[pid] = {"summary": entry.summary, "capabilities": dict(entry.capabilities)}
    return {
        "schema": OPERATOR_POOL_REGISTRY_EXPORT_V1,
        "registered_ids": sorted(set(OPERATOR_POOL_REGISTRY) | set(OPERATOR_POOL_ID_ALIASES)),
        "canonical_operator_pool_ids": sorted(OPERATOR_POOL_REGISTRY.keys()),
        "pool_id_aliases": dict(sorted(OPERATOR_POOL_ID_ALIASES.items())),
        "pools": pools,
        "adapt_pool_yaml_field": "quantum.adapt.pool_id",
        "iqeb_pool_yaml_field": "quantum.iqeb.pool_id",
        "export_alignment_note": (
            "Open pools are JW (default slices) plus explicit **BK** spin-UCCSD pools "
            "(`fermionic_uccsd_bravyi_kitaev`, singles/doubles slices, concatenated id). "
            "Aliases (`uccsd_jw`, `uccsd_singles`, `uccsd_doubles_only`, "
            "`uccsd_bravyi_kitaev`, `uccsd_bk`, `uccsd_bk_singles`, "
            "`uccsd_bk_doubles_only`, `uccsd_bk_singles_then_doubles`, `qubit_excitation`). "
            "Not vendor excitation-taxonomy parity."
        ),
    }
