"""QML-FF inference and JAX-MD trajectory helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.md_bridge.qmlff_builders import (
    QmlffModelHandle,
    _require_qmlff,
)
from qchem_stack.md_bridge.qmlff_training import (
    _denormalize_energy_ev,
    _model_cutoff_ang,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

_BOHR_TO_ANGSTROM = 0.529177210903
_HARTREE_TO_EV = 27.211386245988
_HARTREE_BOHR_TO_EV_ANG = _HARTREE_TO_EV / _BOHR_TO_ANGSTROM


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

        masses_arr = np.asarray(
            get_atomic_masses(jnp.asarray(species_idx), handle.species_list),
            dtype=np.float64,
        )
    else:
        masses_arr = np.asarray(masses_amu, dtype=np.float64)
        if masses_arr.shape != (n_atoms,):
            raise ValueError(f"masses_amu must have shape ({n_atoms},); got {masses_arr.shape!r}")

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
        sigma = jnp.sqrt(kT / jnp.asarray(masses_arr)[:, None])
        v0 = sigma * jax.random.normal(key, (n_atoms, 3))
        result = sim.run_nve(
            initial_positions=jnp.asarray(pos_ang),
            initial_velocities=v0,
            n_steps=int(n_steps),
            output_freq=int(save_stride),
            masses=jnp.asarray(masses_arr),
            temperature=float(temperature_K),
        )
    elif ens in {"nvt_langevin", "langevin"}:
        result = sim.run_nvt(
            initial_positions=jnp.asarray(pos_ang),
            temperature=float(temperature_K),
            n_steps=int(n_steps),
            output_freq=int(save_stride),
            masses=jnp.asarray(masses_arr),
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
            masses=jnp.asarray(masses_arr),
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
