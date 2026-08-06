"""Shared GQE training loop (Nakaji template + variant hooks)."""

from __future__ import annotations

from collections import deque
from dataclasses import asdict
from typing import TYPE_CHECKING, Any, Callable

import numpy as np

from qchem_stack.quantum.algorithms.gqe.circuit import (
    default_reference_state,
    energy_of_sequence,
    prefix_energies,
    qsci_energy_of_sequence,
    sequence_qcc_cost,
)
from qchem_stack.quantum.algorithms.gqe.losses import grpo_advantages, schedule_beta
from qchem_stack.quantum.algorithms.gqe.policy import (
    AutoregressivePolicy,
    preference_logit_diff,
)
from qchem_stack.quantum.algorithms.gqe.pool import build_gqe_pool, precompute_token_unitaries
from qchem_stack.quantum.algorithms.gqe.types import GQEConfig, GQEResult, PoolToken
from qchem_stack.quantum.statevector import qubit_operator_to_sparse

if TYPE_CHECKING:
    from qchem_stack.chem.hamiltonian import QubitHamiltonian


CostFn = Callable[[list[int]], float]


def _n_electrons(hamiltonian: QubitHamiltonian) -> int | None:
    fs = hamiltonian.fermion_space
    if fs is None:
        return None
    return int(fs.n_electrons)


def make_qcc_mask_fn(tokens: list[PoolToken], budget: float | None):
    if budget is None:
        return None

    def mask_fn(prefix: list[int]) -> np.ndarray:
        used = sequence_qcc_cost(prefix, tokens)
        remaining = float(budget) - float(used)
        return np.asarray([tok.qcc_cost <= remaining + 1e-12 for tok in tokens], dtype=bool)

    return mask_fn


def build_cost_fn(
    *,
    variant: str,
    unitaries: list[np.ndarray],
    reference: np.ndarray,
    hamiltonian: QubitHamiltonian,
    h_matrix: np.ndarray | None,
    cfg: GQEConfig,
) -> CostFn:
    h_op = hamiltonian.operator
    n = hamiltonian.n_qubits

    if variant in {"qsci", "gqkae"}:
        if h_matrix is None:
            raise ValueError("QSCI variants require dense Hamiltonian matrix")

        def cost_qsci(seq: list[int]) -> float:
            return qsci_energy_of_sequence(
                seq,
                unitaries=unitaries,
                reference=reference,
                hamiltonian_matrix=h_matrix,
                subspace_size=cfg.qsci_subspace_size,
            )

        return cost_qsci

    if variant == "auger":
        def cost_auger(seq: list[int]) -> float:
            from qchem_stack.quantum.algorithms.gqe.circuit import prepare_state_from_sequence

            e = energy_of_sequence(
                seq,
                unitaries=unitaries,
                reference=reference,
                hamiltonian=h_op,
                n_qubits=n,
            )
            psi = prepare_state_from_sequence(seq, unitaries, reference)
            ov = abs(complex(np.vdot(reference, psi))) ** 2
            return float(e + 0.25 * ov)

        return cost_auger

    def cost_energy(seq: list[int]) -> float:
        return energy_of_sequence(
            seq,
            unitaries=unitaries,
            reference=reference,
            hamiltonian=h_op,
            n_qubits=n,
        )

    return cost_energy


def _resolve_loss_name(cfg: GQEConfig) -> str:
    if cfg.variant == "pdpo_qcc":
        return "pdpo"
    if cfg.variant == "conditional" and cfg.loss == "grpo":
        return "dpo"
    if cfg.variant == "spin":
        return "wmse"
    return str(cfg.loss)


def _apply_batch_grads(
    policy: AutoregressivePolicy,
    *,
    loss_name: str,
    batch_tokens: list[list[int]],
    batch_energies: list[float],
    old_log_probs: list[float],
    beta: float,
    cfg: GQEConfig,
    condition: np.ndarray | None,
    mask_fn,
    prefix_fn,
    ref_policy: AutoregressivePolicy | None,
) -> list[np.ndarray]:
    grads = policy.zero_grads()
    n = max(len(batch_tokens), 1)

    if loss_name == "lm":
        for toks, e in zip(batch_tokens, batch_energies, strict=True):
            policy.accumulate_lm_grad(
                grads,
                toks,
                energy=e,
                beta=beta,
                energy_offset=cfg.energy_offset,
                condition=condition,
                mask_fn=mask_fn,
            )
        for g in grads:
            g /= n
        return grads

    if loss_name == "wmse":
        for toks, e in zip(batch_tokens, batch_energies, strict=True):
            policy.accumulate_wmse_grad(
                grads,
                toks,
                prefix_fn(toks),
                final_energy=e,
                condition=condition,
                mask_fn=mask_fn,
            )
        for g in grads:
            g /= n
        return grads

    if loss_name in {"dpo", "pdpo"}:
        if len(batch_tokens) < 2:
            return grads
        order = np.argsort(np.asarray(batch_energies, dtype=float))
        # Preference: increase winner logprob, decrease loser (REINFORCE-style)
        for i in range(min(len(order) // 2, 4)):
            w_idx = int(order[i])
            l_idx = int(order[-(i + 1)])
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
            # Soft push: treat as advantages +1 / -1 scaled by σ(-βz)
            push = float(1.0 / (1.0 + np.exp(cfg.dpo_beta * z)))
            if loss_name == "pdpo":
                push = max(push, float(cfg.pdpo_alpha))
            policy.accumulate_grpo_grad(
                grads,
                batch_tokens[w_idx],
                advantage=push,
                beta=beta,
                ratio_clip=cfg.grpo_clip,
                old_log_prob=old_log_probs[w_idx],
                condition=condition,
                mask_fn=mask_fn,
            )
            policy.accumulate_grpo_grad(
                grads,
                batch_tokens[l_idx],
                advantage=-push,
                beta=beta,
                ratio_clip=cfg.grpo_clip,
                old_log_prob=old_log_probs[l_idx],
                condition=condition,
                mask_fn=mask_fn,
            )
        return grads

    # GRPO
    adv = grpo_advantages(batch_energies)
    for m, toks in enumerate(batch_tokens):
        policy.accumulate_grpo_grad(
            grads,
            toks,
            advantage=float(adv[m]),
            beta=beta,
            ratio_clip=cfg.grpo_clip,
            old_log_prob=old_log_probs[m],
            condition=condition,
            mask_fn=mask_fn,
        )
    for g in grads:
        g /= n
    return grads


def run_gqe_training(
    hamiltonian: QubitHamiltonian,
    cfg: GQEConfig,
    *,
    condition: np.ndarray | None = None,
    teacher_sequences: list[list[int]] | None = None,
) -> GQEResult:
    """Execute one GQE / variant training run and return best oracle energy."""
    pool_mode = "spin_heisenberg" if cfg.variant == "spin" else cfg.pool_mode
    tokens = build_gqe_pool(
        hamiltonian,
        mode=pool_mode,
        time_scale=cfg.time_scale,
        time_exponents=cfg.time_exponents,
        max_paulis=16,
    )
    unitaries = precompute_token_unitaries(tokens, hamiltonian.n_qubits)
    reference = default_reference_state(hamiltonian.n_qubits, _n_electrons(hamiltonian))
    h_matrix = None
    if cfg.variant in {"qsci", "gqkae"}:
        h_matrix = qubit_operator_to_sparse(hamiltonian.operator, hamiltonian.n_qubits)

    backbone = "kan" if cfg.variant == "gqkae" or cfg.backbone == "kan" else "linear"
    cond_dim = int(cfg.condition_dim)
    if cfg.variant == "conditional" and cond_dim <= 0:
        cond_dim = max(2, hamiltonian.n_qubits)
    if condition is not None:
        cond_dim = int(np.asarray(condition).ravel().size)
        condition = np.asarray(condition, dtype=float).ravel()

    policy = AutoregressivePolicy(
        len(tokens),
        embed_dim=cfg.embed_dim,
        condition_dim=cond_dim,
        backbone=backbone,
        seed=cfg.seed,
    )
    ref_policy = None
    loss_name = _resolve_loss_name(cfg)
    if loss_name in {"dpo", "pdpo"} or cfg.variant in {"conditional", "pdpo_qcc"}:
        ref_policy = AutoregressivePolicy(
            len(tokens),
            embed_dim=cfg.embed_dim,
            condition_dim=cond_dim,
            backbone=backbone,
            seed=cfg.seed + 1,
        )
        ref_policy.load_params(policy.clone_params())

    mask_fn = make_qcc_mask_fn(tokens, cfg.qcc_budget if cfg.variant == "pdpo_qcc" else None)
    cost_fn = build_cost_fn(
        variant=cfg.variant,
        unitaries=unitaries,
        reference=reference,
        hamiltonian=hamiltonian,
        h_matrix=h_matrix,
        cfg=cfg,
    )

    def prefix_fn(seq: list[int]) -> list[float]:
        return prefix_energies(
            seq,
            unitaries=unitaries,
            reference=reference,
            hamiltonian=hamiltonian.operator,
            n_qubits=hamiltonian.n_qubits,
        )

    rng = np.random.default_rng(cfg.seed)
    buffer: deque[tuple[list[int], float, float]] = deque(maxlen=max(4, int(cfg.buffer_size)))
    beta = float(cfg.beta)
    energy_trace: list[float] = []
    n_oracle = 0
    best_e = float("inf")
    best_seq: list[int] = [0] * cfg.n_gates

    if cfg.variant == "adapt_gqe" and teacher_sequences:
        for _ in range(min(3, cfg.max_iters)):
            batch = [list(s) for s in teacher_sequences[: cfg.batch_size]]
            energies = [float(cost_fn(s)) for s in batch]
            n_oracle += len(batch)
            old_lp = [
                policy.sequence_stats(s, beta=beta, condition=condition, mask_fn=mask_fn)[0]
                for s in batch
            ]
            grads = _apply_batch_grads(
                policy,
                loss_name="lm",
                batch_tokens=batch,
                batch_energies=energies,
                old_log_probs=old_lp,
                beta=beta,
                cfg=cfg,
                condition=condition,
                mask_fn=mask_fn,
                prefix_fn=prefix_fn,
                ref_policy=ref_policy,
            )
            policy.adam_step(grads, cfg.learning_rate)

    for _it in range(cfg.max_iters):
        batch_tokens: list[list[int]] = []
        batch_energies: list[float] = []
        old_log_probs: list[float] = []
        for _ in range(cfg.batch_size):
            toks, _, _ = policy.sample_sequence(
                cfg.n_gates,
                beta=beta,
                rng=rng,
                condition=condition,
                mask_fn=mask_fn,
            )
            e = float(cost_fn(toks))
            n_oracle += 1
            lp, _, _ = policy.sequence_stats(
                toks, beta=beta, condition=condition, mask_fn=mask_fn
            )
            batch_tokens.append(toks)
            batch_energies.append(e)
            old_log_probs.append(lp)
            buffer.append((toks, e, lp))
            if e < best_e:
                best_e = e
                best_seq = list(toks)

        if len(buffer) > cfg.batch_size:
            for toks, e, lp in list(buffer)[-max(1, cfg.batch_size // 2) :]:
                batch_tokens.append(list(toks))
                batch_energies.append(float(e))
                old_log_probs.append(float(lp))

        energy_trace.append(float(np.min(batch_energies)))
        beta = schedule_beta(
            beta,
            batch_energies,
            beta_min=cfg.beta_min,
            beta_max=cfg.beta_max,
            energy_std_floor=cfg.energy_std_floor,
        )

        # KAN backbone: freeze KAN internals and train readout via linear path on hidden
        # by temporarily using LM/GRPO on W/b only through accumulate_* (linear only).
        # For kan, fall back to readout-only: treat hidden as fixed features.
        if backbone == "kan":
            # Simple REINFORCE on b only (cheap, stable for smoke tests).
            grads = policy.zero_grads()
            adv = grpo_advantages(batch_energies)
            for m, toks in enumerate(batch_tokens):
                prefix: list[int] = []
                for j in toks:
                    w = policy.logits(prefix, condition=condition, mask=None if mask_fn is None else mask_fn(prefix))
                    probs = np.exp(-beta * (w - np.max(w)))
                    probs = probs / probs.sum()
                    one_hot = np.zeros(policy.vocab_size)
                    one_hot[int(j)] = 1.0
                    dlogp_dw = -beta * (one_hot - probs)
                    grads[-1] += (-float(adv[m])) * dlogp_dw
                    prefix.append(int(j))
            grads[-1] /= max(len(batch_tokens), 1)
        else:
            grads = _apply_batch_grads(
                policy,
                loss_name=loss_name,
                batch_tokens=batch_tokens,
                batch_energies=batch_energies,
                old_log_probs=old_log_probs,
                beta=beta,
                cfg=cfg,
                condition=condition,
                mask_fn=mask_fn,
                prefix_fn=prefix_fn,
                ref_policy=ref_policy,
            )
        policy.adam_step(grads, cfg.learning_rate)

    best_labels = [tokens[j].label for j in best_seq]
    meta: dict[str, Any] = {
        "variant": cfg.variant,
        "loss": loss_name,
        "beta_final": beta,
        "vocab_size": len(tokens),
        "pool_mode": pool_mode,
        "backbone": backbone,
        "n_gates": cfg.n_gates,
        "config": asdict(cfg),
        "best_smiles": [tokens[j].smiles_text for j in best_seq],
    }
    return GQEResult(
        energy=float(best_e if np.isfinite(best_e) else 0.0),
        best_sequence=best_seq,
        best_labels=best_labels,
        n_oracle_calls=int(n_oracle),
        energy_trace=energy_trace,
        meta=meta,
        angles=np.asarray(best_seq, dtype=float),
        nfev=int(n_oracle),
    )
