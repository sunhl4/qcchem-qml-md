"""Optional bridge to the QML-FF (Quantum ML force field + JAX-MD) project.

This module is **additive** and does **not** alter any existing ``md_bridge`` surface.
All ``qmlff`` / ``jax_md`` imports are deferred to function bodies so the rest of
``qchem_stack`` remains usable without those packages installed.

Two equally valid install layouts are supported:

* ``pip install -e /path/to/QML-FF`` (editable install of the sibling repo)
* ``PYTHONPATH=/path/to/QML-FF`` (manual import path)

Units convention at the boundary
--------------------------------
* qchem_stack internals: **Hartree, Bohr, Hartree/Bohr** (matches :class:`QMFrame`).
* QML-FF / JAX-MD internals: **eV, Å, eV/Å, ps, K, amu**.

Conversion is centralised here so callers can stay in their native units.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import numpy as np

from qchem_stack.exceptions import PipelineError

if TYPE_CHECKING:
    from collections.abc import Sequence

    from qchem_stack.md_bridge.schema import QMEFDataset

ForceFieldBackend = Literal[
    "qmlff_preset",
    "qmlff_quantum",
    "qmlff_angle",
    "qmlff_qmp_h2",
    "classical_h2",
]


_BOHR_TO_ANGSTROM = 0.529177210903
_HARTREE_TO_EV = 27.211386245988
_HARTREE_BOHR_TO_EV_ANG = _HARTREE_TO_EV / _BOHR_TO_ANGSTROM

_Z_TO_SYMBOL = {
    1: "H",
    2: "He",
    3: "Li",
    4: "Be",
    5: "B",
    6: "C",
    7: "N",
    8: "O",
    9: "F",
    10: "Ne",
    11: "Na",
    12: "Mg",
    13: "Al",
    14: "Si",
    15: "P",
    16: "S",
    17: "Cl",
    18: "Ar",
    19: "K",
    20: "Ca",
    26: "Fe",
    27: "Co",
    28: "Ni",
    29: "Cu",
}
_SYMBOL_TO_Z = {v: k for k, v in _Z_TO_SYMBOL.items()}


def _require_qmlff() -> Any:
    """Import qmlff lazily; raise a helpful error if unavailable."""
    try:
        import qmlff  # noqa: F401
    except ImportError as exc:  # pragma: no cover - exercised via tests when qmlff present
        raise ImportError(
            "qmlff is not installed. Install the QML-FF project (sibling repo), e.g.:\n"
            "  pip install -e /path/to/QML-FF\n"
            "or set PYTHONPATH=/path/to/QML-FF before launching."
        ) from exc
    import qmlff as _q

    return _q


def _require_jax_md() -> Any:
    """Import jax_md lazily; raise a helpful error if unavailable."""
    try:
        import jax_md  # noqa: F401
    except ImportError as exc:  # pragma: no cover - exercised via tests when jax_md present
        raise ImportError(
            "jax-md is required for QML-FF MD simulations. Install with: pip install jax-md"
        ) from exc
    import jax_md as _jm

    return _jm


def atomic_number_to_symbol(z: int) -> str:
    """Best-effort Z → element-symbol lookup (returns ``'X'`` for unknown)."""
    return _Z_TO_SYMBOL.get(int(z), "X")


def symbol_to_atomic_number(sym: str) -> int:
    """Best-effort element-symbol → Z lookup (returns ``0`` for unknown)."""
    return _SYMBOL_TO_Z.get(str(sym), 0)


# ---------------------------------------------------------------------------
# Lightweight handle that bundles a QML-FF model with its bookkeeping
# ---------------------------------------------------------------------------


@dataclass
class QmlffModelHandle:
    """Opaque handle wrapping a QML-FF model + parameters + species table.

    Holding the raw ``qmlff`` model in a typed-only field keeps ``qchem_stack``
    importable when QML-FF is absent (the handle is only created inside
    ``build_qmlff_model_from_preset`` after a successful import).
    """

    model: Any
    params: dict[str, Any]
    species_list: list[str]
    preset_name: str = "atomic_amplitude"
    backend: ForceFieldBackend = "qmlff_preset"
    train_meta: dict[str, Any] = field(default_factory=dict)
    energy_norm_params: dict[str, Any] | None = None
    """QML-FF ``normalize_energies`` params; apply on predict when set."""
    opt_state: Any | None = None
    step: int = 0
    epoch: int = 0

    def species_indices(self, atomic_numbers: Sequence[int]) -> np.ndarray:
        """Map a list of Z to QML-FF ``species_list`` integer indices."""
        idx: list[int] = []
        for z in atomic_numbers:
            sym = atomic_number_to_symbol(int(z))
            if sym not in self.species_list:
                raise ValueError(
                    f"atomic_number {z} (symbol {sym!r}) not present in "
                    f"QML-FF species_list={self.species_list!r}; rebuild the model "
                    "with species_list covering all elements you will simulate."
                )
            idx.append(self.species_list.index(sym))
        return np.asarray(idx, dtype=np.int32)


# ---------------------------------------------------------------------------
# Build / train
# ---------------------------------------------------------------------------


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


def build_qmlff_model_angle(
    species_list: Sequence[str],
    *,
    preset: str = "atomic_amplitude",
    **builder_overrides: Any,
) -> QmlffModelHandle:
    """Atomic descriptor + **angle** encoding (more robust than amplitude on H2)."""
    _require_qmlff()
    from qmlff.api import ModelBuilder
    from qmlff.core.encoding.base import AngleEncoderConfig

    species_list = list(species_list)
    mod = __import__(f"qmlff.config.presets.{preset}", fromlist=["get_config"])
    config = mod.get_config(species_list=species_list, **builder_overrides)
    config.encoder = AngleEncoderConfig()
    model = ModelBuilder(config).build()
    params = model.get_parameters()
    return QmlffModelHandle(
        model=model,
        params={k: np.asarray(v) for k, v in params.items()},
        species_list=list(getattr(model, "species_list", species_list)),
        preset_name=f"{preset}_angle",
        backend="qmlff_angle",
    )


def build_qmp_h2_model(
    species_list: Sequence[str],
    qmp_overrides: dict[str, Any] | None = None,
) -> QmlffModelHandle:
    """QML-FF Schur Scheme B QMP path (H2-native equivariant architecture)."""
    _require_qmlff()
    import jax
    from qmlff.models import SchurSchemeBQMLFF, SchurSchemeBQMLFFConfig

    overrides = dict(qmp_overrides or {})
    species_list = list(species_list or ["H"])
    cfg = SchurSchemeBQMLFFConfig(**overrides)
    model = SchurSchemeBQMLFF(config=cfg, species_list=species_list)
    if not hasattr(model, "cutoff"):
        model.cutoff = float(cfg.cutoff)
    key = jax.random.PRNGKey(int(overrides.get("seed", cfg.seed)))
    params = model.init_params(key)
    model.set_parameters(params)
    return QmlffModelHandle(
        model=model,
        params={k: np.asarray(v) for k, v in params.items()},
        species_list=list(species_list),
        preset_name="qmp_h2_schur_b",
        backend="qmlff_qmp_h2",
    )


def build_qmlff_model_quantum_ff(
    species_list: Sequence[str],
    *,
    n_qubits: int = 5,
    n_layers: int = 4,
    cutoff: float = 6.0,
    encoding_type: str = "angle",
    **kwargs: Any,
) -> QmlffModelHandle:
    """QML-FF ``QuantumForceField`` — same class as ``h2_complete_workflow`` / ``train.py``."""
    _require_qmlff()
    from qmlff.models import QuantumForceField

    species_list = list(species_list or ["H"])
    model = QuantumForceField(
        n_qubits=int(n_qubits),
        n_layers=int(n_layers),
        cutoff=float(cutoff),
        species_list=species_list,
        encoding_type=str(encoding_type),
        **kwargs,
    )
    params = model.get_parameters()
    return QmlffModelHandle(
        model=model,
        params={k: np.asarray(v) for k, v in params.items()},
        species_list=list(species_list),
        preset_name="quantum_force_field",
        backend="qmlff_quantum",
    )


def build_force_field_handle(
    species_list: Sequence[str],
    *,
    backend: ForceFieldBackend = "qmlff_preset",
    preset: str = "atomic_amplitude",
    builder_overrides: dict[str, Any] | None = None,
    qmp_h2_overrides: dict[str, Any] | None = None,
) -> Any:
    """Dispatch to preset, angle, QMP-H2, or classical Morse backends."""
    overrides = dict(builder_overrides or {})
    if backend == "classical_h2":
        from qchem_stack.md_bridge.classical_h2_ff import build_classical_h2_handle

        return build_classical_h2_handle(species_list)
    if backend == "qmlff_angle":
        return build_qmlff_model_angle(species_list, preset=preset, **overrides)
    if backend == "qmlff_quantum":
        return build_qmlff_model_quantum_ff(species_list, **overrides)
    if backend == "qmlff_qmp_h2":
        return build_qmp_h2_model(species_list, qmp_h2_overrides)
    return build_qmlff_model_from_preset(species_list, preset=preset, **overrides)


def build_qmlff_model_from_preset(
    species_list: Sequence[str],
    *,
    preset: str = "atomic_amplitude",
    **builder_overrides: Any,
) -> QmlffModelHandle:
    """Construct a QML-FF model via ``qmlff.api.ModelBuilder.from_preset``.

    Args:
        species_list: ordered element symbols, e.g. ``["H", "O"]``.
        preset: ``atomic_amplitude`` | ``e3nn_chemical`` | ``equivariant``.
        builder_overrides: forwarded to the preset ``get_config(**overrides)``.

    Returns:
        :class:`QmlffModelHandle` with initial parameters from the model.
    """
    _require_qmlff()
    from qmlff.api import ModelBuilder

    species_list = list(species_list)
    if not species_list:
        raise ValueError("species_list must be non-empty (e.g. ['H'] for hydrogen)")

    builder = ModelBuilder.from_preset(preset, species_list=species_list, **builder_overrides)
    model = builder.build()

    if hasattr(model, "descriptor") and hasattr(model, "n_qubits"):
        _qdim = int(getattr(model.descriptor, "quantum_dim", 0))
        _max_amp = 2 ** int(model.n_qubits)
        if _qdim > _max_amp:
            raise ValueError(
                f"QML-FF preset {preset!r} needs at least {_qdim} amplitude dimensions "
                f"(descriptor quantum_dim={_qdim}, requires n_qubits>="
                f"{int(np.ceil(np.log2(_qdim)))}), but circuit n_qubits={model.n_qubits} "
                f"(max {_max_amp}). Increase qmlff_builder_overrides.n_qubits or shrink the "
                "descriptor (n_radial_basis / n_angular_basis)."
            )

    params = model.get_parameters()
    return QmlffModelHandle(
        model=model,
        params={k: np.asarray(v) for k, v in params.items()},
        species_list=list(getattr(model, "species_list", species_list)),
        preset_name=str(preset),
        backend="qmlff_preset",
    )


def train_force_field_on_qmef(
    handle: Any,
    dataset: QMEFDataset,
    *,
    n_epochs: int = 5,
    batch_size: int = 1,
    learning_rate: float = 1e-3,
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
    learning_rate: float = 1e-3,
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


# ---------------------------------------------------------------------------
# Inference (single geometry)
# ---------------------------------------------------------------------------


def predict_energy_forces_hartree(
    handle: QmlffModelHandle,
    *,
    positions_bohr: np.ndarray,
    atomic_numbers: Sequence[int],
    box_bohr: np.ndarray | None = None,
) -> tuple[float, np.ndarray]:
    """QML-FF prediction returned in qchem-native units (Hartree, Hartree/Bohr).

    Args:
        handle: model handle from :func:`build_qmlff_model_from_preset` /
            :func:`train_qmlff_on_qmef`.
        positions_bohr: ``(N, 3)`` array, Bohr.
        atomic_numbers: length-``N`` sequence of atomic numbers ``Z``.
        box_bohr: optional ``(3,)`` or ``(3,3)`` box for PBC, Bohr.

    Returns:
        ``(energy_hartree, forces_hartree_per_bohr)`` — Python ``float`` and
        ``np.ndarray`` of shape ``(N, 3)``.
    """
    backend = getattr(handle, "backend", "qmlff_preset")
    if backend != "classical_h2":
        _require_qmlff()
    import jax.numpy as jnp

    species_idx = handle.species_indices(atomic_numbers)
    positions_ang = np.asarray(positions_bohr, dtype=np.float64) * _BOHR_TO_ANGSTROM
    box_ang = None
    if box_bohr is not None:
        box_ang = np.asarray(box_bohr, dtype=np.float64) * _BOHR_TO_ANGSTROM

    pos_j = jnp.asarray(positions_ang)
    spec_j = jnp.asarray(species_idx)
    box_j = jnp.asarray(box_ang) if box_ang is not None else None

    e_ev = float(handle.model.compute_total_energy(pos_j, spec_j, handle.params, box=box_j))
    f_ev_ang = np.asarray(
        handle.model.compute_forces(pos_j, spec_j, handle.params, box=box_j),
        dtype=np.float64,
    )

    norm_params = handle.energy_norm_params or handle.train_meta.get("energy_norm_params")
    e_ev = _denormalize_energy_ev(
        e_ev,
        n_atoms=len(atomic_numbers),
        norm_params=norm_params,
    )
    e_hartree = e_ev / _HARTREE_TO_EV
    f_hb = f_ev_ang / _HARTREE_BOHR_TO_EV_ANG
    return float(e_hartree), f_hb


# ---------------------------------------------------------------------------
# JAX-MD trajectory
# ---------------------------------------------------------------------------


@dataclass
class JaxMdTrajectory:
    """Container for the output of :func:`run_jaxmd_trajectory` (Bohr/Hartree)."""

    positions_bohr: list[np.ndarray]
    """Saved frames, each ``(N, 3)`` in Bohr."""
    energies_hartree: list[float]
    """One QML-FF predicted energy per saved frame (Hartree)."""
    temperatures_K: list[float]
    """Instantaneous kinetic temperature per saved frame (K)."""
    times_ps: list[float]
    """Wall-clock simulation time per saved frame (ps)."""
    atomic_numbers: list[int]
    """Element Z list, length-``N`` (constant across the run)."""
    meta: dict[str, Any] = field(default_factory=dict)
    """Free-form bookkeeping: dt, ensemble, seed, n_steps, output_freq …"""


def run_jaxmd_trajectory(
    handle: QmlffModelHandle,
    *,
    initial_positions_bohr: np.ndarray,
    atomic_numbers: Sequence[int],
    n_steps: int,
    dt_fs: float = 0.5,
    temperature_K: float = 300.0,
    ensemble: str = "nvt_langevin",
    save_stride: int = 10,
    seed: int = 42,
    masses_amu: Sequence[float] | None = None,
    box_bohr: np.ndarray | None = None,
    gamma_ps_inv: float = 0.1,
    tau_fs: float = 100.0,
    cutoff_ang: float | None = None,
    max_neighbors: int = 64,
) -> JaxMdTrajectory:
    """Run a JAX-MD trajectory on ``handle.model``; return frames in Bohr/Hartree.

    Args:
        handle: trained QML-FF model handle.
        initial_positions_bohr: ``(N, 3)`` starting geometry (Bohr).
        atomic_numbers: length-``N`` Z list (constant for the run).
        n_steps: total MD steps.
        dt_fs: time step, **femtoseconds** (JAX-MD convention).
        temperature_K: target temperature.
        ensemble: ``nvt_langevin`` | ``nvt_nose_hoover`` | ``nve``.
        save_stride: emit a frame every N MD steps (also drives logging).
        seed: PRNG seed for thermostats / initial velocities.
        masses_amu: optional per-atom mass in amu; defaults to standard table.
        box_bohr: optional simulation box (``(3,)`` orthorhombic or ``(3,3)``).
        gamma_ps_inv / tau_fs: Langevin / Nosé-Hoover knobs.
        cutoff_ang: neighbor-list cutoff in Å (defaults to ``handle.model.cutoff``).
        max_neighbors: neighbor-list capacity per atom.

    Returns:
        :class:`JaxMdTrajectory` — positions in **Bohr**, energies in **Hartree**.
    """
    backend = getattr(handle, "backend", "qmlff_preset")
    if backend != "classical_h2":
        _require_qmlff()
    _require_jax_md()
    import jax.numpy as jnp
    from qmlff.simulation.jaxmd_integration import JAXMDSimulator

    pos_bohr = np.asarray(initial_positions_bohr, dtype=np.float64)
    if pos_bohr.ndim != 2 or pos_bohr.shape[1] != 3:
        raise ValueError(f"initial_positions_bohr must have shape (N, 3); got {pos_bohr.shape!r}")
    n_atoms = pos_bohr.shape[0]
    if len(atomic_numbers) != n_atoms:
        raise ValueError(f"atomic_numbers length ({len(atomic_numbers)}) must match N={n_atoms}")

    species_idx = handle.species_indices(atomic_numbers)
    pos_ang = pos_bohr * _BOHR_TO_ANGSTROM
    box_ang = None
    if box_bohr is not None:
        box_ang = np.asarray(box_bohr, dtype=np.float64) * _BOHR_TO_ANGSTROM

    if masses_amu is None:
        from qmlff.simulation.md_simulation import get_atomic_masses

        masses_amu = np.asarray(
            get_atomic_masses(jnp.asarray(species_idx), handle.species_list),
            dtype=np.float64,
        )
    else:
        masses_amu = np.asarray(masses_amu, dtype=np.float64)
        if masses_amu.shape != (n_atoms,):
            raise ValueError(f"masses_amu must have shape ({n_atoms},); got {masses_amu.shape!r}")

    sim = JAXMDSimulator(
        model=handle.model,
        box=jnp.asarray(box_ang) if box_ang is not None else None,
        species=jnp.asarray(species_idx),
        dt=float(dt_fs),
        cutoff=_model_cutoff_ang(handle.model, cutoff_ang),
        max_neighbors=int(max_neighbors),
    )

    ens = ensemble.lower()
    if ens == "nve":
        # NVE needs initial velocities; sample Maxwell-Boltzmann at T.
        import jax

        kB = 8.617333e-5  # eV/K
        kT = kB * float(temperature_K)
        key = jax.random.PRNGKey(int(seed))
        sigma = jnp.sqrt(kT / jnp.asarray(masses_amu)[:, None])
        v0 = sigma * jax.random.normal(key, (n_atoms, 3))
        result = sim.run_nve(
            initial_positions=jnp.asarray(pos_ang),
            initial_velocities=v0,
            n_steps=int(n_steps),
            output_freq=int(save_stride),
            masses=jnp.asarray(masses_amu),
            temperature=float(temperature_K),
        )
    elif ens in {"nvt_langevin", "langevin"}:
        result = sim.run_nvt(
            initial_positions=jnp.asarray(pos_ang),
            temperature=float(temperature_K),
            n_steps=int(n_steps),
            output_freq=int(save_stride),
            masses=jnp.asarray(masses_amu),
            thermostat="langevin",
            gamma=float(gamma_ps_inv),
            seed=int(seed),
        )
    elif ens in {"nvt_nose_hoover", "nose_hoover", "nvt"}:
        result = sim.run_nvt(
            initial_positions=jnp.asarray(pos_ang),
            temperature=float(temperature_K),
            n_steps=int(n_steps),
            output_freq=int(save_stride),
            masses=jnp.asarray(masses_amu),
            thermostat="nose_hoover",
            tau=float(tau_fs),
            seed=int(seed),
        )
    else:
        raise ValueError(
            f"Unknown ensemble {ensemble!r}; expected one of nve | nvt_langevin | nvt_nose_hoover"
        )

    traj_ang = np.asarray(result["trajectory"], dtype=np.float64)
    energies_ev = np.asarray(result["energies"], dtype=np.float64)
    temps_K = np.asarray(result.get("temperatures", np.zeros_like(energies_ev)), dtype=np.float64)

    n_frames = traj_ang.shape[0]
    times_ps = [float(i) * float(save_stride) * float(dt_fs) * 1e-3 for i in range(n_frames)]

    return JaxMdTrajectory(
        positions_bohr=[
            (traj_ang[i] / _BOHR_TO_ANGSTROM).astype(np.float64) for i in range(n_frames)
        ],
        energies_hartree=[float(e / _HARTREE_TO_EV) for e in energies_ev.tolist()],
        temperatures_K=[float(t) for t in temps_K.tolist()],
        times_ps=times_ps,
        atomic_numbers=[int(z) for z in atomic_numbers],
        meta={
            "ensemble": ens,
            "dt_fs": float(dt_fs),
            "n_steps": int(n_steps),
            "save_stride": int(save_stride),
            "temperature_K": float(temperature_K),
            "seed": int(seed),
            "n_atoms": int(n_atoms),
            "box_bohr": (None if box_bohr is None else np.asarray(box_bohr).tolist()),
        },
    )


# ---------------------------------------------------------------------------
# Convenience: trajectory → list of geometries to label
# ---------------------------------------------------------------------------


def select_geometries_from_trajectory(
    traj: JaxMdTrajectory,
    *,
    n_candidates: int,
    skip_initial: bool = True,
) -> list[list[list[float]]]:
    """Pick up to ``n_candidates`` geometries (Bohr) evenly spaced over the trajectory.

    Returns a ``list[list[list[float]]]`` shaped ``(n, n_atom, 3)`` — exactly the
    format accepted by :func:`qchem_stack.config.md_ml_export.MdMlTrajectorySpec.extra_coordinates_bohr`.
    """
    if n_candidates <= 0:
        raise ValueError("n_candidates must be >= 1")
    start = 1 if (skip_initial and len(traj.positions_bohr) > 1) else 0
    frames = traj.positions_bohr[start:]
    if not frames:
        return []
    if len(frames) <= n_candidates:
        chosen = frames
    else:
        idx = np.linspace(0, len(frames) - 1, n_candidates, dtype=int)
        chosen = [frames[int(i)] for i in idx]
    out: list[list[list[float]]] = []
    for arr in chosen:
        a = np.asarray(arr, dtype=np.float64)
        out.append([[float(a[i, 0]), float(a[i, 1]), float(a[i, 2])] for i in range(a.shape[0])])
    return out


def trajectory_to_extxyz(traj: JaxMdTrajectory, path: str | Path) -> None:
    """Dump a :class:`JaxMdTrajectory` as Bohr/Hartree extended XYZ for inspection."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for i, (pos, e) in enumerate(zip(traj.positions_bohr, traj.energies_hartree, strict=False)):
        n = pos.shape[0]
        lines.append(str(n))
        lines.append(
            f"frame={i} time_ps={traj.times_ps[i]:.6f} "
            f"energy_hartree={e:.10f} "
            f"Properties=species:S:1:pos_bohr:R:3"
        )
        for z, r in zip(traj.atomic_numbers, pos, strict=False):
            sym = atomic_number_to_symbol(int(z))
            lines.append(f"{sym} {r[0]:.8f} {r[1]:.8f} {r[2]:.8f}")
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")


def qmlff_handle_to_qmef_frame(
    handle: QmlffModelHandle,
    *,
    positions_bohr: np.ndarray,
    atomic_numbers: Sequence[int],
    method_tag: str = "qmlff_prediction",
) -> dict[str, Any]:
    """Build a :class:`QMFrame`-shaped dict from a QML-FF prediction.

    Useful for: debugging next to the qchem reference, or piping into
    :meth:`QMEFDataset` for round-trip exports.
    """
    if not handle.params:
        raise PipelineError("QML-FF handle has no parameters; call train_qmlff_on_qmef first")
    e_hartree, forces_hb = predict_energy_forces_hartree(
        handle,
        positions_bohr=positions_bohr,
        atomic_numbers=atomic_numbers,
    )
    pos_arr = np.asarray(positions_bohr, dtype=np.float64)
    return {
        "atomic_numbers": [int(z) for z in atomic_numbers],
        "positions_bohr": [
            [float(pos_arr[i, 0]), float(pos_arr[i, 1]), float(pos_arr[i, 2])]
            for i in range(pos_arr.shape[0])
        ],
        "energy_hartree": float(e_hartree),
        "forces_hartree_bohr": forces_hb.tolist(),
        "method_tag": method_tag,
        "active_space_hash": "",
        "protocol_hash": "",
        "repro_config_sha256_prefix": "",
        "backend_noise_tag": "qmlff",
    }


__all__ = [
    "ForceFieldBackend",
    "QmlffModelHandle",
    "JaxMdTrajectory",
    "build_force_field_handle",
    "build_qmlff_model_from_preset",
    "build_qmlff_model_quantum_ff",
    "build_qmlff_model_angle",
    "build_qmp_h2_model",
    "train_force_field_on_qmef",
    "train_qmlff_on_qmef",
    "predict_energy_forces_hartree",
    "run_jaxmd_trajectory",
    "select_geometries_from_trajectory",
    "trajectory_to_extxyz",
    "qmlff_handle_to_qmef_frame",
    "atomic_number_to_symbol",
    "symbol_to_atomic_number",
]
