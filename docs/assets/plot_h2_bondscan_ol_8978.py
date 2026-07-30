#!/usr/bin/env python3
"""Publication figures for HPC job 8978: H2 P0–P2 bond-scan → pretrain → online learning."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.colors import Normalize

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "results/h2_bondscan_ol_statevector_p0p2_r40_8978"
DATA_6759 = ROOT / "results/h2_bondscan_ol_statevector_r20_6759"
OUT_DIR = DATA / "figures"
OUT_ALT = [
    ROOT / "docs/assets/shuzhi_demo/uqc",
    Path("/tmp/shuzhi_unified/figures/uqc"),
]

INK = "#142033"
MUTED = "#4E5D6C"
ACCENT = "#2A4F8A"
ACCENT2 = "#8A4333"
OK = "#246044"
WARN = "#B45309"
GRID = "#E2E8F0"
CUTOFF_BOHR = 11.33835674775462
DISSOC_BOHR = 3.0


def _setup_font() -> None:
    for fp in (
        "/mnt/c/Windows/Fonts/msyh.ttc",
        "/mnt/c/Windows/Fonts/simhei.ttf",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    ):
        if Path(fp).exists():
            font_manager.fontManager.addfont(fp)
            name = font_manager.FontProperties(fname=fp).get_name()
            plt.rcParams["font.sans-serif"] = [name, "DejaVu Sans"]
            break
    plt.rcParams.update(
        {
            "axes.unicode_minus": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#C8D0DA",
            "axes.labelcolor": INK,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "text.color": INK,
            "axes.titlesize": 12,
            "axes.labelsize": 10.5,
            "legend.fontsize": 8.5,
            "figure.dpi": 160,
        }
    )


def _bonds_from_xyz(path: Path) -> list[float]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    bonds: list[float] = []
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        n = int(lines[i])
        i += 2
        pos = []
        for _ in range(n):
            parts = lines[i].split()
            pos.append([float(x) for x in parts[1:4]])
            i += 1
        arr = np.asarray(pos, float)
        if arr.shape[0] == 2:
            bonds.append(float(np.linalg.norm(arr[0] - arr[1])))
    return bonds


def _load_rounds() -> list[dict]:
    paths = sorted(DATA.glob("validation_round_*.json"), key=lambda p: int(p.stem.split("_")[-1]))
    rounds: list[dict] = []
    for p in paths:
        payload = json.loads(p.read_text(encoding="utf-8"))
        r = payload["round"]
        frames_dbg = payload.get("frames_debug") or {}
        frame_rows = []
        for fr in r.get("frames") or []:
            fi = int(fr["frame_index"])
            dbg = frames_dbg.get(str(fi)) or frames_dbg.get(fi) or {}
            qml = (dbg.get("qml_prediction") or {}) if isinstance(dbg, dict) else {}
            pos = np.asarray(qml.get("positions_bohr") or [], float)
            bond = float(np.linalg.norm(pos[0] - pos[1])) if pos.shape == (2, 3) else float("nan")
            frame_rows.append(
                {
                    "frame_index": fi,
                    "bond_bohr": bond,
                    "abs_delta": float(fr["abs_delta_hartree"]),
                    "e_qml": float(fr["energy_qml_hartree"]),
                    "e_qchem": float(fr["energy_qchem_hartree"]),
                    "time_ps": float(fr.get("time_ps") or 0.0),
                }
            )
        tm = (r.get("training_metrics") or {}).get("final_metrics") or {}
        rounds.append(
            {
                "round_index": int(r["round_index"]),
                "n_train_before": int(r["n_train_before"]),
                "n_train_after": int(r["n_train_after"]),
                "max_abs_delta_hartree": float(r["max_abs_delta_hartree"]),
                "mean_abs_delta_hartree": float(r["mean_abs_delta_hartree"]),
                "converged": bool(r.get("converged")),
                "energy_mae": float(tm.get("energy_mae") or np.nan),
                "force_rmse": float(tm.get("force_rmse") or np.nan),
                "frames": frame_rows,
            }
        )
    return rounds


def _stage_tol(ri: int) -> float:
    if ri <= 15:
        return 0.05
    if ri <= 30:
        return 0.01
    return 5.0e-4


def _save(fig: plt.Figure, name: str) -> list[Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = [OUT_DIR / name]
    for alt in OUT_ALT:
        alt.mkdir(parents=True, exist_ok=True)
        paths.append(alt / name)
    for p in paths:
        fig.savefig(p, dpi=180, bbox_inches="tight", facecolor="white")
        print("wrote", p)
    return paths


def plot_overview(rounds: list[dict], bonds0: list[float], bonds_f: list[float]) -> None:
    xs = [r["round_index"] for r in rounds]
    max_de = [r["max_abs_delta_hartree"] for r in rounds]
    mean_de = [r["mean_abs_delta_hartree"] for r in rounds]
    n_train = [r["n_train_after"] for r in rounds]
    bound_max = []
    for r in rounds:
        vals = [f["abs_delta"] for f in r["frames"] if f["bond_bohr"] == f["bond_bohr"] and f["bond_bohr"] < DISSOC_BOHR]
        bound_max.append(max(vals) if vals else np.nan)

    fig, axes = plt.subplots(2, 2, figsize=(11.4, 8.4))
    fig.suptitle(
        "H2 QML-FF P0–P2：键长扫描预训练 → 在线学习（HPC job 8978，进行中）",
        fontsize=13.2,
        fontweight="bold",
        color=INK,
        y=0.98,
    )

    ax = axes[0, 0]
    ax.plot(xs, max_de, "o-", color=ACCENT, lw=1.8, ms=5.5, label="overall max |ΔE|")
    ax.plot(xs, mean_de, "s--", color=ACCENT2, lw=1.5, ms=4.5, label="overall mean |ΔE|")
    ax.plot(xs, bound_max, "^-.", color=OK, lw=1.4, ms=4.5, label=f"bound only (R<{DISSOC_BOHR:g})")
    ax.axhline(0.05, color=MUTED, ls=":", lw=1.2, label="stage1 tol 0.05")
    ax.axvline(15.5, color=GRID, lw=1.2)
    ax.set_yscale("log")
    ax.set_xlabel("在线学习轮次")
    ax.set_ylabel("|E_QML − E_VQE| (Ha)")
    ax.set_title("校验误差随轮次（对数轴）")
    ax.grid(True, which="both", color=GRID, lw=0.8)
    ax.legend(frameon=False, loc="upper right")
    spike_i = int(np.argmax(max_de))
    ax.annotate(
        f"r{xs[spike_i]} 尖峰\nmax={max_de[spike_i]:.3f}",
        xy=(xs[spike_i], max_de[spike_i]),
        xytext=(xs[spike_i] - 5.5, max_de[spike_i] * 0.55),
        fontsize=8.5,
        color=MUTED,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=0.9),
    )

    ax = axes[0, 1]
    n0 = rounds[0]["n_train_before"]
    ax.fill_between(xs, [n0] + n_train[:-1], n_train, step="pre", color=ACCENT, alpha=0.12)
    ax.plot(xs, n_train, "o-", color=ACCENT, lw=1.8, ms=5)
    ax.axhline(n0, color=MUTED, ls="--", lw=1.2, label=f"预训练后 {n0} 帧")
    ax.set_xlabel("在线学习轮次")
    ax.set_ylabel("累计训练帧数")
    ax.set_title(f"训练集增长（{n0} → {n_train[-1]}）")
    ax.set_ylim(0, max(n_train) + 10)
    ax.grid(True, color=GRID, lw=0.8)
    ax.legend(frameon=False)

    ax = axes[1, 0]
    # overlay 6759 if available
    if (DATA_6759 / "md_validation_summary.json").exists():
        s6759 = json.loads((DATA_6759 / "md_validation_summary.json").read_text(encoding="utf-8"))
        x2 = [r["round_index"] for r in s6759["rounds"]]
        y2 = [r["max_abs_delta_hartree"] for r in s6759["rounds"]]
        ax.plot(x2, y2, "^-", color=ACCENT2, lw=1.5, ms=4.5, alpha=0.9, label="6759 overall max")
    ax.plot(xs, max_de, "o-", color=ACCENT, lw=1.8, ms=5, label="8978 overall max")
    ax.plot(xs, bound_max, "s--", color=OK, lw=1.4, ms=4, label="8978 bound only")
    ax.axhline(0.05, color=MUTED, ls=":", lw=1.1)
    ax.set_xlabel("在线学习轮次")
    ax.set_ylabel("max |ΔE| (Ha)")
    ax.set_title("与 job 6759 对比（线性轴）")
    ax.set_ylim(0, 1.05)
    ax.grid(True, color=GRID, lw=0.8)
    ax.legend(frameon=False, loc="upper right")

    ax = axes[1, 1]
    phys0 = [b for b in bonds0 if b < 5]
    phys_f = [b for b in bonds_f if b < 5]
    mid_f = [b for b in bonds_f if 5 <= b <= CUTOFF_BOHR]
    bad_f = [b for b in bonds_f if b > CUTOFF_BOHR]
    bins = np.linspace(0.6, 5.5, 25)
    if phys0:
        ax.hist(phys0, bins=bins, color=MUTED, alpha=0.55, label=f"预训练后 ({len(phys0)})")
    if phys_f:
        ax.hist(phys_f, bins=bins, color=ACCENT, alpha=0.45, label=f"当前 ≤5 Bohr ({len(phys_f)})")
    ax.axvline(DISSOC_BOHR, color=WARN, ls="--", lw=1.2, label=f"解离标记 {DISSOC_BOHR:g}")
    ax.set_xlabel("H-H 键长 (Bohr)")
    ax.set_ylabel("构型数")
    title_extra = f"另有 {len(mid_f)} 个 5-cutoff、{len(bad_f)} 个 >cutoff"
    ax.set_title(f"训练集键长覆盖（{title_extra}）" if (mid_f or bad_f) else "训练集键长覆盖")
    ax.grid(True, axis="y", color=GRID, lw=0.8)
    ax.legend(frameon=False, fontsize=8)

    fig.text(
        0.5,
        0.01,
        "Source: HPC job 8978 RUNNING · P0–P2 · statevector VQE · 30 CPU / 120G · "
        f"r{xs[-1]}/40 · cutoff={CUTOFF_BOHR:.1f} Bohr · stage tol 0.05→0.01→5e-4",
        ha="center",
        fontsize=8.5,
        color=MUTED,
    )
    fig.tight_layout(rect=(0, 0.03, 1, 0.96))
    _save(fig, "h2_bondscan_ol_8978_overview.png")
    plt.close(fig)


def plot_md_diagnosis(rounds: list[dict]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.6))
    fig.suptitle("MD 校验帧诊断：飞散主导 overall 指标", fontsize=13, fontweight="bold", color=INK)

    ax = axes[0]
    Rs, des, rounds_c = [], [], []
    for r in rounds:
        for f in r["frames"]:
            if f["bond_bohr"] != f["bond_bohr"]:
                continue
            Rs.append(f["bond_bohr"])
            des.append(f["abs_delta"])
            rounds_c.append(r["round_index"])
    Rs = np.asarray(Rs)
    des = np.asarray(des)
    rounds_c = np.asarray(rounds_c)
    # clip display for extreme flyaways but keep marker
    R_plot = np.clip(Rs, 0.3, 80)
    sc = ax.scatter(
        R_plot,
        des,
        c=rounds_c,
        cmap="viridis",
        s=36,
        alpha=0.85,
        edgecolors="none",
        norm=Normalize(vmin=1, vmax=max(rounds_c)),
    )
    ax.axvline(DISSOC_BOHR, color=WARN, ls="--", lw=1.2, label=f"解离 {DISSOC_BOHR:g} Bohr")
    ax.axvline(CUTOFF_BOHR, color=ACCENT2, ls="--", lw=1.2, label=f"cutoff {CUTOFF_BOHR:.1f} Bohr")
    ax.axhline(0.05, color=MUTED, ls=":", lw=1.1, label="tol 0.05")
    ax.set_xscale("log")
    ax.set_xlabel("H-H 键长 (Bohr, 显示上限 80)")
    ax.set_ylabel("|ΔE| (Ha)")
    ax.set_title("校验帧：键长 vs |ΔE|")
    ax.grid(True, which="both", color=GRID, lw=0.8)
    ax.legend(frameon=False, loc="upper left")
    cb = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("轮次")

    ax = axes[1]
    eq, em, rc, rb = [], [], [], []
    for r in rounds:
        for f in r["frames"]:
            eq.append(f["e_qchem"])
            em.append(f["e_qml"])
            rc.append(r["round_index"])
            rb.append(f["bond_bohr"])
    eq = np.asarray(eq)
    em = np.asarray(em)
    rb = np.asarray(rb)
    bound = rb < DISSOC_BOHR
    fly = rb >= DISSOC_BOHR
    lo = float(min(eq.min(), em.min()))
    hi = float(max(eq.max(), em.max()))
    pad = 0.05 * (hi - lo + 1e-6)
    ax.plot([lo - pad, hi + pad], [lo - pad, hi + pad], "--", color=MUTED, lw=1.2, label="y = x")
    ax.scatter(eq[fly], em[fly], c="#C4A484", s=34, alpha=0.75, label=f"R>={DISSOC_BOHR:g} ({int(fly.sum())})", edgecolors="none")
    ax.scatter(eq[bound], em[bound], c=OK, s=40, alpha=0.9, label=f"R<{DISSOC_BOHR:g} ({int(bound.sum())})", edgecolors="none")
    ax.set_xlabel("E_VQE (Ha)")
    ax.set_ylabel("E_QML (Ha)")
    ax.set_title("MD 校验帧：QML vs VQE 能量")
    ax.grid(True, color=GRID, lw=0.8)
    ax.legend(frameon=False, loc="upper left")

    fig.tight_layout()
    _save(fig, "h2_bondscan_ol_8978_md_diagnosis.png")
    plt.close(fig)


def plot_train_parity(rounds: list[dict]) -> None:
    xs = [r["round_index"] for r in rounds]
    mae = [r["energy_mae"] for r in rounds]
    frmse = [r["force_rmse"] for r in rounds]

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.4))
    fig.suptitle("在线学习训练 fit 指标与分阶段容差", fontsize=13, fontweight="bold", color=INK)

    ax = axes[0]
    ax.plot(xs, mae, "o-", color=ACCENT, lw=1.7, ms=5, label="train Energy MAE")
    ax.plot(xs, frmse, "s--", color=ACCENT2, lw=1.5, ms=4.5, label="train Force RMSE")
    ax.set_xlabel("在线学习轮次")
    ax.set_ylabel("训练集误差 (Ha / Ha/Bohr)")
    ax.set_title("每轮训练结束时的 fit 误差")
    ax.grid(True, color=GRID, lw=0.8)
    ax.legend(frameon=False)

    ax = axes[1]
    tols = [_stage_tol(r["round_index"]) for r in rounds]
    hits = [r["max_abs_delta_hartree"] <= _stage_tol(r["round_index"]) for r in rounds]
    ax.plot(xs, [r["max_abs_delta_hartree"] for r in rounds], "o-", color=ACCENT, lw=1.7, ms=5, label="overall max |ΔE|")
    ax.step(xs, tols, where="mid", color=OK, lw=1.5, label="分阶段容差")
    ax.set_xlabel("在线学习轮次")
    ax.set_ylabel("Ha")
    ax.set_title(f"阶段容差命中：{sum(hits)}/{len(hits)}")
    ax.set_ylim(0, 1.05)
    ax.grid(True, color=GRID, lw=0.8)
    ax.legend(frameon=False, loc="upper right")

    fig.tight_layout()
    _save(fig, "h2_bondscan_ol_8978_train_parity.png")
    plt.close(fig)


def main() -> int:
    _setup_font()
    rounds = _load_rounds()
    if not rounds:
        raise SystemExit(f"no validation rounds in {DATA}")

    bonds0 = _bonds_from_xyz(DATA / "train_after_pretrain.xyz")
    # prefer latest train_round_*.xyz
    train_rounds = sorted(DATA.glob("train_round_*.xyz"), key=lambda p: int(p.stem.split("_")[-1]) if p.stem.split("_")[-1].isdigit() else -1)
    bonds_f = _bonds_from_xyz(train_rounds[-1]) if train_rounds else bonds0

    plot_overview(rounds, bonds0, bonds_f)
    plot_md_diagnosis(rounds)
    plot_train_parity(rounds)
    print(f"rounds plotted: {rounds[0]['round_index']}–{rounds[-1]['round_index']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
