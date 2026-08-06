"""Generative Quantum Eigensolver family (peer algorithms to VQE).

Implements Nakaji GPT-QE plus Yaozheng GQE-review extensions A1–A8:

* ``gqe`` / GPT-QE — Logit Matching / GRPO
* ``conditional_gqe`` — A1 conditioned generation + DPO
* ``pdpo_gqe`` — A2 Persistent-DPO + QCC budget mask
* ``smiles_gqe`` — A3 SMILES-style operator text vocabulary
* ``gqe_qsci`` — A4 QSCI subspace-energy reward
* ``auger_gqe`` — A5 spectral / Auger-style oracle
* ``gqkae`` — A6 KAN backbone + QSCI reward
* ``spin_gqe`` — A7 spin pool + WMSE
* ``adapt_gqe`` — A8 ADAPT teacher warm-start + GRPO
"""

from __future__ import annotations

from qchem_stack.quantum.algorithms.gqe.core import (
    ALGORITHM_GQE_REPORT_V1,
    VARIANT_TO_CLASS,
    AdaptGQE,
    AugerGQE,
    ConditionalGQE,
    GQE,
    GQKAE,
    PersistentDPOGQE,
    QSCIGQE,
    SmilesTransferGQE,
    SpinGQE,
    gqe_algorithm_report_v1,
)
from qchem_stack.quantum.algorithms.gqe.types import GQEConfig, GQEResult, PoolToken

__all__ = [
    "ALGORITHM_GQE_REPORT_V1",
    "VARIANT_TO_CLASS",
    "AdaptGQE",
    "AugerGQE",
    "ConditionalGQE",
    "GQE",
    "GQKAE",
    "GQEConfig",
    "GQEResult",
    "PersistentDPOGQE",
    "PoolToken",
    "QSCIGQE",
    "SmilesTransferGQE",
    "SpinGQE",
    "gqe_algorithm_report_v1",
]
