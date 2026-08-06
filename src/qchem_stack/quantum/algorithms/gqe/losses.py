"""GQE training losses: LM, GRPO, DPO, P-DPO, WMSE (Nakaji + A1/A2/A7)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from qchem_stack.quantum.algorithms.gqe.policy import (
    AutoregressivePolicy,
    dpo_loss_from_z,
    pdpo_loss_from_z,
    preference_logit_diff,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence


def schedule_beta(
    beta: float,
    energies: Sequence[float],
    *,
    beta_min: float,
    beta_max: float,
    energy_std_floor: float,
) -> float:
    """Nakaji Appendix A.3 adaptive inverse-temperature."""
    arr = np.asarray(list(energies), dtype=float)
    if arr.size < 2:
        return float(np.clip(beta, beta_min, beta_max))
    std = float(np.std(arr))
    b = float(beta)
    if std < float(energy_std_floor):
        b *= 0.5
    else:
        b *= 1.05
    return float(np.clip(b, beta_min, beta_max))


def logit_matching_loss(
    w_sums: Sequence[float],
    energies: Sequence[float],
    *,
    beta: float,
    energy_offset: float = 0.0,
) -> float:
    """Nakaji Eq. (6): align ``e^{-β w}`` with ``e^{-β E}``."""
    loss = 0.0
    b = float(beta)
    for w, e in zip(w_sums, energies, strict=True):
        ew = np.exp(-b * float(w))
        ee = np.exp(-b * (float(e) + float(energy_offset)))
        loss += (ew - ee) ** 2
    return float(loss / max(len(energies), 1))


def grpo_advantages(energies: Sequence[float]) -> np.ndarray:
    """Group-relative advantages with reward ``-E``."""
    e = np.asarray(list(energies), dtype=float)
    r = -e
    mu = float(np.mean(r))
    sig = float(np.std(r))
    if sig < 1.0e-12:
        return np.zeros_like(e)
    return (r - mu) / sig


def wmse_loss(
    step_logits: Sequence[np.ndarray],
    tokens: Sequence[int],
    prefix_energies: Sequence[float],
    *,
    final_energy: float,
    beta_weight: float = 1.0,
) -> float:
    """SpinGQE weighted MSE on prefix energies (A7)."""
    if not tokens:
        return 0.0
    w = float(np.exp(-beta_weight * float(final_energy)))
    loss = 0.0
    for logit_vec, j, e_t in zip(step_logits, tokens, prefix_energies, strict=True):
        loss += (float(logit_vec[int(j)]) - float(e_t)) ** 2
    return float(w * loss / len(tokens))


def scalar_batch_loss(
    policy: AutoregressivePolicy,
    batch_tokens: Sequence[list[int]],
    batch_energies: Sequence[float],
    *,
    loss_name: str,
    beta: float,
    grpo_clip: float,
    energy_offset: float,
    pdpo_alpha: float,
    dpo_beta: float,
    ref_policy: AutoregressivePolicy | None = None,
    condition: np.ndarray | None = None,
    mask_fn: Callable[[list[int]], np.ndarray] | None = None,
    prefix_energy_fn: Callable[[list[int]], list[float]] | None = None,
    old_log_probs: Sequence[float] | None = None,
) -> float:
    """Compute a scalar loss for finite-difference Adam updates."""
    name = loss_name.lower()
    if name == "lm":
        w_sums: list[float] = []
        for toks in batch_tokens:
            _, w_sum, _ = policy.sequence_stats(
                toks, beta=beta, condition=condition, mask_fn=mask_fn
            )
            w_sums.append(w_sum)
        return logit_matching_loss(
            w_sums, batch_energies, beta=beta, energy_offset=energy_offset
        )

    if name == "wmse":
        if prefix_energy_fn is None:
            raise ValueError("wmse requires prefix_energy_fn")
        total = 0.0
        for toks, e in zip(batch_tokens, batch_energies, strict=True):
            _, _, step_logits = policy.sequence_stats(
                toks, beta=beta, condition=condition, mask_fn=mask_fn
            )
            pe = prefix_energy_fn(toks)
            total += wmse_loss(step_logits, toks, pe, final_energy=e)
        return float(total / max(len(batch_tokens), 1))

    if name in {"dpo", "pdpo"}:
        if len(batch_tokens) < 2:
            return 0.0
        order = np.argsort(np.asarray(batch_energies, dtype=float))
        total = 0.0
        n_pairs = 0
        for i in range(len(order) - 1):
            w_idx = int(order[i])
            l_idx = int(order[-1 - i])
            if w_idx == l_idx:
                continue
            z = preference_logit_diff(
                policy,
                batch_tokens[w_idx],
                batch_tokens[l_idx],
                beta=beta,
                ref_policy=ref_policy,
                condition=condition,
                mask_fn=mask_fn,
            )
            if name == "pdpo":
                total += pdpo_loss_from_z(z, beta=dpo_beta, alpha=pdpo_alpha)
            else:
                total += dpo_loss_from_z(z, beta=dpo_beta)
            n_pairs += 1
        return float(total / max(n_pairs, 1))

    # Default: GRPO (Nakaji main experiment)
    adv = grpo_advantages(batch_energies)
    total = 0.0
    for m, toks in enumerate(batch_tokens):
        log_p, _, _ = policy.sequence_stats(
            toks, beta=beta, condition=condition, mask_fn=mask_fn
        )
        if old_log_probs is None:
            ratio = 1.0
        else:
            ratio = float(np.exp(log_p - float(old_log_probs[m])))
        clipped = float(np.clip(ratio, 1.0 - grpo_clip, 1.0 + grpo_clip))
        # Maximize advantage-weighted likelihood ⇒ minimize negative
        total += -min(ratio * float(adv[m]), clipped * float(adv[m]))
    return float(total / max(len(batch_tokens), 1))
