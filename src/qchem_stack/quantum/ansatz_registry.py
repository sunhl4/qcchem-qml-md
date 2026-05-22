"""Stable chemistry-facing ansatz identifiers (workflow UX / plugin hooks).

Open-stack counterpart to broad ansatz menus in research packages (e.g. Tangelo-style toolboxes):
execution still lives under ``quantum.algorithms.*``; this module is the **name → docs** registry only.

Outer-loop / YAML ``quantum.algorithm`` identifiers live in ``quantum.algorithm_registry``.
Fermion→qubit mapping names live in ``chem.fermion_mapping_registry``.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Final

from qchem_stack.quantum.algorithms.uccsd_vqe import UCCSDVQE, UCCSDTrotterVQE
from qchem_stack.quantum.algorithms.vqe import VQE

if TYPE_CHECKING:
    from qchem_stack.chem.hamiltonian import QubitHamiltonian

AnsatzFactory = Callable[..., Any]


@dataclass(frozen=True)
class AnsatzRegistryEntry:
    summary: str
    implementation: str
    factory: AnsatzFactory
    capabilities: dict[str, bool] = field(default_factory=dict)


def _hea_factory(hamiltonian: QubitHamiltonian, **kwargs: Any) -> VQE:
    return VQE(hamiltonian, **kwargs)


def _uccsd_factory(hamiltonian: QubitHamiltonian, **kwargs: Any) -> UCCSDVQE:
    return UCCSDVQE(hamiltonian, **kwargs)


def _uccsd_trotter_factory(hamiltonian: QubitHamiltonian, **kwargs: Any) -> UCCSDTrotterVQE:
    return UCCSDTrotterVQE(hamiltonian, **kwargs)


def _adapt_factory(hamiltonian: QubitHamiltonian, **kwargs: Any) -> Any:
    from qchem_stack.quantum.algorithms.adapt import FermionicAdaptVQE

    return FermionicAdaptVQE(hamiltonian, **kwargs)


def _iqeb_factory(hamiltonian: QubitHamiltonian, **kwargs: Any) -> Any:
    from qchem_stack.quantum.algorithms.iqeb import IQEBVQE

    return IQEBVQE(hamiltonian, **kwargs)


ANSATZ_REGISTRY: Final[dict[str, AnsatzRegistryEntry]] = {
    "hea": AnsatzRegistryEntry(
        summary="Hardware-efficient layered rotations; depth from ``quantum.vqe.depth``.",
        implementation="qchem_stack.quantum.algorithms.vqe.VQE",
        factory=_hea_factory,
        capabilities={"supports_gradient": True, "supports_auxiliary": True},
    ),
    "uccsd": AnsatzRegistryEntry(
        summary=(
            "Closed-shell spin-orbital UCCSD as sequential matrix exponentials on the JW Hartree–Fock "
            "reference (``quantum.variational.ansatz: uccsd`` with ``algorithm: vqe``; JW-only)."
        ),
        implementation="qchem_stack.quantum.algorithms.uccsd_vqe.UCCSDVQE",
        factory=_uccsd_factory,
        capabilities={"jordan_wigner_only": True},
    ),
    "fermionic_adapt": AnsatzRegistryEntry(
        summary="Fermionic-pool ADAPT-VQE.",
        implementation="qchem_stack.quantum.algorithms.adapt.FermionicAdaptVQE",
        factory=_adapt_factory,
        capabilities={"supports_pool_growth": True},
    ),
    "iqeb": AnsatzRegistryEntry(
        summary="IQEB outer loop with inner VQE.",
        implementation="qchem_stack.quantum.algorithms.iqeb.IQEBVQE",
        factory=_iqeb_factory,
        capabilities={"supports_outer_rounds": True},
    ),
    "uccsd_closed_shell_reference": AnsatzRegistryEntry(
        summary=(
            "Closed-shell spin-orbital UCCSD **excitation-count / bookkeeping** surface "
            "(``parity_integrations.uccsd_excitation_reference`` in ``parity_snapshot``); "
            "main-line variational ansatz remains HEA unless you swap algorithms."
        ),
        implementation=(
            "integrations/gap_closure_bundle + parity_snapshot ucc rows; "
            "qchem_stack.quantum.algorithms.vqe.VQE for demo energies"
        ),
        factory=_hea_factory,
    ),
    "trotter_ucc_placeholder": AnsatzRegistryEntry(
        summary=(
            "Alias for **first-order Trotter-layer UCCSD** wiring: set ``quantum.variational.ansatz: uccsd`` "
            "and ``quantum.variational.uccsd_trotter_steps`` (JW-only). Example: ``configs/example_h2_uccsd_trotter.yaml``."
        ),
        implementation="qchem_stack.quantum.algorithms.uccsd_vqe.UCCSDTrotterVQE",
        factory=_uccsd_trotter_factory,
        capabilities={"jordan_wigner_only": True},
    ),
    "adapt_solver_tangelo_alias": AnsatzRegistryEntry(
        summary=(
            "Naming parity anchor vs broad solver menus (e.g. Tangelo ``ADAPTSolver`` tutorials): "
            "still resolves to fermionic-pool ADAPT-VQE in this stack."
        ),
        implementation="qchem_stack.quantum.algorithms.adapt.FermionicAdaptVQE",
        factory=_adapt_factory,
    ),
    "ucc1_tangelo_partial": AnsatzRegistryEntry(
        summary="Partial alias: documented Tangelo UCC1 naming; execution redirects to HEA depth tuning.",
        implementation="qchem_stack.quantum.algorithms.vqe.VQE",
        factory=_hea_factory,
        capabilities={"partial_tangelo_alias": True},
    ),
    "qcc_tangelo_partial": AnsatzRegistryEntry(
        summary="Partial alias: QCC naming parity; execution uses HEA until dedicated QCC ansatz lands.",
        implementation="qchem_stack.quantum.algorithms.vqe.VQE",
        factory=_hea_factory,
        capabilities={"partial_tangelo_alias": True},
    ),
    "vsqs_tangelo_partial": AnsatzRegistryEntry(
        summary="Partial alias: VSQS naming parity; execution uses HEA layers.",
        implementation="qchem_stack.quantum.algorithms.vqe.VQE",
        factory=_hea_factory,
        capabilities={"partial_tangelo_alias": True},
    ),
}


def list_registered_ansatz_ids() -> tuple[str, ...]:
    """Sorted tuple of registry keys (deterministic for export / tests)."""
    return tuple(sorted(ANSATZ_REGISTRY.keys()))


def ansatz_registry_export() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for key, entry in ANSATZ_REGISTRY.items():
        out[key] = {
            "summary": entry.summary,
            "implementation": entry.implementation,
            "capabilities": dict(entry.capabilities),
        }
    return out
