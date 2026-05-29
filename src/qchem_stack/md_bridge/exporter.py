from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from qchem_stack.md_bridge.schema import QMEFDataset


def export_extended_xyz(dataset: QMEFDataset, path: str | Path) -> None:
    """Extended XYZ with energy/forces in comment line (minimal)."""
    p = Path(path)
    lines: list[str] = []
    for fr in dataset.frames:
        n = len(fr.atomic_numbers)
        lines.append(str(n))
        lines.append(
            f"energy={fr.energy_hartree:.10f} "
            f"Properties=species:S:1:pos:R:3:forces:R:3 "
            f"charge={fr.charge} mult={fr.multiplicity} method={fr.method_tag}"
        )
        for z, r, f in zip(
            fr.atomic_numbers,
            fr.positions_bohr,
            fr.forces_hartree_bohr if fr.forces_hartree_bohr else [[0.0, 0.0, 0.0]] * n,
            strict=False,
        ):
            sym = {1: "H", 6: "C", 7: "N", 8: "O"}.get(int(z), "X")
            lines.append(f"{sym} {r[0]:.8f} {r[1]:.8f} {r[2]:.8f} {f[0]:.8f} {f[1]:.8f} {f[2]:.8f}")
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_hdf5_stub(dataset: QMEFDataset, path: str | Path) -> None:
    """Write numpy NPZ when h5py is absent (drop-in stub)."""
    p = Path(path).with_suffix(".npz")
    zs, rs, es, fs = [], [], [], []
    for fr in dataset.frames:
        zs.append(fr.atomic_numbers)
        rs.append(fr.positions_bohr)
        es.append(fr.energy_hartree)
        frc = fr.forces_hartree_bohr or [[0.0, 0.0, 0.0]] * len(fr.atomic_numbers)
        fs.append(frc)
    np.savez_compressed(
        p,
        Z=np.array(zs, dtype=int),
        R=np.array(rs, dtype=float),
        E=np.array(es, dtype=float),
        F=np.array(fs, dtype=float),
        provenance=np.array([dataset.provenance_yaml], dtype=object),
    )
