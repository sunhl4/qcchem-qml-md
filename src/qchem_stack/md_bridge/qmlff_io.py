"""QML-FF trajectory and frame I/O helpers."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.exceptions import PipelineError
from qchem_stack.md_bridge.qmlff_builders import (
    QmlffModelHandle,
    atomic_number_to_symbol,
)
from qchem_stack.md_bridge.qmlff_md import (
    JaxMdTrajectory,
    predict_energy_forces_hartree,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


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
