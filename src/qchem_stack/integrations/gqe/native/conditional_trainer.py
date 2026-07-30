"""Instance-conditioned GPT-QE (Conditional-GQE style) for chemistry.

Reference idea: Conditional-GQE (Digital Discovery 2025, DOI:10.1039/D5DD00138B /
arXiv:2501.16986) — generate circuits conditioned on problem instance features.

Chemistry v1: condition on bond length + Hamiltonian Pauli-coefficient fingerprint;
shared Nakaji paper operator pool; multi-geometry H₂ (or other paper molecule) training.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
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
    PAPER_N_ITER,
    PAPER_N_SAMPLE,
    PAPER_WARMUP_SAMPLES,
)
from qchem_stack.integrations.gqe.native.pauli_features import (
    hamiltonian_coefficients,
    pauli_basis_from_hamiltonian,
)
from qchem_stack.integrations.gqe.native.schedules import chemical_accuracy_report
from qchem_stack.integrations.gqe.native.transformer import TinyGPTConfig, init_tiny_gpt_params
from qchem_stack.integrations.gqe.probe_jax import probe_gqe_jax_installation

if TYPE_CHECKING:
    from collections.abc import Sequence

    from qchem_stack.integrations.gqe.native.operator_pool import GQEOperatorPool

LossMode = Literal["lm", "grpo"]


@dataclass
class ConditionedInstance:
    """One chemistry instance (geometry) for conditional training."""

    bond_angstrom: float
    condition: np.ndarray
    cost_fn: GQECostFn
    oracle_fn: Any
    pool: GQEOperatorPool
    fci_energy: float | None = None
    scf_energy: float | None = None
    label: str = ""


@dataclass
class ConditionTrainConfig:
    seq_len: int = 10
    n_epochs: int = 30
    n_sample: int = PAPER_N_SAMPLE
    n_batch: int = PAPER_BATCH_SIZE
    n_iter: int = PAPER_N_ITER
    buffer_max: int = PAPER_BUFFER_MAX
    warmup_samples: int = PAPER_WARMUP_SAMPLES
    learning_rate: float = 1e-3
    loss_mode: LossMode = "grpo"
    d_model: int = 64
    n_layers: int = 2
    seed: int = 0
    n_condition: int = 8
    energy_offset: float = 0.0
    log_every: int = 1


@dataclass
class ConditionTrainResult:
    best_energy: float
    best_sequence: list[int]
    best_bond_angstrom: float | None
    history: list[dict[str, Any]] = field(default_factory=list)
    report: dict[str, Any] = field(default_factory=dict)
    params: dict[str, Any] | None = None
    n_energy_evals: int = 0


def build_condition_vector(
    *,
    bond_angstrom: float,
    qubit_hamiltonian: Any,
    n_condition: int,
    bond_scale_angstrom: float = 2.0,
) -> np.ndarray:
    """Pack ``[bond_norm, h_coeff_fingerprint…]`` into fixed width ``n_condition``."""
    n_c = max(int(n_condition), 1)
    vec = np.zeros(n_c, dtype=np.float64)
    vec[0] = float(bond_angstrom) / max(float(bond_scale_angstrom), 1e-6)
    if n_c == 1:
        return vec
    try:
        basis = pauli_basis_from_hamiltonian(qubit_hamiltonian.operator)
        _const, h = hamiltonian_coefficients(qubit_hamiltonian.operator, basis)
        feats = np.asarray(h, dtype=np.float64).ravel()
        # normalize by max-abs for scale stability across bonds
        scale = float(np.max(np.abs(feats))) if feats.size else 1.0
        if scale < 1e-12:
            scale = 1.0
        feats = feats / scale
        n_fill = min(n_c - 1, feats.size)
        vec[1 : 1 + n_fill] = feats[:n_fill]
    except Exception:
        pass
    return vec


def run_conditioned_gqe_loop(
    instances: Sequence[ConditionedInstance],
    *,
    config: ConditionTrainConfig | None = None,
) -> ConditionTrainResult:
    """Warmup across instances, then GPT updates conditioned on instance features."""
    probe = probe_gqe_jax_installation()
    if not probe.get("available"):
        raise ImportError(f"conditioned GQE needs jax+optax; probe={probe}")
    if not instances:
        raise ValueError("conditioned GQE requires at least one ConditionedInstance")

    import jax
    import jax.numpy as jnp
    import optax

    cfg = config or ConditionTrainConfig()
    loss_mode = str(cfg.loss_mode).lower()
    if loss_mode not in {"lm", "grpo"}:
        raise ValueError(loss_mode)

    pool0 = instances[0].pool
    n_cond = int(cfg.n_condition)
    for inst in instances:
        if inst.pool.vocab_size != pool0.vocab_size:
            raise ValueError("all conditioned instances must share the same vocab_size")
        if int(inst.condition.shape[0]) != n_cond:
            raise ValueError(f"condition dim {inst.condition.shape[0]} != n_condition={n_cond}")

    gpt_cfg = TinyGPTConfig(
        vocab_size=pool0.vocab_size,
        seq_len=int(cfg.seq_len),
        d_model=int(cfg.d_model),
        n_layers=int(cfg.n_layers),
        seed=int(cfg.seed),
        n_condition=n_cond,
    )
    params = init_tiny_gpt_params(gpt_cfg)
    params_old = jax.tree.map(lambda x: x.copy() if hasattr(x, "copy") else x, params)
    optimizer = optax.adam(float(cfg.learning_rate))
    opt_state = optimizer.init(params)

    beta_state = DispersionBetaState()
    buffer: deque[dict[str, Any]] = deque(maxlen=int(cfg.buffer_max))
    rng = np.random.default_rng(int(cfg.seed) + 11)
    key = jax.random.PRNGKey(int(cfg.seed))

    best_energy = float("inf")
    best_sequence: list[int] = []
    best_bond: float | None = None
    n_evals = 0
    history: list[dict[str, Any]] = []
    t0 = time.perf_counter()

    def _eval(
        inst: ConditionedInstance, seq: Sequence[int], meta: dict[str, Any]
    ) -> dict[str, Any]:
        if inst.oracle_fn is not None:
            rec = inst.oracle_fn(seq)
        else:
            e = float(inst.cost_fn(seq))
            rec = make_oracle_record(indices=seq, energy=e, pool=inst.pool, meta={})
        rec = dict(rec)
        meta2 = {**(rec.get("meta") or {}), **meta}
        rec["meta"] = meta2
        rec["condition"] = np.asarray(inst.condition, dtype=np.float32)
        rec["bond_angstrom"] = float(inst.bond_angstrom)
        return rec

    def _push(rec: dict[str, Any]) -> None:
        nonlocal best_energy, best_sequence, best_bond, n_evals
        buffer.append(rec)
        n_evals += 1
        e = float(rec["labels"]["energy_hartree"])
        if e < best_energy:
            best_energy = e
            best_sequence = list(rec["candidate"]["token_sequence"])
            bond_val = rec.get("bond_angstrom")
            best_bond = float(bond_val) if bond_val is not None else None

    # Warmup: HF + random sequences spread across instances
    id_tok = 0
    for inst in instances:
        hf = _eval(inst, [], {"seed": "hf", "phase": "warmup"})
        hf["candidate"] = {
            **hf["candidate"],
            "token_sequence": [id_tok] * int(cfg.seq_len),
            "sequence_length": int(cfg.seq_len),
        }
        _push(hf)

    target_warm = min(int(cfg.warmup_samples), int(cfg.buffer_max))
    while len(buffer) < target_warm:
        inst = instances[int(rng.integers(0, len(instances)))]
        seq = rng.integers(0, pool0.vocab_size, size=int(cfg.seq_len)).tolist()
        _push(_eval(inst, seq, {"phase": "warmup"}))

    def _lm(p: Any, toks: Any, ens: Any, beta: Any, cond: Any) -> Any:
        return logit_matching_loss_paper(
            p,
            toks,
            ens,
            beta=beta,
            energy_offset=jnp.asarray(cfg.energy_offset, dtype=jnp.float32),
            jnp=jnp,
            condition=cond,
        )

    def _grpo(p: Any, p_old: Any, toks: Any, ens: Any, cond: Any) -> Any:
        return grpo_loss_paper(p, p_old, toks, ens, jnp=jnp, condition=cond)

    lm_vg = jax.jit(jax.value_and_grad(_lm))
    grpo_vg = jax.jit(jax.value_and_grad(_grpo, argnums=0))

    for epoch in range(int(cfg.n_epochs)):
        beta = float(beta_state.beta)
        epoch_energies: list[float] = []
        for _ in range(int(cfg.n_sample)):
            inst = instances[int(rng.integers(0, len(instances)))]
            key, sub = jax.random.split(key)
            cond = jnp.asarray(inst.condition[None, :], dtype=jnp.float32)
            seq = sample_with_paper_beta(
                params,
                seq_len=int(cfg.seq_len),
                vocab_size=pool0.vocab_size,
                key=sub,
                beta=beta,
                condition=cond,
            )
            rec = _eval(
                inst,
                seq.tolist(),
                {"epoch": epoch, "beta": beta, "loss_mode": loss_mode, "phase": "train"},
            )
            _push(rec)
            epoch_energies.append(float(rec["labels"]["energy_hartree"]))

        beta_state.update(epoch_energies)
        buf_list = list(buffer)
        last_loss = float("nan")
        for _it in range(int(cfg.n_iter)):
            if len(buf_list) < 2:
                break
            n_b = min(int(cfg.n_batch), len(buf_list))
            pick = rng.choice(len(buf_list), size=n_b, replace=False)
            seqs, ens, conds = [], [], []
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
                conds.append(np.asarray(rec["condition"], dtype=np.float32))
            toks = jnp.asarray(np.stack(seqs), dtype=jnp.int32)
            ens_j = jnp.asarray(ens, dtype=jnp.float32)
            cond_j = jnp.asarray(np.stack(conds), dtype=jnp.float32)
            if loss_mode == "lm":
                loss, grads = lm_vg(params, toks, ens_j, beta, cond_j)
            else:
                loss, grads = grpo_vg(params, params_old, toks, ens_j, cond_j)
            updates, opt_state = optimizer.update(grads, opt_state, params)
            params = optax.apply_updates(params, updates)
            last_loss = float(loss)

        params_old = jax.tree.map(lambda x: x.copy() if hasattr(x, "copy") else x, params)

        hist = {
            "epoch": epoch,
            "loss": last_loss,
            "loss_mode": loss_mode,
            "beta": float(beta_state.beta),
            "mean_energy": float(np.mean(epoch_energies)),
            "min_energy": float(np.min(epoch_energies)),
            "best_so_far": float(best_energy),
            "best_bond_angstrom": best_bond,
            "buffer_size": len(buffer),
            "n_evals": n_evals,
            "n_instances": len(instances),
        }
        # report chem-acc vs the instance matching best_bond if available
        if best_bond is not None:
            for inst in instances:
                if abs(inst.bond_angstrom - best_bond) < 1e-9 and inst.fci_energy is not None:
                    hist["abs_err_fci"] = abs(best_energy - float(inst.fci_energy))
                    hist["within_chem_acc"] = hist["abs_err_fci"] <= CHEMICAL_ACCURACY_HARTREE
                    break
        history.append(hist)

        log_every = max(int(cfg.log_every), 1)
        if epoch % log_every == 0 or epoch + 1 == int(cfg.n_epochs):
            elapsed = time.perf_counter() - t0
            print(
                f"[gqe-condition] epoch={epoch + 1}/{cfg.n_epochs} "
                f"best={best_energy:.8f} bond={best_bond} "
                f"n_evals={n_evals} elapsed={elapsed:.1f}s",
                flush=True,
            )

    # per-instance chemical accuracy table for the target bonds
    per_bond: list[dict[str, Any]] = []
    for inst in instances:
        row: dict[str, Any] = {
            "bond_angstrom": float(inst.bond_angstrom),
            "fci_energy": inst.fci_energy,
            "scf_energy": inst.scf_energy,
        }
        if (
            inst.fci_energy is not None
            and best_bond is not None
            and abs(inst.bond_angstrom - float(best_bond)) < 1e-9
        ):
            row["chemical_accuracy"] = chemical_accuracy_report(
                best_energy=best_energy,
                reference_energy=float(inst.fci_energy),
                scf_energy=inst.scf_energy,
            )
        per_bond.append(row)

    report: dict[str, Any] = {
        "schema": GQE_TRAIN_REPORT_V1,
        "plan": "B-condition",
        "paper": "arXiv:2401.09253 + Conditional-GQE DOI:10.1039/D5DD00138B",
        "train_mode": "condition",
        "pool_id": pool0.pool_id,
        "vocab_size": pool0.vocab_size,
        "config": {
            "seq_len": cfg.seq_len,
            "n_epochs": cfg.n_epochs,
            "n_sample": cfg.n_sample,
            "n_batch": cfg.n_batch,
            "n_iter": cfg.n_iter,
            "buffer_max": cfg.buffer_max,
            "warmup_samples": cfg.warmup_samples,
            "loss_mode": loss_mode,
            "d_model": cfg.d_model,
            "n_layers": cfg.n_layers,
            "seed": cfg.seed,
            "n_condition": n_cond,
            "bonds": [float(i.bond_angstrom) for i in instances],
        },
        "best_energy": float(best_energy),
        "best_sequence": list(best_sequence),
        "best_bond_angstrom": best_bond,
        "n_energy_evals": n_evals,
        "history": history,
        "per_bond": per_bond,
        "jax_probe": probe,
    }
    return ConditionTrainResult(
        best_energy=float(best_energy),
        best_sequence=list(best_sequence),
        best_bond_angstrom=best_bond,
        history=history,
        report=report,
        params=params,
        n_energy_evals=n_evals,
    )
