"""Paper-faithful GPT-QE training loop (Nakaji et al. §3.1 + Appendices A–B)."""

from __future__ import annotations

import json
import time
from collections import deque
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import numpy as np

from qchem_stack.contracts.schema_ids import GQE_TRAIN_REPORT_V1
from qchem_stack.integrations.gqe.native.cost_bridge import GQECostFn, make_oracle_record
from qchem_stack.integrations.gqe.native.paper_losses import (
    DispersionBetaState,
    grpo_loss_paper,
    logit_matching_loss_paper,
    sample_with_paper_beta,
)
from qchem_stack.integrations.gqe.native.paper_spec import (
    CHEMICAL_ACCURACY_HARTREE,
    PAPER_BATCH_SIZE,
    PAPER_BUFFER_MAX,
    PAPER_D_MODEL,
    PAPER_N_ITER,
    PAPER_N_LAYERS,
    PAPER_N_SAMPLE,
    PAPER_WARMUP_SAMPLES,
)
from qchem_stack.integrations.gqe.native.schedules import chemical_accuracy_report
from qchem_stack.integrations.gqe.native.transformer import TinyGPTConfig, init_tiny_gpt_params
from qchem_stack.integrations.gqe.probe_jax import probe_gqe_jax_installation

if TYPE_CHECKING:
    from qchem_stack.integrations.gqe.native.operator_pool import GQEOperatorPool

LossMode = Literal["lm", "grpo"]
TrainMode = Literal["gpt", "prefill"]
OracleFn = Callable[[Sequence[int]], dict[str, Any]]


@dataclass
class PaperTrainConfig:
    seq_len: int = 10
    n_epochs: int = 200
    n_sample: int = PAPER_N_SAMPLE
    n_batch: int = PAPER_BATCH_SIZE
    n_iter: int = PAPER_N_ITER
    buffer_max: int = PAPER_BUFFER_MAX
    warmup_samples: int = PAPER_WARMUP_SAMPLES
    learning_rate: float = 1e-3
    loss_mode: LossMode = "grpo"
    train_mode: TrainMode = "gpt"
    """gpt = warmup + GPT updates; prefill = warmup-only (no gradient steps)."""
    d_model: int = PAPER_D_MODEL
    n_layers: int = PAPER_N_LAYERS
    seed: int = 0
    energy_offset: float = 0.0
    """Appendix B.1 offset (N2 uses 107)."""
    pretrain_mix_start: float = 0.0
    """Initial fraction of buffer drawn from ``pretrain_dataset`` (§3.2)."""
    pretrain_mix_decay_epochs: int = 0
    """Linearly decay pretrain mix to 0 over this many epochs."""
    checkpoint_dir: str | None = None
    """If set, write progress JSON every ``checkpoint_every`` epochs."""
    checkpoint_every: int = 0
    """Epoch interval for checkpoints; 0 disables (unless checkpoint_dir set → default 25)."""
    log_every: int = 1
    """Print progress every N epochs (1 = every epoch)."""


@dataclass
class PaperTrainResult:
    best_energy: float
    best_sequence: list[int]
    history: list[dict[str, Any]] = field(default_factory=list)
    report: dict[str, Any] = field(default_factory=dict)
    params: dict[str, Any] | None = None
    n_energy_evals: int = 0


def _require_optax() -> Any:
    import optax

    return optax


def _eval_seq(
    seq: Sequence[int],
    *,
    cost_fn: GQECostFn,
    oracle_fn: OracleFn | None,
    pool: GQEOperatorPool,
    meta: dict[str, Any],
) -> dict[str, Any]:
    if oracle_fn is not None:
        rec = oracle_fn(seq)
        rec.setdefault("meta", {}).update(meta)
        return rec
    e = float(cost_fn(seq))
    return make_oracle_record(indices=seq, energy=e, pool=pool, meta=meta)


def run_paper_gqe_loop(
    cost_fn: GQECostFn,
    pool: GQEOperatorPool,
    *,
    config: PaperTrainConfig | None = None,
    oracle_fn: OracleFn | None = None,
    pretrain_dataset: list[dict[str, Any]] | None = None,
    reference_energy: float | None = None,
    scf_energy: float | None = None,
) -> PaperTrainResult:
    """FIFO replay + N_iter batch updates + dispersion β (paper §3.1)."""
    probe = probe_gqe_jax_installation()
    if not probe.get("available"):
        raise ImportError(f"paper GQE loop needs jax+optax; probe={probe}")

    import jax
    import jax.numpy as jnp

    optax = _require_optax()
    cfg = config or PaperTrainConfig()
    loss_mode = str(cfg.loss_mode).lower()
    if loss_mode not in {"lm", "grpo"}:
        raise ValueError(loss_mode)
    train_mode = str(cfg.train_mode).lower()
    if train_mode not in {"gpt", "prefill"}:
        raise ValueError(f"unsupported train_mode={train_mode!r}; expected gpt|prefill")

    gpt_cfg = TinyGPTConfig(
        vocab_size=pool.vocab_size,
        seq_len=int(cfg.seq_len),
        d_model=int(cfg.d_model),
        n_layers=int(cfg.n_layers),
        seed=int(cfg.seed),
    )
    params = init_tiny_gpt_params(gpt_cfg)
    params_old = jax.tree.map(lambda x: x.copy() if hasattr(x, "copy") else x, params)
    optimizer = optax.adam(float(cfg.learning_rate))
    opt_state = optimizer.init(params)

    beta_state = DispersionBetaState()
    buffer: deque[dict[str, Any]] = deque(maxlen=int(cfg.buffer_max))
    rng = np.random.default_rng(int(cfg.seed) + 7)
    key = jax.random.PRNGKey(int(cfg.seed))

    best_energy = float("inf")
    best_sequence: list[int] = []
    n_evals = 0
    history: list[dict[str, Any]] = []
    t0 = time.perf_counter()

    ckpt_every = int(cfg.checkpoint_every)
    if cfg.checkpoint_dir and ckpt_every <= 0:
        ckpt_every = 25
    ckpt_dir = Path(cfg.checkpoint_dir) if cfg.checkpoint_dir else None
    if ckpt_dir is not None:
        ckpt_dir.mkdir(parents=True, exist_ok=True)

    def _write_checkpoint(epoch: int, *, final: bool = False) -> None:
        if ckpt_dir is None:
            return
        payload = {
            "epoch": epoch,
            "final": final,
            "train_mode": train_mode,
            "best_energy": float(best_energy),
            "best_sequence": list(best_sequence),
            "n_energy_evals": int(n_evals),
            "elapsed_sec": float(time.perf_counter() - t0),
            "history": list(history),
            "config": {
                "seq_len": cfg.seq_len,
                "n_epochs": cfg.n_epochs,
                "n_sample": cfg.n_sample,
                "loss_mode": loss_mode,
                "train_mode": train_mode,
                "d_model": cfg.d_model,
                "n_layers": cfg.n_layers,
                "seed": cfg.seed,
                "warmup_samples": cfg.warmup_samples,
            },
        }
        if reference_energy is not None:
            payload["chemical_accuracy"] = chemical_accuracy_report(
                best_energy=best_energy,
                reference_energy=float(reference_energy),
                scf_energy=scf_energy,
            )
        name = "checkpoint_final.json" if final else f"checkpoint_ep{epoch:04d}.json"
        path = ckpt_dir / name
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        # Always refresh a stable pointer for monitoring / TIMEOUT recovery.
        (ckpt_dir / "checkpoint_latest.json").write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )

    def _push(rec: dict[str, Any]) -> None:
        nonlocal best_energy, best_sequence, n_evals
        buffer.append(rec)
        n_evals += 1
        e = float(rec["labels"]["energy_hartree"])
        if e < best_energy:
            best_energy = e
            best_sequence = list(rec["candidate"]["token_sequence"])

    # Warmup: random + HF seed (§3.1; paper N_warmup=200)
    hf_rec = _eval_seq([], cost_fn=cost_fn, oracle_fn=oracle_fn, pool=pool, meta={"seed": "hf"})
    # pad HF for fixed-length training
    id_tok = 0 if pool.include_identity else 0
    hf_pad = dict(hf_rec)
    hf_pad["candidate"] = {
        **hf_rec["candidate"],
        "token_sequence": [id_tok] * int(cfg.seq_len),
        "sequence_length": int(cfg.seq_len),
    }
    _push(hf_pad)
    while len(buffer) < min(int(cfg.warmup_samples), int(cfg.buffer_max)):
        seq = rng.integers(0, pool.vocab_size, size=int(cfg.seq_len)).tolist()
        rec = _eval_seq(
            seq, cost_fn=cost_fn, oracle_fn=oracle_fn, pool=pool, meta={"phase": "warmup"}
        )
        _push(rec)

    if pretrain_dataset:
        for rec in pretrain_dataset:
            seq = list(rec["candidate"]["token_sequence"])
            if len(seq) != int(cfg.seq_len):
                continue
            buffer.append(dict(rec))

    # Prefill-only: stop after warmup (compare against GPT path with same oracle budget)
    if train_mode == "prefill":
        hist = {
            "epoch": 0,
            "phase": "prefill",
            "loss": float("nan"),
            "loss_mode": loss_mode,
            "beta": float(beta_state.beta),
            "mean_energy": float(np.mean([float(r["labels"]["energy_hartree"]) for r in buffer])),
            "min_energy": float(best_energy),
            "best_so_far": float(best_energy),
            "buffer_size": len(buffer),
            "n_evals": n_evals,
            "pretrain_mix": 0.0,
        }
        if reference_energy is not None:
            hist["abs_err_fci"] = abs(best_energy - float(reference_energy))
            hist["within_chem_acc"] = hist["abs_err_fci"] <= CHEMICAL_ACCURACY_HARTREE
        history.append(hist)
        print(
            f"[gqe-paper] train_mode=prefill warmup={cfg.warmup_samples} "
            f"best={best_energy:.8f} n_evals={n_evals} buffer={len(buffer)}",
            flush=True,
        )
        _write_checkpoint(0, final=True)
        report = _build_report(
            cfg=cfg,
            pool=pool,
            loss_mode=loss_mode,
            train_mode=train_mode,
            best_energy=best_energy,
            best_sequence=best_sequence,
            n_evals=n_evals,
            history=history,
            probe=probe,
            reference_energy=reference_energy,
            scf_energy=scf_energy,
        )
        return PaperTrainResult(
            best_energy=float(best_energy),
            best_sequence=list(best_sequence),
            history=history,
            report=report,
            params=params,
            n_energy_evals=n_evals,
        )

    def _lm(p: Any, toks: Any, ens: Any, beta: Any) -> Any:
        return logit_matching_loss_paper(
            p,
            toks,
            ens,
            beta=beta,
            energy_offset=jnp.asarray(cfg.energy_offset, dtype=jnp.float32),
            jnp=jnp,
        )

    def _grpo(p: Any, p_old: Any, toks: Any, ens: Any) -> Any:
        return grpo_loss_paper(p, p_old, toks, ens, jnp=jnp)

    lm_vg = jax.jit(jax.value_and_grad(_lm))
    grpo_vg = jax.jit(jax.value_and_grad(_grpo, argnums=0))

    for epoch in range(int(cfg.n_epochs)):
        beta = float(beta_state.beta)
        epoch_energies: list[float] = []
        for _ in range(int(cfg.n_sample)):
            key, sub = jax.random.split(key)
            seq = sample_with_paper_beta(
                params,
                seq_len=int(cfg.seq_len),
                vocab_size=pool.vocab_size,
                key=sub,
                beta=beta,
            )
            rec = _eval_seq(
                seq.tolist(),
                cost_fn=cost_fn,
                oracle_fn=oracle_fn,
                pool=pool,
                meta={"epoch": epoch, "beta": beta, "loss_mode": loss_mode},
            )
            _push(rec)
            epoch_energies.append(float(rec["labels"]["energy_hartree"]))

        beta_state.update(epoch_energies)

        # Pretrain mix fraction (§3.2 approach ii)
        mix = 0.0
        if pretrain_dataset and cfg.pretrain_mix_start > 0 and cfg.pretrain_mix_decay_epochs > 0:
            frac = max(0.0, 1.0 - epoch / float(cfg.pretrain_mix_decay_epochs))
            mix = float(cfg.pretrain_mix_start) * frac

        buf_list = list(buffer)
        if mix > 0 and pretrain_dataset:
            n_pt = int(round(mix * len(buf_list)))
            n_pt = min(n_pt, len(pretrain_dataset), len(buf_list))
            if n_pt > 0:
                pt_idx = rng.choice(len(pretrain_dataset), size=n_pt, replace=False)
                on_idx = rng.choice(len(buf_list), size=len(buf_list) - n_pt, replace=False)
                mixed = [buf_list[int(i)] for i in on_idx] + [
                    pretrain_dataset[int(i)] for i in pt_idx
                ]
                buf_list = mixed

        last_loss = float("nan")
        for _it in range(int(cfg.n_iter)):
            if len(buf_list) < 2:
                break
            n_b = min(int(cfg.n_batch), len(buf_list))
            pick = rng.choice(len(buf_list), size=n_b, replace=False)
            seqs = []
            ens = []
            for j in pick:
                rec = buf_list[int(j)]
                s = np.asarray(rec["candidate"]["token_sequence"], dtype=np.int32)
                if s.shape[0] != cfg.seq_len:
                    if s.shape[0] > cfg.seq_len:
                        s = s[: cfg.seq_len]
                    else:
                        s = np.concatenate([s, np.zeros(cfg.seq_len - s.shape[0], dtype=np.int32)])
                seqs.append(s)
                ens.append(float(rec["labels"]["energy_hartree"]))
            toks = jnp.asarray(np.stack(seqs), dtype=jnp.int32)
            ens_j = jnp.asarray(ens, dtype=jnp.float32)
            if loss_mode == "lm":
                loss, grads = lm_vg(params, toks, ens_j, beta)
            else:
                loss, grads = grpo_vg(params, params_old, toks, ens_j)
            updates, opt_state = optimizer.update(grads, opt_state, params)
            params = optax.apply_updates(params, updates)
            last_loss = float(loss)

        # Appendix B.2: refresh θ_old at epoch end for GRPO clip ratio
        params_old = jax.tree.map(lambda x: x.copy() if hasattr(x, "copy") else x, params)

        hist = {
            "epoch": epoch,
            "loss": last_loss,
            "loss_mode": loss_mode,
            "beta": float(beta_state.beta),
            "mean_energy": float(np.mean(epoch_energies)),
            "min_energy": float(np.min(epoch_energies)),
            "best_so_far": float(best_energy),
            "buffer_size": len(buffer),
            "n_evals": n_evals,
            "pretrain_mix": mix,
        }
        if reference_energy is not None:
            hist["abs_err_fci"] = abs(best_energy - float(reference_energy))
            hist["within_chem_acc"] = hist["abs_err_fci"] <= CHEMICAL_ACCURACY_HARTREE
        history.append(hist)

        log_every = max(int(cfg.log_every), 1)
        if epoch % log_every == 0 or epoch + 1 == int(cfg.n_epochs):
            elapsed = time.perf_counter() - t0
            msg = (
                f"[gqe-paper] epoch={epoch + 1}/{cfg.n_epochs} "
                f"best={best_energy:.8f} mean_E={hist['mean_energy']:.8f} "
                f"beta={hist['beta']:.4f} n_evals={n_evals} "
                f"elapsed={elapsed / 3600:.2f}h"
            )
            if reference_energy is not None:
                msg += f" abs_err={hist.get('abs_err_fci'):.6g}"
            print(msg, flush=True)

        if (
            ckpt_dir is not None
            and ckpt_every > 0
            and ((epoch + 1) % ckpt_every == 0 or epoch + 1 == int(cfg.n_epochs))
        ):
            _write_checkpoint(epoch + 1, final=(epoch + 1 == int(cfg.n_epochs)))

    if ckpt_dir is not None and (not history or ckpt_every <= 0):
        _write_checkpoint(len(history), final=True)

    report = _build_report(
        cfg=cfg,
        pool=pool,
        loss_mode=loss_mode,
        train_mode=train_mode,
        best_energy=best_energy,
        best_sequence=best_sequence,
        n_evals=n_evals,
        history=history,
        probe=probe,
        reference_energy=reference_energy,
        scf_energy=scf_energy,
    )

    return PaperTrainResult(
        best_energy=float(best_energy),
        best_sequence=list(best_sequence),
        history=history,
        report=report,
        params=params,
        n_energy_evals=n_evals,
    )


def _build_report(
    *,
    cfg: PaperTrainConfig,
    pool: GQEOperatorPool,
    loss_mode: str,
    train_mode: str,
    best_energy: float,
    best_sequence: list[int],
    n_evals: int,
    history: list[dict[str, Any]],
    probe: dict[str, Any],
    reference_energy: float | None,
    scf_energy: float | None,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema": GQE_TRAIN_REPORT_V1,
        "plan": "B-paper",
        "paper": "arXiv:2401.09253",
        "pool_id": pool.pool_id,
        "vocab_size": pool.vocab_size,
        "train_mode": train_mode,
        "config": {
            "seq_len": cfg.seq_len,
            "n_epochs": cfg.n_epochs,
            "n_sample": cfg.n_sample,
            "n_batch": cfg.n_batch,
            "n_iter": cfg.n_iter,
            "buffer_max": cfg.buffer_max,
            "warmup_samples": cfg.warmup_samples,
            "loss_mode": loss_mode,
            "train_mode": train_mode,
            "d_model": cfg.d_model,
            "n_layers": cfg.n_layers,
            "seed": cfg.seed,
            "energy_offset": cfg.energy_offset,
        },
        "best_energy": float(best_energy),
        "best_sequence": list(best_sequence),
        "n_energy_evals": n_evals,
        "history": history,
        "jax_probe": probe,
    }
    if reference_energy is not None:
        report["chemical_accuracy"] = chemical_accuracy_report(
            best_energy=best_energy,
            reference_energy=float(reference_energy),
            scf_energy=scf_energy,
        )
    return report
