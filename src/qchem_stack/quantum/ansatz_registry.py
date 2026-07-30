"""Stable chemistry-facing ansatz identifiers (workflow UX / plugin hooks).

Execution lives under ``quantum.algorithms.*``; this module is the **name → docs** registry only.

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


def _uccgd_factory(hamiltonian: QubitHamiltonian, **kwargs: Any) -> Any:
    from qchem_stack.quantum.algorithms.uccgd_vqe import UCCGDVQE

    return UCCGDVQE(hamiltonian, **kwargs)


def _qcc_factory(hamiltonian: QubitHamiltonian, **kwargs: Any) -> Any:
    from qchem_stack.quantum.algorithms.qcc_vqe import QCCVQE

    return QCCVQE(hamiltonian, **kwargs)


def _puccd_factory(hamiltonian: QubitHamiltonian, **kwargs: Any) -> Any:
    from qchem_stack.quantum.algorithms.puccd_vqe import PUCCDVQE

    return PUCCDVQE(hamiltonian, **kwargs)


def _upccgsd_factory(hamiltonian: QubitHamiltonian, **kwargs: Any) -> Any:
    from qchem_stack.quantum.algorithms.upccgsd_vqe import UpCCGSDVQE

    return UpCCGSDVQE(hamiltonian, **kwargs)


def _iqcc_factory(hamiltonian: QubitHamiltonian, **kwargs: Any) -> Any:
    from qchem_stack.quantum.algorithms.iqcc import IQCCVQE

    return IQCCVQE(hamiltonian, **kwargs)


def _qite_factory(hamiltonian: QubitHamiltonian, **kwargs: Any) -> Any:
    from qchem_stack.quantum.algorithms.qite import QITEVQE

    return QITEVQE(hamiltonian, **kwargs)


def _vsqs_factory(hamiltonian: QubitHamiltonian, **kwargs: Any) -> Any:
    from qchem_stack.quantum.algorithms.vsqs_vqe import VSQSVQE

    return VSQSVQE(hamiltonian, **kwargs)


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
    "uccgd": AnsatzRegistryEntry(
        summary="UCC with generalized doubles (JW/BK square encodings).",
        implementation="qchem_stack.quantum.algorithms.uccgd_vqe.UCCGDVQE",
        factory=_uccgd_factory,
        capabilities={"jordan_wigner_only": True, "generalized_doubles": True},
    ),
    "qcc": AnsatzRegistryEntry(
        summary="Quantum Coupled Cluster via fixed qubit-excitation pool exponentials.",
        implementation="qchem_stack.quantum.algorithms.qcc_vqe.QCCVQE",
        factory=_qcc_factory,
        capabilities={"qubit_excitation_pool": True},
    ),
    "upccgsd": AnsatzRegistryEntry(
        summary="Unitary pair coupled-cluster GSD (singles + paired doubles, JW/BK square).",
        implementation="qchem_stack.quantum.algorithms.upccgsd_vqe.UpCCGSDVQE",
        factory=_upccgsd_factory,
        capabilities={"jordan_wigner_only": True, "paired_doubles": True},
    ),
    "puccd": AnsatzRegistryEntry(
        summary="Pair UCCD — paired doubles only on closed-shell references.",
        implementation="qchem_stack.quantum.algorithms.puccd_vqe.PUCCDVQE",
        factory=_puccd_factory,
        capabilities={"jordan_wigner_only": True, "doubles_only": True},
    ),
    "iqcc": AnsatzRegistryEntry(
        summary=(
            "Legacy UX alias for iterative QCC; prefer ``quantum.algorithm: iqcc`` "
            "+ ``quantum.iqcc.*`` (same ``IQCCVQE`` runner)."
        ),
        implementation="qchem_stack.quantum.algorithms.iqcc.IQCCVQE",
        factory=_iqcc_factory,
        capabilities={
            "legacy_ansatz_alias": True,
            "supports_hamiltonian_dressing": True,
            "supports_en2_pt": True,
            "open_stack_implementation": True,
        },
    ),
    "qite": AnsatzRegistryEntry(
        summary="Quantum imaginary-time evolution research plugin (fixed pool).",
        implementation="qchem_stack.quantum.algorithms.qite.QITEVQE",
        factory=_qite_factory,
        capabilities={"research_plugin": True},
    ),
    "vsqs": AnsatzRegistryEntry(
        summary="Variational Scheduled Quantum Simulation (arXiv:2003.09913).",
        implementation="qchem_stack.quantum.algorithms.vsqs_vqe.VSQSVQE",
        factory=_vsqs_factory,
        capabilities={"requires_hf_reference": True, "requires_spatial_integrals_meta": True},
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
