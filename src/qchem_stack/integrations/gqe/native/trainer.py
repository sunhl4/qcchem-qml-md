"""Native GQE training loop (LM / GRPO / pretrain) with JAX + optax."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

import numpy as np

from qchem_stack.contracts.schema_ids import GQE_TRAIN_REPORT_V1
from qchem_stack.integrations.gqe.native.cost_bridge import (
    GQECostFn,
    make_oracle_record,
)
from qchem_stack.integrations.gqe.native.schedules import BetaSchedule, chemical_accuracy_report
from qchem_stack.integrations.gqe.native.transformer import (
    TinyGPTConfig,
    init_tiny_gpt_params,
    sample_sequence,
    tiny_gpt_logits,
)
from qchem_stack.integrations.gqe.probe_jax import probe_gqe_jax_installation

if TYPE_CHECKING:
    from qchem_stack.integrations.gqe.native.operator_pool import GQEOperatorPool

LossMode = Literal["lm", "grpo"]
OracleFn = Callable[[Sequence[int]], dict[str, Any]]


@dataclass
class GQETrainConfig:
    seq_len: int = 4
    n_epochs: int = 3
    samples_per_epoch: int = 8
    learning_rate: float = 1e-2
    beta: float = 5.0
    """Used when ``beta_schedule`` is None (constant β)."""
    beta_schedule: BetaSchedule | None = None
    """If set, overrides ``beta`` each epoch (Nakaji: small → large)."""
    temperature: float = 1.0
    """Base sampling temperature; effective T = temperature / β_epoch when schedule used."""
    d_model: int = 32
    n_layers: int = 2
    seed: int = 0
    keep_top_k_replay: int = 64
    loss_mode: LossMode = "lm"
    """``lm`` = Nakaji logit-matching (w_sum ≈ E); ``grpo`` = group-relative PG."""
    replay_mix_fraction: float = 0.25
    grpo_advantage_eps: float = 1e-6
    pretrain_epochs: int = 0
    """Extra epochs of offline logit-matching on ``pretrain_dataset`` before online loop."""
    energy_shift: float | None = None
    """Optional constant subtracted from energies in LM (stabilizes scale); default = batch mean."""


@dataclass
class GQETrainResult:
    best_energy: float
    best_sequence: list[int]
    history: list[dict[str, Any]] = field(default_factory=list)
    replay: list[dict[str, Any]] = field(default_factory=list)
    report: dict[str, Any] = field(default_factory=dict)
    params: dict[str, Any] | None = None


def _require_optax() -> Any:
    try:
        import optax
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "Native GQE trainer requires optax. Install with: pip install 'qchem-stack[gqe]'"
        ) from exc
    return optax


def _token_logprobs(params: dict[str, Any], tokens_batch: Any, jnp: Any) -> Any:
    logits = tiny_gpt_logits(params, tokens_batch)  # (B, T, V)
    log_probs = logits - jnp.max(logits, axis=-1, keepdims=True)
    log_probs = log_probs - jnp.log(jnp.sum(jnp.exp(log_probs), axis=-1, keepdims=True))
    b_idx = jnp.arange(tokens_batch.shape[0])[:, None]
    t_idx = jnp.arange(tokens_batch.shape[1])[None, :]
    return log_probs[b_idx, t_idx, tokens_batch]  # (B, T)


def _w_sum(params: dict[str, Any], tokens_batch: Any, jnp: Any) -> Any:
    """Nakaji w_sum: negative sum of token log-probs (proxy matched to energy)."""
    return -jnp.sum(_token_logprobs(params, tokens_batch, jnp), axis=-1)


def _logit_matching_loss(
    params: dict[str, Any],
    tokens_batch: Any,
    energies: Any,
    *,
    beta: Any,
    energy_shift: Any,
    jnp: Any,
) -> Any:
    """Match ``w_sum`` to energy via batch z-score MSE (scale-free Nakaji LM).

    Absolute ``w_sum`` (~nats) and ``E`` (Hartree) live on different scales; matching
    standardized values within the batch preserves the ranking signal that drives
    GPT-QE while remaining JIT-friendly. Boltzmann weights still emphasize low-E.
    """
    w = _w_sum(params, tokens_batch, jnp)
    w_n = (w - jnp.mean(w)) / (jnp.std(w) + 1e-6)
    e_n = (energies - jnp.mean(energies)) / (jnp.std(energies) + 1e-6)
    residual = w_n - e_n
    # energy_shift unused for z-score path but kept for API / logging compatibility
    _ = energy_shift
    e_rel = energies - jnp.min(energies)
    # Cap β·ΔE to avoid overflow → NaN when the batch collapses to one energy
    log_w = -jnp.clip(beta * e_rel, min=0.0, max=40.0)
    weights = jnp.exp(log_w)
    weights = weights / (jnp.mean(weights) + 1e-8)
    return jnp.mean(weights * residual**2)


def _effective_temperature(cfg: GQETrainConfig, beta_epoch: float) -> float:
    # Mild cooling with β (avoid hard collapse to identity token).
    return float(cfg.temperature) / (1.0 + 0.05 * max(float(beta_epoch) - 1.0, 0.0))


def _grpo_loss(
    params: dict[str, Any],
    tokens_batch: Any,
    energies: Any,
    *,
    eps: float,
    jnp: Any,
) -> Any:
    tok_lp = _token_logprobs(params, tokens_batch, jnp)
    seq_lp = jnp.sum(tok_lp, axis=-1)
    mean_e = jnp.mean(energies)
    std_e = jnp.std(energies)
    adv = (mean_e - energies) / (std_e + float(eps))
    try:
        import jax

        adv = jax.lax.stop_gradient(adv)
    except ImportError:  # pragma: no cover
        pass
    return -jnp.mean(seq_lp * adv)


def _mix_replay_batch(
    *,
    epoch_seqs: list[np.ndarray],
    epoch_energies: list[float],
    replay: list[dict[str, Any]],
    mix_fraction: float,
    seq_len: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    n = len(epoch_seqs)
    n_replay = int(round(float(mix_fraction) * n)) if replay else 0
    n_replay = min(n_replay, len(replay), n)
    if n_replay <= 0:
        return np.stack(epoch_seqs, axis=0), np.asarray(epoch_energies, dtype=np.float64)

    n_on = n - n_replay
    on_idx = rng.choice(n, size=n_on, replace=False)
    seqs = [epoch_seqs[int(i)] for i in on_idx]
    ens = [epoch_energies[int(i)] for i in on_idx]
    pick = rng.choice(len(replay), size=n_replay, replace=False)
    for j in pick:
        rec = replay[int(j)]
        seq = np.asarray(rec["candidate"]["token_sequence"], dtype=np.int32)
        if seq.shape[0] != seq_len:
            if seq.shape[0] > seq_len:
                seq = seq[:seq_len]
            else:
                pad = np.zeros(seq_len - seq.shape[0], dtype=np.int32)
                seq = np.concatenate([seq, pad])
        seqs.append(seq)
        ens.append(float(rec["labels"]["energy_hartree"]))
    return np.stack(seqs, axis=0), np.asarray(ens, dtype=np.float64)


def _resolve_beta(cfg: GQETrainConfig, epoch: int) -> float:
    if cfg.beta_schedule is not None:
        return float(cfg.beta_schedule.value(epoch, cfg.n_epochs))
    return float(cfg.beta)


def pretrain_on_dataset(
    params: dict[str, Any],
    *,
    tokens: np.ndarray,
    energies: np.ndarray,
    config: GQETrainConfig,
    opt_state: Any | None = None,
) -> tuple[dict[str, Any], Any, list[dict[str, Any]]]:
    """Offline logit-matching on a fixed ``{j, E}`` dataset (Nakaji pre-training)."""
    import jax
    import jax.numpy as jnp

    optax = _require_optax()
    optimizer = optax.adam(float(config.learning_rate))
    state = opt_state if opt_state is not None else optimizer.init(params)
    toks = jnp.asarray(tokens, dtype=jnp.int32)
    ens = jnp.asarray(energies, dtype=jnp.float32)
    shift = (
        float(config.energy_shift)
        if config.energy_shift is not None
        else float(np.mean(np.asarray(energies)))
    )
    history: list[dict[str, Any]] = []

    def _loss(p: Any) -> Any:
        return _logit_matching_loss(
            p, toks, ens, beta=jnp.asarray(config.beta), energy_shift=jnp.asarray(shift), jnp=jnp
        )

    loss_and_grad = jax.jit(jax.value_and_grad(_loss))
    for ep in range(int(config.pretrain_epochs)):
        loss, grads = loss_and_grad(params)
        updates, state = optimizer.update(grads, state, params)
        params = optax.apply_updates(params, updates)
        history.append({"pretrain_epoch": ep, "loss": float(loss), "energy_shift": shift})
    return params, state, history


def run_gqe_lm_loop(
    cost_fn: GQECostFn,
    pool: GQEOperatorPool,
    *,
    config: GQETrainConfig | None = None,
    oracle_fn: OracleFn | None = None,
    pretrain_dataset: list[dict[str, Any]] | None = None,
    reference_energy: float | None = None,
    scf_energy: float | None = None,
) -> GQETrainResult:
    """Sample → oracle score → JAX update (Plan B native loop).

    Args:
        cost_fn: energy-only callable (used if ``oracle_fn`` is None).
        oracle_fn: optional full oracle returning records (with Pauli features).
        pretrain_dataset: optional offline ``{j, E}`` records for pre-training.
        reference_energy: FCI/exact energy for chemical-accuracy reporting.
        scf_energy: optional SCF reference for correlation diagnostics.
    """
    probe = probe_gqe_jax_installation()
    if not probe.get("available"):
        raise ImportError(
            "GQE native trainer needs jax+optax; "
            f"probe={probe}. Install with: pip install 'qchem-stack[gqe]'"
        )

    import jax
    import jax.numpy as jnp

    optax = _require_optax()
    cfg = config or GQETrainConfig()
    loss_mode = str(cfg.loss_mode).lower()
    if loss_mode not in {"lm", "grpo"}:
        raise ValueError(f"loss_mode must be 'lm' or 'grpo'; got {cfg.loss_mode!r}")

    gpt_cfg = TinyGPTConfig(
        vocab_size=pool.vocab_size,
        seq_len=int(cfg.seq_len),
        d_model=int(cfg.d_model),
        n_layers=int(cfg.n_layers),
        seed=int(cfg.seed),
    )
    params = init_tiny_gpt_params(gpt_cfg)
    optimizer = optax.adam(float(cfg.learning_rate))
    opt_state = optimizer.init(params)

    pretrain_hist: list[dict[str, Any]] = []
    if pretrain_dataset and int(cfg.pretrain_epochs) > 0:
        from qchem_stack.integrations.gqe.native.pauli_features import dataset_from_oracle_records

        toks_pt, ens_pt = dataset_from_oracle_records(pretrain_dataset)
        if toks_pt.shape[1] != int(cfg.seq_len):
            raise ValueError(f"pretrain seq_len {toks_pt.shape[1]} != config.seq_len {cfg.seq_len}")
        params, opt_state, pretrain_hist = pretrain_on_dataset(
            params, tokens=toks_pt, energies=ens_pt, config=cfg, opt_state=opt_state
        )

    # Seed with HF / identity circuit so SCF is always in the candidate set.
    if oracle_fn is not None:
        hf_rec = oracle_fn([])
    else:
        hf_e = float(cost_fn([]))
        hf_rec = make_oracle_record(indices=[], energy=hf_e, pool=pool, meta={"seed": "hf"})
    hf_energy = float(hf_rec["labels"]["energy_hartree"])
    # Pad with identity token (index 0 when include_identity) for fixed seq_len training
    id_tok = 0 if pool.include_identity else 0
    hf_rec = dict(hf_rec)
    hf_rec["candidate"] = dict(hf_rec["candidate"])
    hf_rec["candidate"]["token_sequence"] = [id_tok] * int(cfg.seq_len)
    hf_rec["candidate"]["sequence_length"] = int(cfg.seq_len)
    hf_rec["meta"] = {**(hf_rec.get("meta") or {}), "seed": "hf_padded", "true_hf_empty": True}
    best_energy = hf_energy
    best_sequence: list[int] = []
    replay: list[dict[str, Any]] = [hf_rec]
    history: list[dict[str, Any]] = []

    key = jax.random.PRNGKey(int(cfg.seed))
    rng = np.random.default_rng(int(cfg.seed) + 17)

    def _lm_loss(p: Any, toks: Any, ens: Any, beta: Any, shift: Any) -> Any:
        return _logit_matching_loss(p, toks, ens, beta=beta, energy_shift=shift, jnp=jnp)

    def _grpo(p: Any, toks: Any, ens: Any) -> Any:
        return _grpo_loss(p, toks, ens, eps=float(cfg.grpo_advantage_eps), jnp=jnp)

    lm_vg = jax.jit(jax.value_and_grad(_lm_loss))
    grpo_vg = jax.jit(jax.value_and_grad(_grpo))

    for epoch in range(int(cfg.n_epochs)):
        beta_ep = _resolve_beta(cfg, epoch)
        temp_ep = _effective_temperature(cfg, beta_ep)
        epoch_seqs: list[np.ndarray] = []
        epoch_energies: list[float] = []
        for _ in range(int(cfg.samples_per_epoch)):
            key, sub = jax.random.split(key)
            seq = sample_sequence(
                params,
                seq_len=int(cfg.seq_len),
                vocab_size=pool.vocab_size,
                key=sub,
                temperature=float(temp_ep),
            )
            if oracle_fn is not None:
                rec = oracle_fn(seq.tolist())
                rec.setdefault("meta", {})
                rec["meta"].update({"epoch": epoch, "loss_mode": loss_mode, "beta": beta_ep})
                energy = float(rec["labels"]["energy_hartree"])
            else:
                energy = float(cost_fn(seq.tolist()))
                rec = make_oracle_record(
                    indices=seq.tolist(),
                    energy=energy,
                    pool=pool,
                    meta={"epoch": epoch, "loss_mode": loss_mode, "beta": beta_ep},
                )
            epoch_seqs.append(seq)
            epoch_energies.append(energy)
            replay.append(rec)
            if energy < best_energy:
                best_energy = energy
                best_sequence = [int(x) for x in seq.tolist()]

        replay.sort(key=lambda r: float(r["labels"]["energy_hartree"]))
        replay = replay[: int(cfg.keep_top_k_replay)]

        toks_np, ens_np = _mix_replay_batch(
            epoch_seqs=epoch_seqs,
            epoch_energies=epoch_energies,
            replay=replay,
            mix_fraction=float(cfg.replay_mix_fraction),
            seq_len=int(cfg.seq_len),
            rng=rng,
        )
        toks = jnp.asarray(toks_np, dtype=jnp.int32)
        ens = jnp.asarray(ens_np, dtype=jnp.float32)
        shift = float(cfg.energy_shift) if cfg.energy_shift is not None else float(np.mean(ens_np))

        if loss_mode == "lm":
            loss, grads = lm_vg(params, toks, ens, beta_ep, shift)
        else:
            loss, grads = grpo_vg(params, toks, ens)
        updates, opt_state = optimizer.update(grads, opt_state, params)
        params = optax.apply_updates(params, updates)

        hist = {
            "epoch": epoch,
            "loss": float(loss),
            "loss_mode": loss_mode,
            "beta": float(beta_ep),
            "temperature": float(temp_ep),
            "energy_shift": float(shift),
            "mean_energy": float(np.mean(epoch_energies)),
            "min_energy": float(np.min(epoch_energies)),
            "best_so_far": float(best_energy),
            "n_train_batch": int(toks_np.shape[0]),
            "n_replay": len(replay),
        }
        history.append(hist)

    report: dict[str, Any] = {
        "schema": GQE_TRAIN_REPORT_V1,
        "plan": "B",
        "pool_id": pool.pool_id,
        "vocab_size": pool.vocab_size,
        "n_qubits": pool.n_qubits,
        "config": {
            "seq_len": cfg.seq_len,
            "n_epochs": cfg.n_epochs,
            "samples_per_epoch": cfg.samples_per_epoch,
            "learning_rate": cfg.learning_rate,
            "beta": cfg.beta,
            "beta_schedule": (
                None
                if cfg.beta_schedule is None
                else {
                    "kind": cfg.beta_schedule.kind,
                    "beta_start": cfg.beta_schedule.beta_start,
                    "beta_end": cfg.beta_schedule.beta_end,
                }
            ),
            "d_model": cfg.d_model,
            "n_layers": cfg.n_layers,
            "seed": cfg.seed,
            "loss_mode": loss_mode,
            "replay_mix_fraction": float(cfg.replay_mix_fraction),
            "pretrain_epochs": int(cfg.pretrain_epochs),
        },
        "best_energy": float(best_energy),
        "best_sequence": list(best_sequence),
        "history": history,
        "pretrain_history": pretrain_hist,
        "n_replay": len(replay),
        "jax_probe": probe,
    }
    if reference_energy is not None:
        report["chemical_accuracy"] = chemical_accuracy_report(
            best_energy=best_energy,
            reference_energy=float(reference_energy),
            scf_energy=scf_energy,
        )

    return GQETrainResult(
        best_energy=float(best_energy),
        best_sequence=list(best_sequence),
        history=history,
        replay=replay,
        report=report,
        params=params,
    )


def run_random_baseline(
    cost_fn: GQECostFn,
    pool: GQEOperatorPool,
    *,
    seq_len: int = 4,
    n_samples: int = 16,
    seed: int = 0,
) -> dict[str, Any]:
    """NumPy random-search baseline (no JAX) for smoke / parity checks."""
    rng = np.random.default_rng(int(seed))
    best_e = float("inf")
    best_seq: list[int] = []
    energies: list[float] = []
    for _ in range(int(n_samples)):
        seq = rng.integers(0, pool.vocab_size, size=int(seq_len)).tolist()
        e = float(cost_fn(seq))
        energies.append(e)
        if e < best_e:
            best_e = e
            best_seq = [int(i) for i in seq]
    return {
        "schema": GQE_TRAIN_REPORT_V1,
        "plan": "B-baseline",
        "best_energy": best_e,
        "best_sequence": best_seq,
        "mean_energy": float(np.mean(energies)) if energies else float("nan"),
        "n_samples": int(n_samples),
        "pool_id": pool.pool_id,
    }
