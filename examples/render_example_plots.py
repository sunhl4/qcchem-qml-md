#!/usr/bin/env python3
"""Render packaged example pipeline results into ``examples/plots/*.png``.

Requires PySCF, matplotlib, and ``PYTHONPATH`` including ``src`` (or editable install).

Outputs (overwritten each run):

- ``examples/plots/h2_pauli_protocol.png`` — ``configs/example_h2.yaml`` (SCF / variational / Pauli).
- ``examples/plots/h2_uccsd_vs_scf.png`` — ``configs/example_h2_uccsd.yaml`` vs sto-3g FCI reference.
- ``examples/plots/fe_helike_smoke.png`` — ``configs/example_fe_sto3g_helike_rhf_cas22.yaml`` (lightweight Fe demo).
"""

from __future__ import annotations

from pathlib import Path


def _require_plotting() -> object:
    try:
        import matplotlib.pyplot as plt
    except ImportError as e:  # pragma: no cover
        raise SystemExit("matplotlib required: pip install matplotlib") from e
    try:
        import pyscf  # noqa: F401
    except ImportError as e:  # pragma: no cover
        raise SystemExit("PySCF required: pip install qchem-stack[chem]") from e
    return plt


def _plot_energy_ladder(
    plt: object,
    *,
    out_path: Path,
    cfg_path: Path,
    title_suffix: str,
    fci_ref_ha: float | None = None,
) -> None:
    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)

    scf = float(out["scf_energy"]) if out.get("scf_energy") is not None else float("nan")
    ev = float(out["energy_after_variational"]) if out.get("energy_after_variational") is not None else float("nan")
    ep = out.get("energy_pauli_protocol")
    ep_f = float(ep) if ep is not None else None

    repro = out.get("repro") or {}
    prof = repro.get("pipeline_profile") or {}
    stages = prof.get("stages") if isinstance(prof, dict) else None

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))

    names = ["SCF", "Variational"]
    vals = [scf, ev]
    if ep_f is not None:
        names.append("Pauli protocol")
        vals.append(ep_f)
    colors = ["#1a365d", "#276749", "#9c4221"][: len(vals)]
    axes[0].bar(names, vals, color=colors, edgecolor="#2d3748", linewidth=0.6)
    axes[0].axhline(scf, color="#718096", linestyle="--", linewidth=0.9, label="SCF reference")
    if fci_ref_ha is not None:
        axes[0].axhline(fci_ref_ha, color="#805ad5", linestyle=":", linewidth=1.0, label="FCI ref (H₂ sto-3g)")
    axes[0].set_ylabel("Energy (Ha)")
    axes[0].set_title(f"Energies — {cfg.experiment_id}")
    axes[0].legend(loc="best", fontsize=8)
    axes[0].set_facecolor("#f7fafc")

    if isinstance(stages, list) and stages:
        labels = [str(s.get("stage", "?")) for s in stages if isinstance(s, dict)]
        ms = [float(s.get("duration_ms", 0.0) or 0.0) for s in stages if isinstance(s, dict)]
        axes[1].barh(labels[::-1], ms[::-1], color="#4a5568", edgecolor="#2d3748", linewidth=0.5)
        axes[1].set_xlabel("duration_ms")
        axes[1].set_title("pipeline_profile stages")
        axes[1].set_facecolor("#f7fafc")
    else:
        axes[1].text(0.5, 0.5, "no pipeline_profile in repro", ha="center", va="center", fontsize=10)
        axes[1].set_axis_off()

    fig.patch.set_facecolor("#edf2f7")
    fig.suptitle(f"qchem-stack — {cfg_path.name}{title_suffix}", fontsize=11, color="#1a202c")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print("wrote", out_path.resolve())


def main() -> int:
    plt = _require_plotting()
    root = Path(__file__).resolve().parents[1]
    plots = root / "examples" / "plots"

    _plot_energy_ladder(
        plt,
        out_path=plots / "h2_pauli_protocol.png",
        cfg_path=root / "configs" / "example_h2.yaml",
        title_suffix="",
        fci_ref_ha=None,
    )

    e_fci_h2 = -1.1372759436170443
    _plot_energy_ladder(
        plt,
        out_path=plots / "h2_uccsd_vs_scf.png",
        cfg_path=root / "configs" / "example_h2_uccsd.yaml",
        title_suffix=" (UCCSD)",
        fci_ref_ha=e_fci_h2,
    )

    _plot_energy_ladder(
        plt,
        out_path=plots / "fe_helike_smoke.png",
        cfg_path=root / "configs" / "example_fe_sto3g_helike_rhf_cas22.yaml",
        title_suffix=" (Fe He-like demo)",
        fci_ref_ha=None,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
