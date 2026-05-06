"""Stable chemistry-facing ansatz identifiers (workflow UX / plugin hooks).

Open-stack counterpart to broad ansatz menus in research packages (e.g. Tangelo-style toolboxes):
execution still lives under ``quantum.algorithms.*``; this module is the **name → docs** registry only.

Outer-loop / YAML ``quantum.algorithm`` identifiers live in ``quantum.algorithm_registry``.
Fermion→qubit mapping names live in ``chem.fermion_mapping_registry``.
"""

from __future__ import annotations

from typing import Final

ANSATZ_REGISTRY: Final[dict[str, dict[str, str]]] = {
    "hea": {
        "summary": "Hardware-efficient layered rotations; depth from ``quantum.vqe_depth``.",
        "implementation": "qchem_stack.quantum.algorithms.vqe.VQE",
    },
    "uccsd": {
        "summary": (
            "Closed-shell spin-orbital UCCSD as sequential matrix exponentials on the JW Hartree–Fock "
            "reference (``quantum.variational_ansatz: uccsd`` with ``algorithm: vqe``; JW-only)."
        ),
        "implementation": "qchem_stack.quantum.algorithms.uccsd_vqe.UCCSDVQE",
    },
    "fermionic_adapt": {
        "summary": "Fermionic-pool ADAPT-VQE.",
        "implementation": "qchem_stack.quantum.algorithms.adapt.FermionicAdaptVQE",
    },
    "iqeb": {
        "summary": "IQEB outer loop with inner VQE.",
        "implementation": "qchem_stack.quantum.algorithms.iqeb.IQEBVQE",
    },
    "uccsd_closed_shell_reference": {
        "summary": (
            "Closed-shell spin-orbital UCCSD **excitation-count / bookkeeping** surface "
            "(``parity_integrations.uccsd_excitation_reference`` in ``parity_snapshot``); "
            "main-line variational ansatz remains HEA unless you swap algorithms."
        ),
        "implementation": (
            "integrations/gap_closure_bundle + parity_snapshot ucc rows; "
            "qchem_stack.quantum.algorithms.vqe.VQE for demo energies"
        ),
    },
    "trotter_ucc_placeholder": {
        "summary": (
            "Alias for **first-order Trotter-layer UCCSD** wiring: set ``quantum.variational_ansatz: uccsd`` "
            "and ``quantum.uccsd_trotter_steps`` (JW-only). Example: ``configs/example_h2_uccsd_trotter.yaml``."
        ),
        "implementation": "qchem_stack.quantum.algorithms.uccsd_vqe.UCCSDTrotterVQE",
    },
}


def list_registered_ansatz_ids() -> tuple[str, ...]:
    """Sorted tuple of registry keys (deterministic for export / tests)."""
    return tuple(sorted(ANSATZ_REGISTRY.keys()))
