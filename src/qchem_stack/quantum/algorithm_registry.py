"""Variational / outer-loop algorithm identifiers (YAML ``quantum.algorithm`` analog).

Execution remains in ``quantum.algorithms.*``; this registry is for export, UX, and conformance labels.
"""

from __future__ import annotations

from typing import Final

ALGORITHM_REGISTRY: Final[dict[str, dict[str, str]]] = {
    "vqe": {
        "summary": "Standard HEA / UCC-style VQE loop (see ``quantum.vqe_depth`` / ``vqe_maxiter``).",
        "implementation": "qchem_stack.quantum.algorithms.vqe.VQE",
    },
    "adapt": {
        "summary": "Fermionic-pool ADAPT-VQE (gradient-driven operator growth).",
        "implementation": "qchem_stack.quantum.algorithms.adapt.FermionicAdaptVQE",
    },
    "iqeb": {
        "summary": "IQEB outer Pauli-selection loop with inner VQE.",
        "implementation": "qchem_stack.quantum.algorithms.iqeb.IQEBVQE",
    },
}


def list_registered_algorithm_ids() -> tuple[str, ...]:
    return tuple(sorted(ALGORITHM_REGISTRY.keys()))
