#!/usr/bin/env python3
"""Long QML-FF H2 MD for OVITO: ~2h wall budget → ~1e5 steps, 50 saved frames.

Design goals
------------
- Keep **COM motion** (no per-frame centering) so Brownian / translation is visible.
- Target thermostat **300 K**, NVT-Langevin, dt=0.25 fs.
- Save exactly **50 frames** (evenly spaced) for OVITO.
- Wall budget ≈ 2 hours on CPU (measured ~17 steps/s for 2-atom H2 QML-FF).

Default schedule (~2 h CPU, 10×H2 **cubic** box, COM preserved)::

    n_mol        = 10
    n_steps      = 10_000      per molecule  (~2.5 ps @ dt=0.25 fs)
    save_stride  = 200         → 50 frames
    temperature  = 300 K
    box          = (22.5, 22.5, 22.5) Bohr  ≈ 11.9 Å cube (3×3×3 lattice)

Longer single-molecule run (~2 h)::

    .venv/bin/python docs/assets/run_qmlff_md_long_ovito.py --n-mol 1 --n-steps 100000
    # → 25 ps, stride=2000, 50 frames

Outputs
-------
- ``results/qmlff_md_long_ovito/h2_qmlff_md_long.extxyz``  (Å + Lattice, OVITO)
- ``results/qmlff_md_long_ovito/run_meta.json``
- optional PNG strip if ``--plot``

Usage::

    cd /home/sunhl/projects/qchem_qml_md
    .venv/bin/python docs/assets/run_qmlff_md_long_ovito.py
    # or shorter smoke:
    .venv/bin/python docs/assets/run_qmlff_md_long_ovito.py --n-steps 4000 --save-frames 50
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

BOHR_A = 0.529177210903
DEFAULT_CKPT = (
    ROOT / "results/uqc_cloud_sim_md_ml_optimized/qmlff_checkpoints/round_05/final.npz"
)
OUT_DIR = ROOT / "results/qmlff_md_long_ovito"


def _load_handle(ckpt: Path):
    from qchem_stack.md_bridge import build_force_field_handle

    handle = build_force_field_handle(["H"], backend="qmlff_preset", preset="atomic_amplitude")
    data = {k: np.asarray(v) for k, v in np.load(ckpt, allow_pickle=True).items()}
    handle.model.set_parameters(data)
    handle.params = data
    return handle


def _rot(rng: np.random.Generator) -> np.ndarray:
    u1, u2, u3 = rng.random(3)
    q = np.array(
        [
            np.sqrt(1 - u1) * np.sin(2 * np.pi * u2),
            np.sqrt(1 - u1) * np.cos(2 * np.pi * u2),
            np.sqrt(u1) * np.sin(2 * np.pi * u3),
            np.sqrt(u1) * np.cos(2 * np.pi * u3),
        ]
    )
    w, x, y, z = q
    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ]
    )


def _pack_centers(n_mol: int, spacing: float = 7.5) -> tuple[np.ndarray, np.ndarray]:
    """Cubic (square) box packing: Lx = Ly = Lz.

    Places molecules on a cubic lattice ``n×n×n`` with ``n = ceil(n_mol**(1/3))``.
    For default 10×H2 and spacing=7.5 Bohr → box = (22.5, 22.5, 22.5) Bohr.
    """
    n = int(np.ceil(n_mol ** (1.0 / 3.0)))
    while n**3 < n_mol:
        n += 1
    centers = []
    for i in range(n_mol):
        ix = i % n
        iy = (i // n) % n
        iz = i // (n * n)
        centers.append([(ix + 0.5) * spacing, (iy + 0.5) * spacing, (iz + 0.5) * spacing])
    L = float(n * spacing)
    box = np.array([L, L, L], float)
    return np.asarray(centers), box


def _write_ovito_extxyz(
    path: Path,
    frames_bohr: list[np.ndarray],
    energies: list[float],
    times_ps: list[float],
    box_bohr: np.ndarray,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    box_a = box_bohr * BOHR_A
    Lx, Ly, Lz = box_a
    lattice = f"{Lx:.8f} 0 0 0 {Ly:.8f} 0 0 0 {Lz:.8f}"
    lines: list[str] = []
    for fi, (pos_b, e, t) in enumerate(zip(frames_bohr, energies, times_ps)):
        pos = np.asarray(pos_b, float) * BOHR_A
        # wrap into box for OVITO display (orthogonal)
        pos = pos % box_a
        n = pos.shape[0]
        lines.append(str(n))
        lines.append(
            f'Lattice="{lattice}" Properties=species:S:1:pos:R:3 '
            f"energy={e:.10f} time_ps={t:.8f} frame={fi} pbc=\"T T T\" "
            f'comment="QML-FF long MD; units=Angstrom; COM preserved"'
        )
        for p in pos:
            lines.append(f"H {p[0]:.8f} {p[1]:.8f} {p[2]:.8f}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ckpt", type=Path, default=DEFAULT_CKPT)
    ap.add_argument("--n-steps", type=int, default=10_000, help="MD steps per molecule. 10k×10mol≈2h CPU; 100k×1mol≈2h.")
    ap.add_argument("--save-frames", type=int, default=50, help="Number of frames to keep.")
    ap.add_argument("--dt-fs", type=float, default=0.25)
    ap.add_argument("--temperature-K", type=float, default=300.0)
    ap.add_argument("--n-mol", type=int, default=10, help="1 = single H2; 10 = box of 10 (default).")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = ap.parse_args()

    if not args.ckpt.exists():
        raise SystemExit(f"checkpoint missing: {args.ckpt}")

    save_stride = max(1, args.n_steps // args.save_frames)
    # adjust n_steps so we get exactly save_frames frames from run_jaxmd
    n_steps = save_stride * args.save_frames
    sim_ps = n_steps * args.dt_fs / 1000.0

    print("=== QML-FF long MD ===")
    print(f"ckpt          : {args.ckpt}")
    print(f"n_steps       : {n_steps}")
    print(f"save_stride   : {save_stride}  → {args.save_frames} frames")
    print(f"dt_fs         : {args.dt_fs}  → sim_time {sim_ps:.2f} ps")
    print(f"T             : {args.temperature_K} K  NVT-Langevin")
    print(f"n_mol         : {args.n_mol}  (COM preserved)")
    print(f"out           : {args.out_dir}")

    handle = _load_handle(args.ckpt)
    from qchem_stack.md_bridge import run_jaxmd_trajectory

    bond = 1.401
    pos0 = np.array([[-bond / 2, 0.0, 0.0], [bond / 2, 0.0, 0.0]], float)
    centers, box_bohr = _pack_centers(args.n_mol)
    print(f"box_bohr      : {box_bohr.tolist()}  (cubic / square)")
    print(f"box_angstrom  : {(box_bohr * BOHR_A).tolist()}")
    rng = np.random.default_rng(args.seed)
    rots = [_rot(rng) for _ in range(args.n_mol)]

    t0 = time.time()
    mol_trajs = []
    for m in range(args.n_mol):
        print(f"\n--- molecule {m + 1}/{args.n_mol} ---")
        # slight initial COM kick so each mol starts with different phase
        kick = rng.normal(0.0, 0.02, size=(2, 3))  # Bohr
        init = pos0 + kick
        traj = run_jaxmd_trajectory(
            handle,
            initial_positions_bohr=init,
            atomic_numbers=[1, 1],
            n_steps=n_steps,
            dt_fs=args.dt_fs,
            temperature_K=args.temperature_K,
            ensemble="nvt_langevin",
            save_stride=save_stride,
            seed=args.seed + m,
            box_bohr=None,
            max_neighbors=16,
        )
        mol_trajs.append(traj)
        print(
            f"  frames={len(traj.positions_bohr)}  "
            f"T_mean={float(np.mean(traj.temperatures_K)):.1f}K  "
            f"bond0={np.linalg.norm(traj.positions_bohr[0][0]-traj.positions_bohr[0][1]):.3f}  "
            f"bond-1={np.linalg.norm(traj.positions_bohr[-1][0]-traj.positions_bohr[-1][1]):.3f}"
        )

    # Compose box frames: KEEP COM relative to each molecule's starting lattice site
    # COM drift = (frame_com - frame0_com) added on top of lattice center
    n_f = min(len(t.positions_bohr) for t in mol_trajs)
    frames = []
    energies = []
    times = []
    for fi in range(n_f):
        pos_all = []
        e_sum = 0.0
        for m, traj in enumerate(mol_trajs):
            local = np.asarray(traj.positions_bohr[fi], float)
            com = local.mean(axis=0)
            # orientation fixed by initial rotation of relative coords around instantaneous COM
            rel = (local - com) @ rots[m].T
            # place at lattice + COM displacement from start (Brownian of each mol)
            com0 = np.asarray(traj.positions_bohr[0], float).mean(axis=0)
            drift = (com - com0) @ rots[m].T
            pos_all.append(rel + centers[m] + drift)
            e_sum += float(traj.energies_hartree[fi])
        frames.append(np.vstack(pos_all))
        energies.append(e_sum)
        times.append(float(mol_trajs[0].times_ps[fi]))

    out_xyz = args.out_dir / "h2_qmlff_md_long.extxyz"
    _write_ovito_extxyz(out_xyz, frames, energies, times, box_bohr)

    elapsed = time.time() - t0
    steps_per_s = (n_steps * args.n_mol) / max(elapsed, 1e-6)
    meta = {
        "ckpt": str(args.ckpt),
        "n_steps": n_steps,
        "save_stride": save_stride,
        "n_frames": n_f,
        "dt_fs": args.dt_fs,
        "sim_time_ps": sim_ps,
        "temperature_K": args.temperature_K,
        "n_mol": args.n_mol,
        "box_bohr": box_bohr.tolist(),
        "box_angstrom": (box_bohr * BOHR_A).tolist(),
        "box_shape": "cubic",
        "wall_seconds": elapsed,
        "steps_per_second": steps_per_s,
        "out_extxyz": str(out_xyz),
        "note": "COM drift preserved; cubic lattice packing for OVITO",
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "run_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("\n=== done ===")
    print(json.dumps(meta, indent=2))
    print(f"OVITO file: {out_xyz}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
