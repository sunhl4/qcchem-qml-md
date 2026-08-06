"""Shared types for the Generative Quantum Eigensolver (GQE) family.

Peer algorithms to VQE (Nakaji 2024 GPT-QE + A1–A8 extensions from the Yaozheng
GQE literature review). Trainable parameters live in a classical generative
policy; the quantum device is an energy / subspace-energy oracle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np

GQEVariant = Literal[
    "gpt_qe",
    "conditional",
    "pdpo_qcc",
    "smiles",
    "qsci",
    "auger",
    "gqkae",
    "spin",
    "adapt_gqe",
]

GQELossName = Literal["lm", "grpo", "dpo", "pdpo", "wmse"]

GQEPoolMode = Literal[
    "hamiltonian_pauli",
    "uccsd",
    "spin_heisenberg",
    "simple",
]


@dataclass(frozen=True)
class PoolToken:
    """One vocabulary entry: optional Pauli string + discrete evolution time."""

    index: int
    pauli_string: str | None
    time: float
    label: str
    is_identity: bool = False
    qcc_cost: float = 0.0
    smiles_text: str = ""


@dataclass
class GQEConfig:
    """Runtime knobs shared by all GQE variants (YAML: ``quantum.gqe``)."""

    n_gates: int = 8
    max_iters: int = 25
    batch_size: int = 8
    buffer_size: int = 64
    learning_rate: float = 5.0e-3
    beta: float = 5.0
    beta_min: float = 0.5
    beta_max: float = 20.0
    energy_std_floor: float = 1.0e-5
    loss: GQELossName = "grpo"
    grpo_clip: float = 0.2
    pdpo_alpha: float = 0.1
    dpo_beta: float = 0.1
    pool_mode: GQEPoolMode = "hamiltonian_pauli"
    time_scale: float = 320.0
    time_exponents: tuple[int, ...] = (0, 1, 2, 3)
    embed_dim: int = 16
    qcc_budget: float | None = None
    qsci_subspace_size: int = 8
    condition_dim: int = 0
    energy_offset: float = 0.0
    variant: GQEVariant = "gpt_qe"
    backbone: Literal["linear", "kan"] = "linear"
    seed: int = 0


@dataclass
class GQEResult:
    energy: float
    best_sequence: list[int]
    best_labels: list[str]
    n_oracle_calls: int
    energy_trace: list[float] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)
    # Pipeline compatibility: variational stage expects an angle vector.
    angles: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype=float))
    nfev: int = 0
