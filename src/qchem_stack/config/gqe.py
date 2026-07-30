"""Top-level GQE (GPT-QE) integration configuration — not ``quantum.algorithm``."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator

from ._base import ForbidExtraBase
from ._validation import strip_optional_text

GqeMode = Literal["paper", "native"]
GqeTrainMode = Literal["gpt", "prefill", "condition"]
GqeLossMode = Literal["lm", "grpo"]
GqeMoleculeId = Literal["h2", "lih", "beh2", "n2"]


class GqeSpec(ForbidExtraBase):
    """Nakaji GPT-QE sidecar knobs (``integrations.gqe``); default disabled.

    Chemistry (molecule / active space / SCF) stays under the usual experiment
    sections. This block only controls the generative eigensolver loop.
    """

    enabled: bool = Field(
        default=False,
        description="If true, orchestration may run GQE after variational via integrations.gqe.api.",
    )
    mode: GqeMode = Field(
        default="paper",
        description="paper = Nakaji pool×time-grid + paper trainer; native = registry pool + LM/GRPO demo loop.",
    )
    train_mode: GqeTrainMode = Field(
        default="gpt",
        description=(
            "gpt = §3.1 warmup + GPT updates; "
            "prefill = warmup-only (paper N_warmup≈200 random+HF, no GPT steps); "
            "condition = instance-conditioned GPT (bond/H fingerprint; Conditional-GQE style)."
        ),
    )
    molecule: GqeMoleculeId | None = Field(
        default=None,
        description="Paper molecule id; when set, rebuilds geometry/CAS from paper specs (overrides molecule coords).",
    )
    bond_angstrom: float = Field(
        default=0.74,
        description="Bond length in Å for paper geometry builders.",
    )
    epochs: int | None = Field(
        default=None, description="Training epochs (default: smoke/paper-aware)."
    )
    n_sample: int | None = Field(default=None, description="Sequences sampled per epoch.")
    seq_len: int | None = Field(default=None, description="Token sequence length L.")
    loss: GqeLossMode = Field(default="grpo", description="lm = logit-matching; grpo = paper GRPO.")
    seed: int | None = Field(default=None, description="RNG seed; None → experiment random_seed.")
    d_model: int = Field(
        default=64, description="Transformer width (smoke default; paper uses 192)."
    )
    n_layers: int = Field(default=2, description="Transformer depth (smoke default; paper uses 6).")
    paper_model: bool = Field(
        default=False,
        description="If true, force d_model=192 and n_layers=6 (paper §3).",
    )
    warmup_samples: int | None = Field(
        default=None,
        description="FIFO warmup oracle count; paper default 200 when omitted in paper gpt/prefill.",
    )
    buffer_max: int | None = Field(default=None)
    n_batch: int | None = Field(default=None)
    n_iter: int | None = Field(default=None)
    learning_rate: float = Field(default=1e-3)
    checkpoint_dir: str | None = Field(default=None)
    checkpoint_every: int = Field(default=0)
    log_every: int = Field(default=1)
    condition_bonds: list[float] | None = Field(
        default=None,
        description="Bond lengths (Å) for condition train_mode; None → paper H₂/molecule scan subset.",
    )
    n_condition: int = Field(
        default=8,
        description="Condition feature dim (bond + Hamiltonian coeff fingerprint).",
    )
    pool_id: str = Field(
        default="fermionic_uccsd",
        description="Operator pool id for native mode (registry).",
    )
    skip_variational: bool = Field(
        default=False,
        description="If true with enabled, orchestration skips HEA/UCCSD VQE and only runs GQE after PreQuantum.",
    )

    @field_validator("checkpoint_dir")
    @classmethod
    def _strip_ckpt(cls, v: str | None) -> str | None:
        return strip_optional_text(v)

    @field_validator("pool_id")
    @classmethod
    def _strip_pool(cls, v: str) -> str:
        return str(v).strip()
