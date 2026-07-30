"""Minimal JAX causal LM for GQE token sequences (optional ``[gqe]`` extra)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class TinyGPTConfig:
    vocab_size: int
    seq_len: int
    d_model: int = 32
    n_layers: int = 2
    seed: int = 0
    n_condition: int = 0
    """If >0, logits take an instance condition vector of this width."""


def _require_jax() -> tuple[Any, Any]:
    try:
        import jax
        import jax.numpy as jnp
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "Native GQE transformer requires jax. Install with: pip install 'qchem-stack[gqe]'"
        ) from exc
    return jax, jnp


def init_tiny_gpt_params(cfg: TinyGPTConfig) -> dict[str, Any]:
    """Initialize a tiny causal Transformer (embedding + stacked self-attn MLP)."""
    jax, jnp = _require_jax()
    key = jax.random.PRNGKey(int(cfg.seed))
    d = int(cfg.d_model)
    v = int(cfg.vocab_size)
    t = int(cfg.seq_len)

    def _split(k: Any) -> tuple[Any, Any]:
        return jax.random.split(k)

    key, k1 = _split(key)
    key, k2 = _split(key)
    params: dict[str, Any] = {
        "tok_emb": jax.random.normal(k1, (v, d)) * 0.02,
        "pos_emb": jax.random.normal(k2, (t, d)) * 0.02,
        "layers": [],
        "lm_head": None,
    }
    layers = []
    for _ in range(int(cfg.n_layers)):
        mats = []
        for shape in ((d, d), (d, d), (d, d), (d, d), (d, 4 * d), (4 * d, d)):
            key, sub = _split(key)
            scale = 1.0 / np.sqrt(float(shape[0]))
            mats.append(jax.random.normal(sub, shape) * scale)
        layers.append(
            {
                "wq": mats[0],
                "wk": mats[1],
                "wv": mats[2],
                "wo": mats[3],
                "w1": mats[4],
                "w2": mats[5],
            }
        )
    key, k_head = _split(key)
    params["layers"] = layers
    params["lm_head"] = jax.random.normal(k_head, (d, v)) * 0.02
    n_cond = int(cfg.n_condition)
    if n_cond > 0:
        key, k_c = _split(key)
        scale = 1.0 / np.sqrt(float(n_cond))
        params["cond_proj"] = jax.random.normal(k_c, (n_cond, d)) * scale
    _ = jnp
    return params


def _softmax(x: Any, jnp: Any) -> Any:
    x = x - jnp.max(x, axis=-1, keepdims=True)
    e = jnp.exp(x)
    return e / jnp.sum(e, axis=-1, keepdims=True)


def _causal_attn(q: Any, k: Any, v: Any, jnp: Any) -> Any:
    scale = 1.0 / jnp.sqrt(q.shape[-1])
    scores = jnp.einsum("btd,bsd->bts", q, k) * scale
    t = scores.shape[-1]
    mask = jnp.tril(jnp.ones((t, t), dtype=scores.dtype))
    scores = jnp.where(mask[None, :, :], scores, -1e9)
    weights = _softmax(scores, jnp)
    return jnp.einsum("bts,bsd->btd", weights, v)


def _broadcast_condition(condition: Any, batch: int, jnp: Any) -> Any:
    c = jnp.asarray(condition, dtype=jnp.float32)
    if c.ndim == 1:
        c = jnp.broadcast_to(c[None, :], (batch, c.shape[0]))
    return c


def tiny_gpt_logits(
    params: dict[str, Any],
    tokens: Any,
    condition: Any | None = None,
) -> Any:
    """Forward: ``tokens`` ``(B, T)`` → logits ``(B, T, V)``.

    Optional ``condition`` ``(B, C)`` or ``(C,)`` is projected and added to every
    token embedding (Conditional-GQE style instance encoding, chemistry v1).
    """
    _, jnp = _require_jax()
    t = tokens.shape[1]
    emb = params["tok_emb"][tokens] + params["pos_emb"][None, :t, :]
    if condition is not None and "cond_proj" in params:
        c = _broadcast_condition(condition, int(tokens.shape[0]), jnp)
        emb = emb + (c @ params["cond_proj"])[:, None, :]
    x = emb
    for layer in params["layers"]:
        q = x @ layer["wq"]
        k = x @ layer["wk"]
        v = x @ layer["wv"]
        attn = _causal_attn(q, k, v, jnp)
        x = x + attn @ layer["wo"]
        h = jnp.tanh(x @ layer["w1"])
        x = x + h @ layer["w2"]
    return x @ params["lm_head"]


def sample_sequence(
    params: dict[str, Any],
    *,
    seq_len: int,
    vocab_size: int,
    key: Any,
    temperature: float = 1.0,
    condition: Any | None = None,
) -> np.ndarray:
    """Autoregressive sample one sequence of length ``seq_len`` (numpy ints)."""
    jax, jnp = _require_jax()
    tokens_list: list[int] = []
    for t in range(int(seq_len)):
        cur = jnp.asarray([tokens_list + [0] * (seq_len - len(tokens_list))], dtype=jnp.int32)
        logits = tiny_gpt_logits(params, cur, condition=condition)[0, t]
        logits = logits[: int(vocab_size)] / max(float(temperature), 1e-6)
        key, sub = jax.random.split(key)
        tok = int(jax.random.categorical(sub, logits))
        tokens_list.append(tok % int(vocab_size))
    return np.asarray(tokens_list, dtype=np.int32)
