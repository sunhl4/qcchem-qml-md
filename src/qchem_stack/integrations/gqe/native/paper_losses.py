"""Nakaji GPT-QE loss functions (Appendix B) and dispersion β (Appendix A.3)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from qchem_stack.integrations.gqe.native.paper_spec import (
    PAPER_BETA_ALPHA,
    PAPER_BETA_INIT,
    PAPER_BETA_TAU_DISP,
    PAPER_GRPO_CLIP_EPS,
)
from qchem_stack.integrations.gqe.native.transformer import tiny_gpt_logits


@dataclass
class DispersionBetaState:
    """Appendix A.3 adaptive β."""

    beta: float = PAPER_BETA_INIT
    alpha: float = PAPER_BETA_ALPHA
    tau_disp: float = PAPER_BETA_TAU_DISP
    beta_min: float = 0.1
    beta_max: float = 50.0

    def update(self, energies: np.ndarray | list[float]) -> float:
        std = float(np.std(np.asarray(energies, dtype=float)))
        if std < self.tau_disp:
            self.beta = max(self.beta_min, self.beta - self.alpha)
        else:
            self.beta = min(self.beta_max, self.beta + self.alpha)
        return float(self.beta)


def _token_logprobs_from_logits(logits: Any, tokens_batch: Any, jnp: Any) -> Any:
    """log π(j_t | …) under softmax(logits) — used for GRPO ratio."""
    log_probs = logits - jnp.max(logits, axis=-1, keepdims=True)
    log_probs = log_probs - jnp.log(jnp.sum(jnp.exp(log_probs), axis=-1, keepdims=True))
    b_idx = jnp.arange(tokens_batch.shape[0])[:, None]
    t_idx = jnp.arange(tokens_batch.shape[1])[None, :]
    return log_probs[b_idx, t_idx, tokens_batch]


def w_sum_from_params(
    params: dict[str, Any],
    tokens_batch: Any,
    jnp: Any,
    *,
    condition: Any | None = None,
) -> Any:
    """Cumulative logit sum used in paper: w_sum = Σ_t w_{j_t}^{(t)}.

    We take the selected-token logit (pre-softmax) as w_j^{(t)}.
    """
    logits = tiny_gpt_logits(params, tokens_batch, condition=condition)  # (B,T,V)
    b_idx = jnp.arange(tokens_batch.shape[0])[:, None]
    t_idx = jnp.arange(tokens_batch.shape[1])[None, :]
    selected = logits[b_idx, t_idx, tokens_batch]
    return jnp.sum(selected, axis=-1)


def logit_matching_loss_paper(
    params: dict[str, Any],
    tokens_batch: Any,
    energies: Any,
    *,
    beta: Any,
    energy_offset: Any,
    jnp: Any,
    condition: Any | None = None,
) -> Any:
    """Appendix B.1 Eq. (6): mean (e^{-β w_sum} - e^{-β (E+offset)})^2."""
    w = w_sum_from_params(params, tokens_batch, jnp, condition=condition)
    e = energies + energy_offset
    # clip exponents for stability
    a = jnp.exp(jnp.clip(-beta * w, -40.0, 40.0))
    b = jnp.exp(jnp.clip(-beta * e, -40.0, 40.0))
    return jnp.mean((a - b) ** 2)


def grpo_loss_paper(
    params: dict[str, Any],
    params_old: dict[str, Any],
    tokens_batch: Any,
    energies: Any,
    *,
    clip_eps: float = PAPER_GRPO_CLIP_EPS,
    jnp: Any,
    condition: Any | None = None,
) -> Any:
    """Appendix B.2 Eq. (9): clipped importance-weighted advantages (maximize → negate)."""
    import jax

    logits = tiny_gpt_logits(params, tokens_batch, condition=condition)
    logits_old = tiny_gpt_logits(params_old, tokens_batch, condition=condition)
    log_pi = _token_logprobs_from_logits(logits, tokens_batch, jnp)
    log_pi_old = _token_logprobs_from_logits(logits_old, tokens_batch, jnp)
    # ρ_{m,k} = π_θ / π_θold
    ratio = jnp.exp(log_pi - jax.lax.stop_gradient(log_pi_old))
    ratio_clipped = jnp.clip(ratio, 1.0 - float(clip_eps), 1.0 + float(clip_eps))

    rewards = -energies
    mean_r = jnp.mean(rewards)
    std_r = jnp.std(rewards) + 1e-6
    adv = (rewards - mean_r) / std_r
    adv = jax.lax.stop_gradient(adv)

    # mean over tokens then batch; maximize → minimize negative
    per_seq = jnp.mean(ratio_clipped, axis=-1) * adv
    return -jnp.mean(per_seq)


def sample_with_paper_beta(
    params: dict[str, Any],
    *,
    seq_len: int,
    vocab_size: int,
    key: Any,
    beta: float,
    condition: Any | None = None,
) -> np.ndarray:
    """Sample with P(j) ∝ exp(-β w_j) (paper Sample)."""
    import jax
    import jax.numpy as jnp

    tokens_list: list[int] = []
    for _t in range(int(seq_len)):
        cur = jnp.asarray([tokens_list + [0] * (seq_len - len(tokens_list))], dtype=jnp.int32)
        logits = tiny_gpt_logits(params, cur, condition=condition)[0, len(tokens_list)]
        # P ∝ e^{-β w}
        scores = -float(beta) * logits
        scores = scores - jnp.max(scores)
        probs = jnp.exp(scores)
        probs = probs / jnp.sum(probs)
        key, sub = jax.random.split(key)
        tok = int(jax.random.choice(sub, vocab_size, p=probs))
        tokens_list.append(tok)
    return np.asarray(tokens_list, dtype=np.int32)
