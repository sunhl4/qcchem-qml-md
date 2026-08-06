"""Lightweight autoregressive generative policies for GQE (NumPy, no torch required)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def _softmax(logits: np.ndarray) -> np.ndarray:
    z = logits - float(np.max(logits))
    e = np.exp(z)
    return e / max(float(np.sum(e)), 1e-300)


def _sigmoid(x: float) -> float:
    if x >= 0:
        z = np.exp(-x)
        return float(1.0 / (1.0 + z))
    z = np.exp(x)
    return float(z / (1.0 + z))


@dataclass
class AdamState:
    m: list[np.ndarray]
    v: list[np.ndarray]
    t: int = 0


class AutoregressivePolicy:
    """Decoder-style policy: ``logits = f(prefix)`` with optional condition / KAN backbone.

    Parameters live entirely on the classical side (GQE vs VQE distinction).
    Sampling uses Boltzmann weights ``π ∝ exp(-β w)`` as in Nakaji GPT-QE.
    """

    def __init__(
        self,
        vocab_size: int,
        *,
        embed_dim: int = 16,
        condition_dim: int = 0,
        backbone: str = "linear",
        seed: int = 0,
    ) -> None:
        self.vocab_size = int(vocab_size)
        self.embed_dim = int(embed_dim)
        self.condition_dim = int(condition_dim)
        self.backbone = str(backbone)
        rng = np.random.default_rng(seed)
        scale = 0.05
        self.token_embed = rng.normal(0.0, scale, size=(self.vocab_size, self.embed_dim))
        in_dim = self.embed_dim + self.condition_dim
        if self.backbone == "kan":
            self.kan_w = rng.normal(0.0, scale, size=(in_dim, 3))
            self.kan_b = np.zeros(3, dtype=float)
            self.W = rng.normal(0.0, scale, size=(3, self.vocab_size))
        else:
            self.kan_w = np.zeros((in_dim, 3), dtype=float)
            self.kan_b = np.zeros(3, dtype=float)
            self.W = rng.normal(0.0, scale, size=(in_dim, self.vocab_size))
        self.b = np.zeros(self.vocab_size, dtype=float)
        self._adam = AdamState(
            m=[np.zeros_like(p) for p in self.parameters()],
            v=[np.zeros_like(p) for p in self.parameters()],
        )

    def parameters(self) -> list[np.ndarray]:
        if self.backbone == "kan":
            return [self.token_embed, self.kan_w, self.kan_b, self.W, self.b]
        return [self.token_embed, self.W, self.b]

    def clone_params(self) -> list[np.ndarray]:
        return [np.array(p, copy=True) for p in self.parameters()]

    def load_params(self, params: list[np.ndarray]) -> None:
        cur = self.parameters()
        if len(params) != len(cur):
            raise ValueError("parameter list length mismatch")
        for dst, src in zip(cur, params, strict=True):
            dst[...] = src

    def _context_vector(
        self, prefix: list[int], condition: np.ndarray | None
    ) -> np.ndarray:
        if not prefix:
            h = np.zeros(self.embed_dim, dtype=float)
        else:
            h = np.mean(self.token_embed[np.asarray(prefix, dtype=int)], axis=0)
        if self.condition_dim > 0:
            if condition is None:
                c = np.zeros(self.condition_dim, dtype=float)
            else:
                c = np.asarray(condition, dtype=float).ravel()
                if c.size != self.condition_dim:
                    raise ValueError(
                        f"condition dim {c.size} != policy.condition_dim {self.condition_dim}"
                    )
            return np.concatenate([h, c])
        return h

    def _hidden(self, ctx: np.ndarray) -> np.ndarray:
        if self.backbone == "kan":
            x = ctx.reshape(-1, 1)
            feats = (
                self.kan_w[:, 0:1] * x
                + self.kan_w[:, 1:2] * (x**2)
                + self.kan_w[:, 2:3] * np.tanh(x)
            )
            return feats.mean(axis=0) + self.kan_b
        return ctx

    def logits(
        self,
        prefix: list[int],
        *,
        condition: np.ndarray | None = None,
        mask: np.ndarray | None = None,
    ) -> np.ndarray:
        ctx = self._context_vector(prefix, condition)
        h = self._hidden(ctx)
        w = h @ self.W + self.b
        if mask is not None:
            w = np.where(mask, w, -1.0e9)
        return w

    def sample_sequence(
        self,
        n_gates: int,
        *,
        beta: float,
        rng: np.random.Generator,
        condition: np.ndarray | None = None,
        mask_fn=None,
    ) -> tuple[list[int], list[np.ndarray], float]:
        tokens: list[int] = []
        step_logits: list[np.ndarray] = []
        w_sum = 0.0
        for _ in range(n_gates):
            mask = None if mask_fn is None else mask_fn(tokens)
            w = self.logits(tokens, condition=condition, mask=mask)
            step_logits.append(w)
            probs = _softmax(-float(beta) * w)
            j = int(rng.choice(self.vocab_size, p=probs))
            tokens.append(j)
            w_sum += float(w[j])
        return tokens, step_logits, w_sum

    def sequence_stats(
        self,
        tokens: list[int],
        *,
        beta: float,
        condition: np.ndarray | None = None,
        mask_fn=None,
    ) -> tuple[float, float, list[np.ndarray]]:
        log_p = 0.0
        w_sum = 0.0
        step_logits: list[np.ndarray] = []
        prefix: list[int] = []
        for j in tokens:
            mask = None if mask_fn is None else mask_fn(prefix)
            w = self.logits(prefix, condition=condition, mask=mask)
            step_logits.append(w)
            probs = _softmax(-float(beta) * w)
            p = float(probs[int(j)])
            log_p += float(np.log(max(p, 1e-300)))
            w_sum += float(w[int(j)])
            prefix.append(int(j))
        return log_p, w_sum, step_logits

    def zero_grads(self) -> list[np.ndarray]:
        return [np.zeros_like(p) for p in self.parameters()]

    def _accumulate_linear_logit_grad(
        self,
        grads: list[np.ndarray],
        prefix: list[int],
        *,
        condition: np.ndarray | None,
        dlogits: np.ndarray,
    ) -> None:
        """Backprop ``dL/dlogits`` into embed / W / b for the linear backbone."""
        if self.backbone != "linear":
            return
        g_embed, g_W, g_b = grads
        ctx = self._context_vector(prefix, condition)
        g_W += np.outer(ctx, dlogits)
        g_b += dlogits
        g_ctx = self.W @ dlogits
        g_h = g_ctx[: self.embed_dim]
        if prefix:
            share = g_h / float(len(prefix))
            for t in prefix:
                g_embed[int(t)] += share

    def accumulate_grpo_grad(
        self,
        grads: list[np.ndarray],
        tokens: list[int],
        *,
        advantage: float,
        beta: float,
        ratio_clip: float,
        old_log_prob: float,
        condition: np.ndarray | None = None,
        mask_fn=None,
    ) -> None:
        log_p, _, _ = self.sequence_stats(
            tokens, beta=beta, condition=condition, mask_fn=mask_fn
        )
        ratio = float(np.exp(log_p - old_log_prob))
        clipped = float(np.clip(ratio, 1.0 - ratio_clip, 1.0 + ratio_clip))
        # Surrogate uses min(ratio A, clip A); gradient flows through unclipped branch
        # when it is the active (smaller) term.
        use_unclipped = (ratio * advantage) <= (clipped * advantage)
        scale = -advantage * (ratio if use_unclipped else 0.0)
        if abs(scale) < 1e-16:
            return
        prefix: list[int] = []
        for j in tokens:
            mask = None if mask_fn is None else mask_fn(prefix)
            w = self.logits(prefix, condition=condition, mask=mask)
            probs = _softmax(-float(beta) * w)
            # d log π(j) / d w = -β (1_{k=j} - π_k) because π∝e^{-βw}
            one_hot = np.zeros(self.vocab_size, dtype=float)
            one_hot[int(j)] = 1.0
            dlogp_dw = -float(beta) * (one_hot - probs)
            self._accumulate_linear_logit_grad(
                grads, prefix, condition=condition, dlogits=scale * dlogp_dw
            )
            prefix.append(int(j))

    def accumulate_lm_grad(
        self,
        grads: list[np.ndarray],
        tokens: list[int],
        *,
        energy: float,
        beta: float,
        energy_offset: float,
        condition: np.ndarray | None = None,
        mask_fn=None,
    ) -> None:
        _, w_sum, _ = self.sequence_stats(
            tokens, beta=beta, condition=condition, mask_fn=mask_fn
        )
        b = float(beta)
        ew = np.exp(-b * float(w_sum))
        ee = np.exp(-b * (float(energy) + float(energy_offset)))
        # L = (ew - ee)^2 ; dL/dw_sum = 2(ew-ee) * (-β ew)
        dL_dwsum = 2.0 * (ew - ee) * (-b * ew)
        prefix: list[int] = []
        for j in tokens:
            mask = None if mask_fn is None else mask_fn(prefix)
            dlogits = np.zeros(self.vocab_size, dtype=float)
            dlogits[int(j)] = float(dL_dwsum)
            self._accumulate_linear_logit_grad(
                grads, prefix, condition=condition, dlogits=dlogits
            )
            prefix.append(int(j))

    def accumulate_wmse_grad(
        self,
        grads: list[np.ndarray],
        tokens: list[int],
        prefix_energies: list[float],
        *,
        final_energy: float,
        condition: np.ndarray | None = None,
        mask_fn=None,
    ) -> None:
        w = float(np.exp(-float(final_energy)))
        prefix: list[int] = []
        n = max(len(tokens), 1)
        for j, e_t in zip(tokens, prefix_energies, strict=True):
            logit_vec = self.logits(prefix, condition=condition, mask=None if mask_fn is None else mask_fn(prefix))
            err = float(logit_vec[int(j)]) - float(e_t)
            dlogits = np.zeros(self.vocab_size, dtype=float)
            dlogits[int(j)] = (2.0 * w * err) / n
            self._accumulate_linear_logit_grad(
                grads, prefix, condition=condition, dlogits=dlogits
            )
            prefix.append(int(j))

    def adam_step(self, grads: list[np.ndarray], lr: float, *, beta1=0.9, beta2=0.999) -> None:
        self._adam.t += 1
        t = self._adam.t
        for i, (p, g) in enumerate(zip(self.parameters(), grads, strict=True)):
            self._adam.m[i] = beta1 * self._adam.m[i] + (1.0 - beta1) * g
            self._adam.v[i] = beta2 * self._adam.v[i] + (1.0 - beta2) * (g * g)
            mhat = self._adam.m[i] / (1.0 - beta1**t)
            vhat = self._adam.v[i] / (1.0 - beta2**t)
            p -= lr * mhat / (np.sqrt(vhat) + 1e-8)


def preference_logit_diff(
    policy: AutoregressivePolicy,
    winner: list[int],
    loser: list[int],
    *,
    beta: float,
    ref_policy: AutoregressivePolicy | None = None,
    condition: np.ndarray | None = None,
    mask_fn=None,
) -> float:
    lp_w, _, _ = policy.sequence_stats(winner, beta=beta, condition=condition, mask_fn=mask_fn)
    lp_l, _, _ = policy.sequence_stats(loser, beta=beta, condition=condition, mask_fn=mask_fn)
    if ref_policy is None:
        return float(lp_w - lp_l)
    rp_w, _, _ = ref_policy.sequence_stats(winner, beta=beta, condition=condition, mask_fn=mask_fn)
    rp_l, _, _ = ref_policy.sequence_stats(loser, beta=beta, condition=condition, mask_fn=mask_fn)
    return float((lp_w - lp_l) - (rp_w - rp_l))


def dpo_loss_from_z(z: float, *, beta: float) -> float:
    return float(-np.log(max(_sigmoid(beta * z), 1e-300)))


def pdpo_loss_from_z(z: float, *, beta: float, alpha: float) -> float:
    s = _sigmoid(beta * z)
    return float(-(alpha * beta * z + (1.0 - alpha) * np.log(max(s, 1e-300))))
