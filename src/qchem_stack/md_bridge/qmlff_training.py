"""QML-FF training helpers."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.md_bridge.qmlff_builders import (
    QmlffModelHandle,
    _require_qmlff,
)
from qchem_stack.quantum.algorithms.tolerances import DEFAULT_LEARNING_RATE

if TYPE_CHECKING:
    from qchem_stack.md_bridge.schema import QMEFDataset


def _denormalize_energy_ev(
    energy_ev: float,
    *,
    n_atoms: int,
    norm_params: dict[str, Any] | None,
) -> float:
    """Map model energy output back to physical eV (matches QML-FF Trainer metrics)."""
    if not norm_params:
        return float(energy_ev)
    method = str(norm_params.get("method", "subtract_mean"))
    if method == "subtract_mean":
        return float(energy_ev) + float(norm_params["mean"])
    if method == "per_atom":
        return float(energy_ev) * float(n_atoms)
    if method == "standardize":
        return float(energy_ev) * float(norm_params["std"]) + float(norm_params["mean"])
    if method == "minmax_01":
        return float(energy_ev) * float(norm_params.get("E_range", 1.0)) + float(
            norm_params.get("E_min", 0.0)
        )
    return float(energy_ev)


def _model_cutoff_ang(model: Any, cutoff_ang: float | None) -> float:
    if cutoff_ang is not None:
        return float(cutoff_ang)
    cutoff = getattr(model, "cutoff", None)
    if cutoff is None and hasattr(model, "config"):
        cutoff = getattr(model.config, "cutoff", None)
    return float(cutoff if cutoff is not None else 6.0)


def train_force_field_on_qmef(
    handle: Any,
    dataset: QMEFDataset,
    *,
    n_epochs: int = 5,
    batch_size: int = 1,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    force_weight: float = 100.0,
    lr_scheduler: str = "constant",
    checkpoint_dir: str | Path = "checkpoints/qmlff_md_bridge",
    warm_start: bool = False,
    warm_start_params_only: bool = True,
    early_stopping: bool = False,
    energy_normalization: str | None = "subtract_mean",
    grad_clip: float = 1.0,
    checkpoint_save_freq: int | None = 0,
    seed: int | None = None,
) -> Any:
    """Train a force-field handle (QML-FF preset/QMP or classical H2 Morse)."""
    backend = getattr(handle, "backend", "qmlff_preset")
    if backend == "classical_h2":
        from qchem_stack.md_bridge.classical_h2_ff import train_classical_h2_on_qmef

        return train_classical_h2_on_qmef(handle, dataset)
    return _train_qmlff_handle(
        handle,
        dataset,
        n_epochs=n_epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        force_weight=force_weight,
        lr_scheduler=lr_scheduler,
        checkpoint_dir=checkpoint_dir,
        warm_start=warm_start,
        warm_start_params_only=warm_start_params_only,
        early_stopping=early_stopping,
        energy_normalization=energy_normalization,
        grad_clip=grad_clip,
        checkpoint_save_freq=checkpoint_save_freq,
        seed=seed,
    )


def train_qmlff_on_qmef(
    handle: QmlffModelHandle,
    dataset: QMEFDataset,
    *,
    n_epochs: int = 5,
    batch_size: int = 1,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    force_weight: float = 100.0,
    lr_scheduler: str = "constant",
    checkpoint_dir: str | Path = "checkpoints/qmlff_md_bridge",
    warm_start: bool = False,
    warm_start_params_only: bool = True,
    early_stopping: bool = False,
    energy_normalization: str | None = "subtract_mean",
    grad_clip: float = 1.0,
    checkpoint_save_freq: int | None = 0,
    seed: int | None = None,
) -> QmlffModelHandle:
    """Train (or fine-tune) ``handle.model`` on a :class:`QMEFDataset`."""
    return _train_qmlff_handle(
        handle,
        dataset,
        n_epochs=n_epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        force_weight=force_weight,
        lr_scheduler=lr_scheduler,
        checkpoint_dir=checkpoint_dir,
        warm_start=warm_start,
        warm_start_params_only=warm_start_params_only,
        early_stopping=early_stopping,
        energy_normalization=energy_normalization,
        grad_clip=grad_clip,
        checkpoint_save_freq=checkpoint_save_freq,
        seed=seed,
    )


def _train_qmlff_handle(
    handle: QmlffModelHandle,
    dataset: QMEFDataset,
    *,
    n_epochs: int,
    batch_size: int,
    learning_rate: float,
    force_weight: float,
    lr_scheduler: str,
    checkpoint_dir: str | Path,
    warm_start: bool,
    warm_start_params_only: bool,
    early_stopping: bool,
    energy_normalization: str | None,
    grad_clip: float,
    checkpoint_save_freq: int | None,
    seed: int | None,
) -> QmlffModelHandle:
    """Train (or fine-tune) ``handle.model`` on a :class:`QMEFDataset`.

    Hartree/Bohr units in ``dataset`` are converted to eV/Å via
    :mod:`qmlff.data.qchem_bridge.frames_to_qmlff_data`. When ``warm_start`` is
    true and ``handle.params`` / ``handle.opt_state`` are populated, the
    optimizer momentum is reused (``Trainer.from_warm_start``).

    The handle is mutated in-place and returned for convenience.
    """
    _require_qmlff()
    from qmlff.data import normalize_energies
    from qmlff.data.qchem_bridge import frames_to_qmlff_data
    from qmlff.training import Trainer, TrainerConfig

    if not dataset.frames:
        raise ValueError("dataset must contain at least one QMFrame to train on")

    frames_json = [fr.model_dump(mode="json") for fr in dataset.frames]
    train_data = frames_to_qmlff_data(frames_json)

    energy_norm_params: dict[str, Any] | None = None
    norm_method = (energy_normalization or "").strip().lower()
    if norm_method and norm_method not in {"none", "off", "false", "raw"}:
        train_data, energy_norm_params = normalize_energies(train_data, method=norm_method)

    ckpt = Path(checkpoint_dir)
    ckpt.mkdir(parents=True, exist_ok=True)

    save_freq = checkpoint_save_freq
    if save_freq is None or int(save_freq) <= 0:
        save_freq = int(n_epochs) + 1

    cfg = TrainerConfig(
        n_epochs=int(n_epochs),
        batch_size=int(batch_size),
        learning_rate=float(learning_rate),
        force_weight=float(force_weight),
        lr_scheduler=str(lr_scheduler),
        grad_clip=float(grad_clip),
        checkpoint_dir=str(ckpt),
        save_freq=int(save_freq),
        early_stopping=bool(early_stopping),
        seed=seed,
        validate_on_init=False,
    )

    reuse_opt = bool(
        warm_start and not warm_start_params_only and handle.params and handle.opt_state is not None
    )
    if reuse_opt:
        trainer = Trainer.from_warm_start(
            handle.model,
            cfg,
            train_data,
            prior_params=handle.params,
            prior_opt_state=handle.opt_state,
            prior_step=int(handle.step),
            prior_epoch=int(handle.epoch),
            energy_norm_params=energy_norm_params,
        )
    else:
        if warm_start and handle.params:
            handle.model.set_parameters(handle.params)
        trainer = Trainer(handle.model, cfg, train_data, energy_norm_params=energy_norm_params)

    history = trainer.train()
    train_history = history.get("train_history") or []
    final = train_history[-1] if train_history else {}

    handle.params = {k: np.asarray(v) for k, v in trainer.params.items()}
    handle.opt_state = trainer.opt_state
    handle.step = int(trainer.step)
    handle.epoch = int(trainer.epoch)
    handle.train_meta = {
        "n_epochs": int(n_epochs),
        "batch_size": int(batch_size),
        "learning_rate": float(learning_rate),
        "force_weight": float(force_weight),
        "lr_scheduler": str(lr_scheduler),
        "grad_clip": float(grad_clip),
        "checkpoint_save_freq": checkpoint_save_freq,
        "energy_normalization": energy_normalization,
        "backend": str(getattr(handle, "backend", "qmlff_preset")),
        "n_train_frames": len(dataset.frames),
        "energy_norm_params": dict(energy_norm_params) if energy_norm_params else None,
        "final_metrics": {
            k: (float(v) if isinstance(v, (int, float, np.integer, np.floating)) else v)
            for k, v in final.items()
        },
    }
    handle.energy_norm_params = energy_norm_params
    handle.model.set_parameters(handle.params)
    return handle
