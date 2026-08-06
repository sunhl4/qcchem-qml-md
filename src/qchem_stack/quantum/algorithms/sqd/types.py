"""Shared types for sample-based quantum chemistry algorithms (SQD family).

Algorithms follow IBM sampling paradigm from
``docs/基于采样的量子化学计算报告.pdf``: QPU as configuration sampler,
classical subspace diagonalization for energies.

Product note: dense statevector prototypes only (see ``MAX_SQD_QUBITS`` and
customer vs experimental algorithm tiers).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np

# Hard product limit for dense 2**n statevector / matrix paths.
MAX_SQD_QUBITS: int = 12

SqdAlgorithmId = Literal[
    "cbs",
    "qsci",
    "sqd",
    "qse_qsci_lite",
    "adapt_qsci",
    "skqd",
    "sqdrift",
    "hi_vqe_lite",
    "ewf_trim_sqd_lite",
    "qbe_sqd_lite",
    "sqd_afqmc_lite",
]

# Customer-facing allowlist (dense prototypes with documented caveats).
CUSTOMER_SQD_ALGORITHM_IDS: frozenset[str] = frozenset(
    {
        "cbs",
        "qsci",
        "sqd",
        "skqd",
        "sqdrift",
    }
)

# Opt-in research / lite demos: require ``quantum.sqd.allow_experimental: true``.
EXPERIMENTAL_SQD_ALGORITHM_IDS: frozenset[str] = frozenset(
    {
        "qse_qsci_lite",
        "adapt_qsci",
        "hi_vqe_lite",
        "ewf_trim_sqd_lite",
        "qbe_sqd_lite",
        "sqd_afqmc_lite",
    }
)

ALL_SQD_ALGORITHM_IDS: frozenset[str] = CUSTOMER_SQD_ALGORITHM_IDS | EXPERIMENTAL_SQD_ALGORITHM_IDS


def sqd_customer_tier(algorithm_id: str) -> str:
    if algorithm_id in CUSTOMER_SQD_ALGORITHM_IDS:
        return "customer"
    if algorithm_id in EXPERIMENTAL_SQD_ALGORITHM_IDS:
        return "experimental"
    return "unknown"


@dataclass
class SqdConfig:
    """Runtime knobs shared by SQD-family algorithms (YAML: ``quantum.sqd``)."""

    n_shots: int = 512
    subspace_size: int = 16
    max_iters: int = 5
    hea_depth: int = 1
    n_electrons: int | None = None
    seed: int = 0
    krylov_dim: int = 4
    krylov_dt: float = 0.3
    qdrift_steps: int = 8
    qdrift_replicas: int = 4
    recovery_iters: int = 3
    n_fragments: int = 2
    afqmc_walkers: int = 32
    afqmc_steps: int = 20
    energy_tol: float = 1.0e-5
    carryover: int = 4


@dataclass
class SqdResult:
    energy: float
    angles: np.ndarray
    nfev: int
    selected_bitstrings: list[int] = field(default_factory=list)
    ci_coefficients: list[complex] = field(default_factory=list)
    energy_trace: list[float] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)
