"""Narrow accessors for ``ExperimentConfig.gqe`` (algorithms must not parse YAML)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from qchem_stack.config.experiment import ExperimentConfig
    from qchem_stack.config.gqe import GqeSpec


def gqe_enabled(cfg: ExperimentConfig) -> bool:
    return bool(cfg.gqe.enabled)


def gqe_skip_variational(cfg: ExperimentConfig) -> bool:
    return bool(cfg.gqe.enabled and cfg.gqe.skip_variational)


def gqe_spec(cfg: ExperimentConfig) -> GqeSpec:
    return cfg.gqe


def gqe_resolved_seed(cfg: ExperimentConfig) -> int:
    if cfg.gqe.seed is not None:
        return int(cfg.gqe.seed)
    return int(cfg.random_seed)


def gqe_model_sizes(cfg: ExperimentConfig) -> tuple[int, int]:
    """Return (d_model, n_layers), applying paper_model override."""
    g = cfg.gqe
    if g.paper_model:
        return 192, 6
    return int(g.d_model), int(g.n_layers)


def gqe_train_overrides(cfg: ExperimentConfig) -> dict[str, Any]:
    """Flat kwargs for trainers derived from ``gqe:`` (None fields omitted)."""
    g = cfg.gqe
    d_model, n_layers = gqe_model_sizes(cfg)
    out: dict[str, Any] = {
        "loss_mode": str(g.loss),
        "seed": gqe_resolved_seed(cfg),
        "d_model": d_model,
        "n_layers": n_layers,
        "learning_rate": float(g.learning_rate),
        "checkpoint_every": int(g.checkpoint_every),
        "log_every": int(g.log_every),
        "mode": str(g.mode),
        "train_mode": str(g.train_mode),
        "molecule": g.molecule,
        "bond_angstrom": float(g.bond_angstrom),
        "pool_id": str(g.pool_id),
        "n_condition": int(g.n_condition),
    }
    if g.epochs is not None:
        out["n_epochs"] = int(g.epochs)
    if g.n_sample is not None:
        out["n_sample"] = int(g.n_sample)
    if g.seq_len is not None:
        out["seq_len"] = int(g.seq_len)
    if g.warmup_samples is not None:
        out["warmup_samples"] = int(g.warmup_samples)
    if g.buffer_max is not None:
        out["buffer_max"] = int(g.buffer_max)
    if g.n_batch is not None:
        out["n_batch"] = int(g.n_batch)
    if g.n_iter is not None:
        out["n_iter"] = int(g.n_iter)
    if g.checkpoint_dir is not None:
        out["checkpoint_dir"] = str(g.checkpoint_dir)
    if g.condition_bonds is not None:
        out["condition_bonds"] = [float(x) for x in g.condition_bonds]
    return out


def gqe_repro_fields(cfg: ExperimentConfig) -> dict[str, Any]:
    """YAML mirrors for repro.run_summary."""
    g = cfg.gqe
    return {
        "gqe_enabled_yaml": bool(g.enabled),
        "gqe_mode_yaml": str(g.mode),
        "gqe_train_mode_yaml": str(g.train_mode),
        "gqe_molecule_yaml": g.molecule,
        "gqe_loss_yaml": str(g.loss),
        "gqe_skip_variational_yaml": bool(g.skip_variational),
    }
