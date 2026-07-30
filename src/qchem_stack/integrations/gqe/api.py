"""Stable entrypoint: run GPT-QE from ``ExperimentConfig`` / YAML path."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.config import ExperimentConfig, load_experiment_config
from qchem_stack.config.gqe_helpers import gqe_train_overrides
from qchem_stack.contracts.schema_ids import GQE_TRAIN_REPORT_V1
from qchem_stack.integrations.gqe.native.cost_bridge import make_gqe_cost, make_gqe_oracle
from qchem_stack.integrations.gqe.native.operator_pool import pool_summary
from qchem_stack.integrations.gqe.native.paper_pool import build_paper_uccsd_pool
from qchem_stack.integrations.gqe.native.paper_spec import (
    PAPER_BATCH_SIZE,
    PAPER_BOND_LENGTHS_ANG,
    PAPER_BUFFER_MAX,
    PAPER_MOLECULES,
    PAPER_N_ITER,
    PAPER_N_SAMPLE,
    PAPER_WARMUP_SAMPLES,
)
from qchem_stack.integrations.gqe.native.paper_trainer import PaperTrainConfig, run_paper_gqe_loop
from qchem_stack.integrations.gqe.native.problem_bridge import (
    GQEProblemBundle,
    _fci_energy,
    _scf_from_meta,
    build_gqe_problem_from_config,
)
from qchem_stack.integrations.gqe.native.trainer import GQETrainConfig, run_gqe_lm_loop
from qchem_stack.integrations.gqe.probe_jax import probe_gqe_jax_installation


def _load_cfg(cfg: ExperimentConfig | str | Path) -> tuple[ExperimentConfig, str | None]:
    if isinstance(cfg, (str, Path)):
        path = str(cfg)
        return load_experiment_config(cfg), path
    return cfg, None


def _with_paper_pool(bundle: GQEProblemBundle) -> GQEProblemBundle:
    """Replace registry pool with Nakaji Appendix A.2 Pauli × time-grid pool."""
    qh = bundle.qubit_hamiltonian
    hop = qh.operator
    pool = build_paper_uccsd_pool(qh, include_identity=True)
    exe = StatevectorHeaExecutor()
    ne = int(bundle.n_electrons)
    cost = make_gqe_cost(exe, hop, pool, n_electrons=ne)
    oracle = make_gqe_oracle(exe, hop, pool, n_electrons=ne)
    return GQEProblemBundle(
        config_path=bundle.config_path,
        experiment_id=bundle.experiment_id,
        n_qubits=bundle.n_qubits,
        n_electrons=ne,
        scf_energy=_scf_from_meta(qh),
        fci_energy=_fci_energy(qh, n_electrons=ne),
        pool=pool,
        cost_fn=cost,
        oracle_fn=oracle,
        qubit_hamiltonian=qh,
        meta={**dict(bundle.meta), "pool": pool_summary(pool), "gqe_mode": "paper"},
    )


def run_gqe_from_config(
    cfg: ExperimentConfig | str | Path,
    *,
    cfg_path: str | Path | None = None,
) -> dict[str, Any]:
    """Run Plan-B GQE and return a ``GQE_TRAIN_REPORT_V1`` dict.

    * ``gqe.mode=paper`` — Nakaji pool (UCCSD Pauli × time grid) + paper trainer.
    * ``gqe.mode=native`` — registry operator pool + demo LM/GRPO loop.
    * ``gqe.train_mode`` — ``gpt`` | ``prefill`` | ``condition`` (paper path).

    Requires optional extra ``pip install 'qchem-stack[gqe]'`` (jax/optax).
    """
    experiment, path_from_arg = _load_cfg(cfg)
    path = str(cfg_path) if cfg_path is not None else path_from_arg
    overrides = gqe_train_overrides(experiment)
    mode = str(overrides["mode"]).lower()
    train_mode = str(overrides.get("train_mode", "gpt")).lower()
    probe = probe_gqe_jax_installation()
    if not probe.get("available"):
        raise ImportError(
            "GQE requires jax and optax. Install with: pip install 'qchem-stack[gqe]'. "
            f"probe={probe}"
        )

    if train_mode == "condition":
        return _run_condition_mode(experiment, overrides=overrides, cfg_path=path)
    if mode == "paper":
        return _run_paper_mode(experiment, overrides=overrides, cfg_path=path)
    if mode == "native":
        if train_mode != "gpt":
            raise ValueError(
                f"gqe.train_mode={train_mode!r} requires gqe.mode=paper (or train_mode=condition)"
            )
        return _run_native_mode(experiment, overrides=overrides, cfg_path=path)
    raise ValueError(f"unsupported gqe.mode={mode!r}; expected 'paper' or 'native'")


def _paper_defaults(overrides: dict[str, Any], *, train_mode: str) -> dict[str, int]:
    """Paper §3.1 defaults; smoke YAML may still override explicitly."""
    # Prefer paper constants when caller did not set them (None omitted from overrides).
    return {
        "warmup_samples": int(overrides.get("warmup_samples", PAPER_WARMUP_SAMPLES)),
        "buffer_max": int(overrides.get("buffer_max", PAPER_BUFFER_MAX)),
        "n_batch": int(overrides.get("n_batch", PAPER_BATCH_SIZE)),
        "n_iter": int(overrides.get("n_iter", PAPER_N_ITER)),
        "n_sample": int(
            overrides.get(
                "n_sample",
                PAPER_N_SAMPLE if train_mode == "gpt" else PAPER_N_SAMPLE,
            )
        ),
    }


def _run_paper_mode(
    experiment: ExperimentConfig,
    *,
    overrides: dict[str, Any],
    cfg_path: str | None,
) -> dict[str, Any]:
    from qchem_stack.integrations.gqe.native.paper_molecules import build_paper_gqe_problem

    train_mode = str(overrides.get("train_mode", "gpt")).lower()
    if train_mode not in {"gpt", "prefill"}:
        raise ValueError(f"unsupported gqe.train_mode={train_mode!r} for paper mode")

    mol = overrides.get("molecule")
    bond = float(overrides["bond_angstrom"])
    energy_offset = 0.0
    defaults = _paper_defaults(overrides, train_mode=train_mode)
    if mol is not None:
        mol_id = str(mol)
        if mol_id not in PAPER_MOLECULES:
            raise ValueError(f"unknown gqe.molecule={mol_id!r}")
        paper_spec = PAPER_MOLECULES[mol_id]  # type: ignore[index]
        bundle = build_paper_gqe_problem(mol_id, bond_length_angstrom=bond)  # type: ignore[arg-type]
        default_epochs = min(30, int(paper_spec.n_epochs)) if train_mode == "gpt" else 0
        default_seq = int(paper_spec.seq_len)
        energy_offset = float(paper_spec.energy_offset)
    else:
        bundle = _with_paper_pool(
            build_gqe_problem_from_config(
                experiment,
                pool_id=str(overrides["pool_id"]),
                cfg_path=cfg_path,
            )
        )
        default_epochs = 30 if train_mode == "gpt" else 0
        default_seq = 10

    # prefill ignores epochs (warmup only); still accept explicit override for reporting
    n_epochs = int(overrides.get("n_epochs", default_epochs))
    if train_mode == "prefill":
        n_epochs = 0

    train = PaperTrainConfig(
        seq_len=int(overrides.get("seq_len", default_seq)),
        n_epochs=n_epochs,
        n_sample=int(defaults["n_sample"]),
        n_batch=int(defaults["n_batch"]),
        n_iter=int(defaults["n_iter"]),
        buffer_max=int(defaults["buffer_max"]),
        warmup_samples=int(defaults["warmup_samples"]),
        learning_rate=float(overrides["learning_rate"]),
        loss_mode=str(overrides["loss_mode"]),  # type: ignore[arg-type]
        train_mode=train_mode,  # type: ignore[arg-type]
        d_model=int(overrides["d_model"]),
        n_layers=int(overrides["n_layers"]),
        seed=int(overrides["seed"]),
        energy_offset=energy_offset,
        checkpoint_dir=overrides.get("checkpoint_dir"),
        checkpoint_every=int(overrides.get("checkpoint_every", 0)),
        log_every=int(overrides.get("log_every", 1)),
    )
    result = run_paper_gqe_loop(
        bundle.cost_fn,
        bundle.pool,
        config=train,
        oracle_fn=bundle.oracle_fn,
        reference_energy=bundle.fci_energy,
        scf_energy=bundle.scf_energy,
    )
    report = dict(result.report)
    report.setdefault("schema", GQE_TRAIN_REPORT_V1)
    report["experiment_id"] = experiment.experiment_id
    report["config_path"] = cfg_path
    report["gqe_mode"] = "paper"
    report["train_mode"] = train_mode
    report["bundle_meta"] = {
        "n_qubits": bundle.n_qubits,
        "scf_energy": bundle.scf_energy,
        "fci_energy": bundle.fci_energy,
        "vocab_size": bundle.pool.vocab_size,
    }
    return report


def _run_condition_mode(
    experiment: ExperimentConfig,
    *,
    overrides: dict[str, Any],
    cfg_path: str | None,
) -> dict[str, Any]:
    from qchem_stack.integrations.gqe.native.conditional_trainer import (
        ConditionedInstance,
        ConditionTrainConfig,
        build_condition_vector,
        run_conditioned_gqe_loop,
    )
    from qchem_stack.integrations.gqe.native.paper_molecules import build_paper_gqe_problem

    mol = overrides.get("molecule") or "h2"
    mol_id = str(mol)
    if mol_id not in PAPER_MOLECULES:
        raise ValueError(f"condition mode requires gqe.molecule in {sorted(PAPER_MOLECULES)}")
    paper_spec = PAPER_MOLECULES[mol_id]  # type: ignore[index]
    bonds = overrides.get("condition_bonds")
    if not bonds:
        # smoke-friendly subset of paper scan; full scan via YAML
        grid = list(PAPER_BOND_LENGTHS_ANG[mol_id])  # type: ignore[index]
        bonds = grid[:3] if len(grid) >= 3 else grid
    n_cond = int(overrides.get("n_condition", 8))
    defaults = _paper_defaults(overrides, train_mode="condition")

    instances: list[ConditionedInstance] = []
    for r in bonds:
        bundle = build_paper_gqe_problem(mol_id, bond_length_angstrom=float(r))  # type: ignore[arg-type]
        cond = build_condition_vector(
            bond_angstrom=float(r),
            qubit_hamiltonian=bundle.qubit_hamiltonian,
            n_condition=n_cond,
        )
        instances.append(
            ConditionedInstance(
                bond_angstrom=float(r),
                condition=cond,
                cost_fn=bundle.cost_fn,
                oracle_fn=bundle.oracle_fn,
                pool=bundle.pool,
                fci_energy=bundle.fci_energy,
                scf_energy=bundle.scf_energy,
                label=f"{mol_id}@{r}",
            )
        )

    train = ConditionTrainConfig(
        seq_len=int(overrides.get("seq_len", min(paper_spec.seq_len, 10))),
        n_epochs=int(overrides.get("n_epochs", 5)),
        n_sample=int(overrides.get("n_sample", 8)),
        n_batch=int(overrides.get("n_batch", defaults["n_batch"])),
        n_iter=int(overrides.get("n_iter", defaults["n_iter"])),
        buffer_max=int(overrides.get("buffer_max", defaults["buffer_max"])),
        warmup_samples=int(overrides.get("warmup_samples", defaults["warmup_samples"])),
        learning_rate=float(overrides["learning_rate"]),
        loss_mode=str(overrides["loss_mode"]),  # type: ignore[arg-type]
        d_model=int(overrides["d_model"]),
        n_layers=int(overrides["n_layers"]),
        seed=int(overrides["seed"]),
        n_condition=n_cond,
        energy_offset=float(paper_spec.energy_offset),
        log_every=int(overrides.get("log_every", 1)),
    )
    result = run_conditioned_gqe_loop(instances, config=train)
    report = dict(result.report)
    report.setdefault("schema", GQE_TRAIN_REPORT_V1)
    report["experiment_id"] = experiment.experiment_id
    report["config_path"] = cfg_path
    report["gqe_mode"] = "paper"
    report["train_mode"] = "condition"
    report["bundle_meta"] = {
        "n_qubits": instances[0].pool.n_qubits,
        "vocab_size": instances[0].pool.vocab_size,
        "bonds": [float(i.bond_angstrom) for i in instances],
    }
    return report


def _run_native_mode(
    experiment: ExperimentConfig,
    *,
    overrides: dict[str, Any],
    cfg_path: str | None,
) -> dict[str, Any]:
    bundle = build_gqe_problem_from_config(
        experiment,
        pool_id=str(overrides["pool_id"]),
        cfg_path=cfg_path,
    )
    train = GQETrainConfig(
        seq_len=int(overrides.get("seq_len", 4)),
        n_epochs=int(overrides.get("n_epochs", 3)),
        samples_per_epoch=int(overrides.get("n_sample", 8)),
        learning_rate=float(overrides["learning_rate"]),
        loss_mode=str(overrides["loss_mode"]),  # type: ignore[arg-type]
        d_model=int(overrides["d_model"]),
        n_layers=int(overrides["n_layers"]),
        seed=int(overrides["seed"]),
        keep_top_k_replay=int(overrides.get("buffer_max", 64)),
    )
    result = run_gqe_lm_loop(bundle.cost_fn, bundle.pool, config=train)
    report = dict(result.report)
    report.setdefault("schema", GQE_TRAIN_REPORT_V1)
    report["plan"] = "B-native"
    report["best_energy"] = float(result.best_energy)
    report["best_sequence"] = list(result.best_sequence)
    report["n_energy_evals"] = int(report.get("n_energy_evals") or len(result.history))
    report["experiment_id"] = experiment.experiment_id
    report["config_path"] = cfg_path
    report["gqe_mode"] = "native"
    report["train_mode"] = "gpt"
    report["jax_probe"] = probe_gqe_jax_installation()
    return report


__all__ = ["run_gqe_from_config"]
