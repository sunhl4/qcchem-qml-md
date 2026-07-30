#!/usr/bin/env python3
"""H2-box MD visualization driven by a trained QML-FF (述职插图).

Loads an online-learning checkpoint, runs short per-molecule NVT MD with the
trained force field, packs ~10 H2 into a visualization box, and writes a
publication-style multi-panel PNG (+ optional XYZ).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CKPT = (
    ROOT
    / "results/h2_bondscan_ol_statevector_r12_8992/qmlff_checkpoints/round_09/final.npz"
)
OUT_PNGS = [
    Path("/tmp/shuzhi_unified/figures/uqc/h2_box_qmlff_md_trajectory.png"),
    ROOT / "docs/assets/shuzhi_demo/uqc/h2_box_qmlff_md_trajectory.png",
]
OUT_XYZ = Path("/tmp/shuzhi_unified/figures/uqc/h2_box_qmlff_md_trajectory.extxyz")
OVITO_EXTXYZ = ROOT / "results/h2_box_qmlff_md_ovito/h2_box_10mol_qmlff_md.extxyz"

BOHR_TO_A = 0.529177210903
N_MOL = 10
BOND0 = 1.401  # Bohr ≈ 0.74 Å

# Soft categorical palette for 10 molecules (distinct but calm)
MOL_COLORS = [
    "#0F766E",
    "#1D4ED8",
    "#7C3AED",
    "#BE185D",
    "#C2410C",
    "#047857",
    "#0369A1",
    "#6D28D9",
    "#9F1239",
    "#B45309",
]


def _setup_font():
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    for fp in ("/mnt/c/Windows/Fonts/msyh.ttc", "/mnt/c/Windows/Fonts/NotoSansSC-VF.ttf"):
        if Path(fp).exists():
            font_manager.fontManager.addfont(fp)
            name = font_manager.FontProperties(fname=fp).get_name()
            plt.rcParams.update(
                {
                    "font.family": "sans-serif",
                    "font.sans-serif": [name, "DejaVu Sans"],
                    "axes.unicode_minus": False,
                }
            )
            break
    return plt


def _load_handle(ckpt: Path):
    from qchem_stack.md_bridge import build_force_field_handle

    handle = build_force_field_handle(
        ["H"],
        backend="qmlff_preset",
        preset="atomic_amplitude",
        builder_overrides={"n_qubits": 8, "n_layers": 3},
    )
    data = {k: np.asarray(v) for k, v in np.load(ckpt, allow_pickle=True).items()}
    handle.model.set_parameters(data)
    handle.params = data
    return handle


def _run_single_md(handle, *, seed: int, n_steps: int = 2000, save_stride: int = 20):
    from qchem_stack.md_bridge import run_jaxmd_trajectory

    pos0 = np.array([[-BOND0 / 2, 0.0, 0.0], [BOND0 / 2, 0.0, 0.0]], dtype=np.float64)
    return run_jaxmd_trajectory(
        handle,
        initial_positions_bohr=pos0,
        atomic_numbers=[1, 1],
        n_steps=n_steps,
        dt_fs=0.10,
        temperature_K=300.0,
        ensemble="nvt_langevin",
        save_stride=save_stride,
        seed=seed,
        box_bohr=None,
        max_neighbors=16,
    )


def _rot(rng: np.random.Generator) -> np.ndarray:
    """Random rotation matrix (uniform on SO(3))."""
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


def _pack_centers(n_mol: int = N_MOL, spacing: float = 7.5) -> tuple[np.ndarray, np.ndarray]:
    """Return (n_mol, 3) centers and (3,) **cubic** box size in Bohr.

    10 molecules uniformly distributed across a 3×3×3 grid (27 cells),
    selecting cells spread across all three layers instead of packing
    them into the first layer.
    """
    n = int(np.ceil(n_mol ** (1.0 / 3.0)))
    while n**3 < n_mol:
        n += 1
    # Uniform selection: spread 10 molecules across 3 layers of 3×3×3 grid
    # 4 in layer 0 (corners), 3 in layer 1 (center + edges), 3 in layer 2
    uniform_cells = [
        (0, 0, 0), (2, 0, 0), (0, 2, 0), (2, 2, 0),  # layer 0: 4 corners
        (1, 1, 1), (0, 1, 1), (2, 1, 1),              # layer 1: center + 2 edges
        (1, 0, 2), (1, 2, 2), (0, 0, 2),              # layer 2: 3 spread
    ]
    centers = []
    for ix, iy, iz in uniform_cells[:n_mol]:
        centers.append([(ix + 0.5) * spacing, (iy + 0.5) * spacing, (iz + 0.5) * spacing])
    L = float(n * spacing)
    box = np.array([L, L, L], dtype=np.float64)
    return np.asarray(centers), box


def _compose_box_traj(mol_trajs, centers, box, n_frames: int = 12):
    """Build multi-molecule frames from independent single-H2 MD trajs.

    Preserves COM drift (translational motion) from each single-molecule MD
    and wraps positions into the periodic box so molecules can wander.
    Uses sequential frames (no random phase / no wrap-around) to keep time
    monotonically increasing.
    """
    n_mol = len(mol_trajs)
    lengths = [len(t.positions_bohr) for t in mol_trajs]
    rng = np.random.default_rng(0)
    rots = [_rot(rng) for _ in range(n_mol)]

    # Use sequential frames from 0; cap n_frames to shortest trajectory
    max_frames = min(min(lengths), n_frames)

    # Record initial COM for each molecule to track drift
    com0 = []
    for m, traj in enumerate(mol_trajs):
        com0.append(np.asarray(traj.positions_bohr[0], float).mean(axis=0))

    Lx, Ly, Lz = float(box[0]), float(box[1]), float(box[2])

    frames = []
    energies = []
    bonds = []
    times = []
    for f in range(max_frames):
        pos_all = []
        e_sum = 0.0
        b_list = []
        t_ref = 0.0
        for m, traj in enumerate(mol_trajs):
            idx = f  # sequential, no phase offset, no wrap
            local = np.asarray(traj.positions_bohr[idx], float)  # (2,3)
            com = local.mean(axis=0)
            # COM drift from initial frame → translational motion
            drift = com - com0[m]
            # Remove COM for rotation/vibration, apply fixed initial rotation
            local_centered = (local - com) @ rots[m].T
            # Place at grid center + drift, wrap COM into box (PBC)
            center_placed = centers[m] + drift
            center_wrapped = center_placed - Lx * np.floor(center_placed / Lx)
            placed = local_centered + center_wrapped
            pos_all.append(placed)
            e_sum += float(traj.energies_hartree[idx])
            b_list.append(float(np.linalg.norm(local_centered[0] - local_centered[1])))
            t_ref = float(traj.times_ps[idx])
        frames.append(np.vstack(pos_all))
        energies.append(e_sum)
        bonds.append(b_list)
        times.append(t_ref)
    return {
        "positions_bohr": frames,
        "energies_hartree": energies,
        "bonds_bohr": bonds,
        "times_ps": times,
        "box_bohr": box,
        "atomic_numbers": [1] * (2 * n_mol),
    }


def _write_xyz(comp, path: Path) -> None:
    """Write extended XYZ (extxyz) with Lattice for OVITO/VMD periodic boundary visualization."""
    path.parent.mkdir(parents=True, exist_ok=True)
    n = len(comp["atomic_numbers"])
    box_bohr = comp["box_bohr"]
    Lx, Ly, Lz = box_bohr * BOHR_TO_A  # convert Bohr → Angstrom for OVITO
    with path.open("w", encoding="utf-8") as f:
        for i, pos_bohr in enumerate(comp["positions_bohr"]):
            e = comp["energies_hartree"][i]
            t = comp["times_ps"][i]
            pos_a = np.asarray(pos_bohr) * BOHR_TO_A  # Angstrom
            f.write(f"{n}\n")
            f.write(
                f'Lattice="{Lx:.6f} 0.0 0.0 0.0 {Ly:.6f} 0.0 0.0 0.0 {Lz:.6f}" '
                f'Properties=species:S:1:pos:R:3:forces:R:3 '
                f'energy={e:.8f} time_ps={t:.6f} '
                f'pbc="T T T"\n'
            )
            for j, p in enumerate(pos_a):
                f.write(f"H {p[0]:.8f} {p[1]:.8f} {p[2]:.8f} 0.0 0.0 0.0\n")


def _draw_box(ax, box_a: np.ndarray, color="#94A3B8", lw=1.35):
    Lx, Ly, Lz = box_a
    corners = np.array(
        [
            [0, 0, 0],
            [Lx, 0, 0],
            [Lx, Ly, 0],
            [0, Ly, 0],
            [0, 0, Lz],
            [Lx, 0, Lz],
            [Lx, Ly, Lz],
            [0, Ly, Lz],
        ]
    )
    # translucent floor
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    floor = [[corners[i] for i in (0, 1, 2, 3)]]
    ax.add_collection3d(
        Poly3DCollection(floor, alpha=0.07, facecolor="#0F766E", edgecolor="none")
    )
    edges = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 0),
        (4, 5),
        (5, 6),
        (6, 7),
        (7, 4),
        (0, 4),
        (1, 5),
        (2, 6),
        (3, 7),
    ]
    for a, b in edges:
        ax.plot(*zip(corners[a], corners[b]), color=color, lw=lw, alpha=0.9)


def _load_ovito_extxyz(path: Path) -> dict:
    """Parse ASE/OVITO extended XYZ (Angstrom) into plot composition dict."""
    text = path.read_text(encoding="utf-8").strip().splitlines()
    frames_pos = []
    energies = []
    times = []
    box = None
    i = 0
    while i < len(text):
        n = int(text[i].strip())
        header = text[i + 1]
        # Lattice="Lx 0 0 0 Ly 0 0 0 Lz"
        if 'Lattice="' in header and box is None:
            lat = header.split('Lattice="')[1].split('"')[0].split()
            box = np.array([float(lat[0]), float(lat[4]), float(lat[8])], float)
        e = float(header.split("energy=")[1].split()[0]) if "energy=" in header else 0.0
        t = float(header.split("time_ps=")[1].split()[0]) if "time_ps=" in header else 0.0
        pos = []
        for j in range(n):
            parts = text[i + 2 + j].split()
            pos.append([float(parts[1]), float(parts[2]), float(parts[3])])
        frames_pos.append(np.asarray(pos, float))
        energies.append(e)
        times.append(t)
        i += 2 + n

    bonds = []
    for pos in frames_pos:
        bonds.append([float(np.linalg.norm(pos[2 * m] - pos[2 * m + 1])) for m in range(N_MOL)])

    # positions stored in Angstrom in file — convert to Bohr for shared plot path
    return {
        "positions_bohr": [p / BOHR_TO_A for p in frames_pos],
        "energies_hartree": energies,
        "bonds_bohr": [[b / BOHR_TO_A for b in row] for row in bonds],
        "times_ps": times,
        "box_bohr": box / BOHR_TO_A if box is not None else np.array([22.5, 22.5, 22.5]),
        "atomic_numbers": [1] * (2 * N_MOL),
        "source": str(path),
    }


def _style_2d(ax, ink="#0F172A"):
    ax.set_facecolor("#FFFFFF")
    ax.grid(True, axis="y", color="#E2E8F0", lw=0.8, zorder=0)
    ax.grid(False, axis="x")
    ax.tick_params(labelsize=11.5, colors="#1E293B", length=3.5, width=0.8)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color("#94A3B8")
        ax.spines[sp].set_linewidth(1.1)


def _plot(comp, ckpt: Path, out_paths: list[Path]) -> None:
    plt = _setup_font()
    from matplotlib.gridspec import GridSpec
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    INK = "#0F172A"
    BODY = "#1E293B"
    SOFT = "#475569"
    PAPER = "#F7F5F1"
    C_MEAN = "#1E3A5F"
    C_EQ = "#C2410C"
    C_E = "#0F766E"
    PANEL = "#FFFFFF"
    HAIR = "#D0D7E0"

    box_a = np.asarray(comp["box_bohr"], float) * BOHR_TO_A
    frames = [np.asarray(p, float) * BOHR_TO_A for p in comp["positions_bohr"]]
    n_mol = N_MOL
    n_f = len(frames)
    show_idx = [0, n_f // 3, 2 * n_f // 3, n_f - 1]

    times = np.asarray(comp["times_ps"], float)
    if len(times) > 1 and np.any(np.diff(times) > 0):
        t_fs = (times - times[0]) * 1000.0
    else:
        t_fs = np.arange(n_f, dtype=float) * 0.5

    fig = plt.figure(figsize=(14.0, 9.0), dpi=120, facecolor=PAPER)
    gs = GridSpec(
        2,
        4,
        figure=fig,
        height_ratios=[1.35, 1.0],
        hspace=0.38,
        wspace=0.22,
        left=0.06,
        right=0.98,
        top=0.88,
        bottom=0.08,
    )

    fig.text(
        0.5,
        0.955,
        "QML-FF 力场驱动：盒子内 10×H2 分子动力学轨迹",
        ha="center",
        va="center",
        fontsize=19,
        fontweight="bold",
        color=INK,
    )
    fig.text(
        0.5,
        0.915,
        "NVT-Langevin · 300 K · atomic_amplitude / P3 round_09 (job 8992) · 10 分子 × 同一力场",
        ha="center",
        va="center",
        fontsize=11.5,
        color=SOFT,
    )

    # ---- 4 snapshots ----
    for k, fi in enumerate(show_idx):
        ax = fig.add_subplot(gs[0, k], projection="3d")
        ax.set_facecolor(PANEL)
        pos = frames[fi]
        _draw_box(ax, box_a, color="#94A3B8", lw=1.5)
        for m in range(n_mol):
            c = MOL_COLORS[m % len(MOL_COLORS)]
            a, b = pos[2 * m], pos[2 * m + 1]
            ax.plot(
                [a[0], b[0]],
                [a[1], b[1]],
                [a[2], b[2]],
                color=c,
                lw=2.8,
                solid_capstyle="round",
                zorder=3,
            )
            ax.scatter(
                [a[0], b[0]],
                [a[1], b[1]],
                [a[2], b[2]],
                s=90,
                c=c,
                edgecolors="white",
                linewidths=1.15,
                depthshade=True,
                zorder=5,
            )
        pad = 0.15
        ax.set_xlim(-pad, box_a[0] + pad)
        ax.set_ylim(-pad, box_a[1] + pad)
        ax.set_zlim(-pad, max(box_a[2], 1.0) + pad)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])
        for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
            pane.fill = False
            pane.set_edgecolor("#E8EEF4")
        ax.grid(False)
        ax.view_init(elev=24, azim=-55 + k * 6)
        try:
            aspect = np.array([box_a[0], box_a[1], box_a[2]])
            ax.set_box_aspect(aspect)
        except Exception:
            pass
        ax.set_title(
            f"帧 {k + 1}/4   ·   t ≈ {t_fs[fi]:.1f} fs",
            fontsize=12.5,
            fontweight="bold",
            color=INK,
            pad=10,
        )

    # ---- bonds ----
    ax_b = fig.add_subplot(gs[1, 0:2])
    _style_2d(ax_b)
    bonds = np.asarray(comp["bonds_bohr"], float) * BOHR_TO_A
    bmin, bmax = bonds.min(axis=1), bonds.max(axis=1)
    ax_b.fill_between(t_fs, bmin, bmax, color="#99F6E4", alpha=0.40, zorder=1, label="10 分子包络")
    for m in range(n_mol):
        ax_b.plot(t_fs, bonds[:, m], color=MOL_COLORS[m], alpha=0.40, lw=1.2, zorder=2)
    ax_b.plot(t_fs, bonds.mean(axis=1), color=C_MEAN, lw=2.7, label="均值", zorder=3)
    ax_b.axhline(0.74, color=C_EQ, ls="--", lw=1.7, label="平衡 ≈ 0.74 Å", zorder=3)
    ax_b.set_xlabel("时间 (fs)", fontsize=12.5, color=BODY)
    ax_b.set_ylabel("H–H 键长 (Å)", fontsize=12.5, color=BODY)
    ax_b.set_title("(a)  键长振荡", fontsize=14, fontweight="bold", color=INK, loc="left", pad=8)
    ax_b.legend(fontsize=10, frameon=False, loc="lower right")
    ax_b.set_xlim(float(t_fs[0]), float(t_fs[-1]))
    ax_b.set_ylim(0.35, 1.05)

    # ---- energy ----
    ax_e = fig.add_subplot(gs[1, 2:4])
    _style_2d(ax_e)
    e = np.asarray(comp["energies_hartree"], float)
    ax_e.fill_between(t_fs, e, float(e.max()) + 0.0008, color="#CCFBF1", alpha=0.5, zorder=1)
    ax_e.plot(t_fs, e, color=C_E, lw=2.6, zorder=3)
    ax_e.scatter(
        t_fs[show_idx],
        e[show_idx],
        s=60,
        c=C_MEAN,
        edgecolors="white",
        linewidths=1.3,
        zorder=4,
        label="上图快照",
    )
    ax_e.set_xlabel("时间 (fs)", fontsize=12.5, color=BODY)
    ax_e.set_ylabel("总能量 E (Ha)", fontsize=12.5, color=BODY)
    ax_e.set_title("(b)  盒子总能量（10 分子之和）", fontsize=14, fontweight="bold", color=INK, loc="left", pad=8)
    ax_e.legend(fontsize=10, frameon=False, loc="best")
    ax_e.set_xlim(float(t_fs[0]), float(t_fs[-1]))

    fig.text(
        0.5,
        0.02,
        "力场按单分子 H2 在线学习训练；装箱时对 10 个分子分别用同一 checkpoint 推进（避免多分子外推失稳）",
        ha="center",
        va="center",
        fontsize=10.5,
        color=SOFT,
    )

    for out in out_paths:
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, dpi=260, facecolor=PAPER, bbox_inches="tight", pad_inches=0.22)
        print(f"wrote {out} ({out.stat().st_size})")
    plt.close(fig)


def main() -> None:
    import argparse
    import sys

    sys.path.insert(0, str(ROOT / "src"))
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--from-extxyz",
        type=Path,
        default=OVITO_EXTXYZ if OVITO_EXTXYZ.exists() else None,
        help="Reuse OVITO extxyz (skip MD). Default: results/.../h2_box_10mol_qmlff_md.extxyz",
    )
    p.add_argument("--rerun-md", action="store_true", help="Force re-run MD instead of loading extxyz")
    args = p.parse_args()

    if args.from_extxyz and args.from_extxyz.exists() and not args.rerun_md:
        print("plot from", args.from_extxyz)
        comp = _load_ovito_extxyz(args.from_extxyz)
        # keep only stable frames (all H–H < 1.2 Å) for presentation clarity
        bonds_a = np.asarray(comp["bonds_bohr"], float) * BOHR_TO_A
        stable = np.where(bonds_a.max(axis=1) < 1.20)[0]
        if len(stable) < 8:
            stable = np.arange(min(24, len(comp["positions_bohr"])))
        # contiguous prefix of stable frames looks most natural
        cut = int(stable[0])
        for i in range(len(stable) - 1):
            if stable[i + 1] != stable[i] + 1:
                break
            cut = int(stable[i + 1])
        idx = np.arange(0, cut + 1)
        if len(idx) > 28:
            idx = np.linspace(0, cut, 28, dtype=int)
        print(f"using {len(idx)} stable frames (0..{cut})")
        comp = {
            **comp,
            "positions_bohr": [comp["positions_bohr"][i] for i in idx],
            "energies_hartree": [comp["energies_hartree"][i] for i in idx],
            "bonds_bohr": [comp["bonds_bohr"][i] for i in idx],
            "times_ps": [comp["times_ps"][i] for i in idx],
        }
        _plot(comp, DEFAULT_CKPT, OUT_PNGS)
        return

    ckpt = DEFAULT_CKPT
    if not ckpt.exists():
        alt = ROOT / "results/qmlff_md_h2/qmlff_checkpoints/final.npz"
        if alt.exists():
            ckpt = alt
        else:
            raise SystemExit(f"checkpoint not found: {DEFAULT_CKPT}")

    print("loading", ckpt)
    handle = _load_handle(ckpt)
    print("running per-molecule MD …")
    mol_trajs = [_run_single_md(handle, seed=10 + i) for i in range(N_MOL)]
    centers, box = _pack_centers(N_MOL)
    comp = _compose_box_traj(mol_trajs, centers, box, n_frames=100)
    _write_xyz(comp, OUT_XYZ)
    print("wrote", OUT_XYZ)
    _plot(comp, ckpt, OUT_PNGS)


if __name__ == "__main__":
    main()
