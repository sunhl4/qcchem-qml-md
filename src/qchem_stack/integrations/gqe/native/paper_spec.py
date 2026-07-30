"""Nakaji et al. GPT-QE (arXiv:2401.09253) reproduction constants & molecule specs.

Source of truth: paper §§3, Appendices A–C (not the encrypted local 精读 notes).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

CHEMICAL_ACCURACY_HARTREE = 1.6e-3

# Appendix A.2 — time grid T = {±2^k / 320}_{k=0}^{5}
PAPER_TIME_GRID: tuple[float, ...] = tuple(
    [2**k / 320.0 for k in range(0, 6)] + [-(2**k) / 320.0 for k in range(0, 6)]
)

# Appendix A.3 — dispersion-triggered β
PAPER_BETA_ALPHA = 0.02
PAPER_BETA_TAU_DISP = 1e-5
PAPER_BETA_INIT = 1.0

# §3.1 training defaults
PAPER_BUFFER_MAX = 1000
PAPER_BATCH_SIZE = 50
PAPER_N_SAMPLE = 50
PAPER_N_ITER = 5
PAPER_WARMUP_SAMPLES = 200
PAPER_GRPO_CLIP_EPS = 0.2
PAPER_N_TRIALS = 3

# Transformer (§3): GPT-2 style, 6 layers / 6 heads — we use d_model divisible by n_heads
PAPER_N_LAYERS = 6
PAPER_N_HEADS = 6
PAPER_D_MODEL = 192  # 32 per head


MoleculeId = Literal["h2", "lih", "beh2", "n2"]


@dataclass(frozen=True)
class PaperMoleculeSpec:
    """Active-space / training knobs matching paper Fig. 4–5 captions."""

    molecule_id: MoleculeId
    symbols: tuple[str, ...]
    # Second atom (or N–N / Be–H pattern) bond length handled by runner
    n_qubits: int
    n_electrons_cas: int
    n_orbitals_cas: int
    seq_len: int
    n_epochs: int
    # Geometry atom layout helper: "diatomic" | "beh2_linear"
    geometry_kind: str
    # Optional energy offset for LM numerical stability (Appendix B.1; N2 uses 107)
    energy_offset: float = 0.0


PAPER_MOLECULES: dict[MoleculeId, PaperMoleculeSpec] = {
    "h2": PaperMoleculeSpec(
        molecule_id="h2",
        symbols=("H", "H"),
        n_qubits=4,
        n_electrons_cas=2,
        n_orbitals_cas=2,
        seq_len=10,
        n_epochs=200,
        geometry_kind="diatomic",
    ),
    "lih": PaperMoleculeSpec(
        molecule_id="lih",
        symbols=("Li", "H"),
        n_qubits=10,
        n_electrons_cas=2,
        n_orbitals_cas=5,
        seq_len=40,
        n_epochs=1000,
        geometry_kind="diatomic",
    ),
    "beh2": PaperMoleculeSpec(
        molecule_id="beh2",
        symbols=("Be", "H", "H"),
        n_qubits=12,
        n_electrons_cas=4,
        n_orbitals_cas=6,
        seq_len=60,
        n_epochs=1500,
        geometry_kind="beh2_linear",
    ),
    "n2": PaperMoleculeSpec(
        molecule_id="n2",
        symbols=("N", "N"),
        n_qubits=12,
        n_electrons_cas=6,
        n_orbitals_cas=6,
        seq_len=100,
        n_epochs=1500,
        geometry_kind="diatomic",
        energy_offset=107.0,
    ),
}


# Bond lengths (Å) used in paper figures — approximate scan grids
PAPER_BOND_LENGTHS_ANG: dict[MoleculeId, tuple[float, ...]] = {
    "h2": (0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.5, 2.0),
    "lih": (1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.5, 3.0),
    "beh2": (1.0, 1.2, 1.3, 1.4, 1.5, 1.7, 2.0, 2.5),
    "n2": (0.9, 1.0, 1.05, 1.1, 1.2, 1.3, 1.5, 1.75, 2.0),
}


def paper_reproduction_checklist() -> dict[str, object]:
    """Machine-readable gap list vs arXiv:2401.09253."""
    return {
        "paper": "arXiv:2401.09253",
        "title": "The generative quantum eigensolver (GQE) and its application for ground state search",
        "targets": {
            "A2_operator_pool": "UCCSD Pauli e^{i P t} + I, T=±2^k/320",
            "A3_beta": "dispersion-triggered β (α=0.02, τ=1e-5)",
            "B1_logit_matching": "L = mean (e^{-β w_sum} - e^{-β E})^2",
            "B2_grpo": "clipped importance ratio vs θ_old, ε=0.2",
            "C_reweight": "Pauli q_a transfer across geometries",
            "sec31_molecules": ["H2", "LiH", "BeH2", "N2"],
            "sec32_pretrain": "N2 1.2→1.05 Å top-x% mix decay",
            "sec33_hardware": "ibm_kawasaki H2 — out of scope without QPU access",
            "train_modes": {
                "gpt": "§3.1 warmup + GPT (LM/GRPO)",
                "prefill": "§3.1 warmup-only N_warmup≈200, no GPT steps",
                "condition": "instance-conditioned GPT (Conditional-GQE chemistry v1)",
            },
        },
        "non_goals_here": [
            "CUDA-Q / cudaq_solvers as required runtime (native JAX + stack oracle)",
            "Real-device ibm_kawasaki run",
            "Full 3-trial × all bond lengths × BeH2/N2 wall-clock on CPU (opt-in)",
        ],
    }
