"""Compare QML-FF native H2 training vs md_bridge native-style recipe.

Runs two benchmarks and writes ``benchmark_summary.json``:

1. **qmlff_native** — ``QML-FF/scripts/train.py`` on ``data/H2/train.extxyz`` (143 frames)
2. **md_bridge_native** — qchem HF labels (13 bond-stretch frames) via md_bridge with
   ``subtract_mean``, ``n_qubits=5``, ``n_layers=4``, etc.

Usage::

    conda activate qmlff-py311
    cd /path/to/qcchem-qml-md
    python examples/qmlff_h2_native_benchmark.py --output results/qmlff_h2_native_benchmark
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path

import numpy as np

_REPO_ROOT = Path(__file__).resolve().parent.parent
_QMLFF_ROOT = _REPO_ROOT.parent / "QML-FF"
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--experiment", default="configs/example_h2.yaml")
    p.add_argument("--output", default="results/qmlff_h2_native_benchmark")
    p.add_argument("--n-epochs", type=int, default=80)
    p.add_argument("--skip-native-qmlff", action="store_true", help="Skip QML-FF train.py step")
    return p.parse_args()


def _energy_mae_hartree(handle, dataset) -> dict[str, float]:
    from qchem_stack.md_bridge import predict_energy_forces_hartree

    errs: list[float] = []
    preds: list[float] = []
    for fr in dataset.frames:
        pos = np.asarray(fr.positions_bohr, dtype=np.float64)
        zs = [int(z) for z in fr.atomic_numbers]
        e_pred, _ = predict_energy_forces_hartree(handle, positions_bohr=pos, atomic_numbers=zs)
        preds.append(float(e_pred))
        errs.append(abs(float(e_pred) - float(fr.energy_hartree)))
    return {
        "energy_mae_hartree": float(np.mean(errs)),
        "energy_max_hartree": float(np.max(errs)),
        "pred_min_hartree": float(min(preds)),
        "pred_max_hartree": float(max(preds)),
    }


def _build_qchem_h2_dataset(experiment: Path):
    from qchem_stack.md_bridge import (
        label_base_geometry_only,
        label_geometries_with_pipeline,
        merge_qmef_datasets,
    )
    from qchem_stack.md_bridge.md_validation_loop import _bond_stretch_geometries

    base = label_base_geometry_only(
        experiment, energy_reference="scf", include_hf_nuclear_gradient=True
    )
    dataset = base.dataset
    base_pos = np.asarray(dataset.frames[0].positions_bohr, dtype=np.float64)
    seed_geoms = _bond_stretch_geometries(base_pos, n=12, r_min_bohr=0.8, r_max_bohr=2.2)
    seed_result = label_geometries_with_pipeline(
        experiment,
        extra_coordinates_bohr=seed_geoms,
        energy_reference="scf",
        theory_level="hf_scf",
        include_hf_nuclear_gradient=True,
        failure_isolation=True,
    )
    return merge_qmef_datasets(dataset, seed_result.dataset)


def _run_md_bridge_native(dataset, out: Path, n_epochs: int) -> dict:
    from qchem_stack.md_bridge import (
        build_force_field_handle,
        train_force_field_on_qmef,
    )

    handle = build_force_field_handle(
        ["H"],
        backend="qmlff_quantum",
        builder_overrides={"n_qubits": 5, "n_layers": 4, "encoding_type": "angle"},
    )
    handle = train_force_field_on_qmef(
        handle,
        dataset,
        n_epochs=n_epochs,
        batch_size=4,
        learning_rate=1e-3,
        force_weight=100.0,
        lr_scheduler="constant",
        energy_normalization="subtract_mean",
        grad_clip=1.0,
        warm_start=False,
        checkpoint_dir=out / "md_bridge_checkpoints",
    )
    metrics = _energy_mae_hartree(handle, dataset)
    fm = handle.train_meta.get("final_metrics", {})
    return {
        "n_frames": len(dataset.frames),
        "train_meta": dict(handle.train_meta),
        "final_energy_mae_ev": fm.get("energy_mae"),
        "final_force_rmse_ev_ang": fm.get("force_rmse"),
        **metrics,
    }


def _run_qmlff_native(out: Path, n_epochs: int) -> dict:
    cfg = _QMLFF_ROOT / "configs/h2_benchmark_80epoch.yaml"
    if not cfg.is_file():
        raise FileNotFoundError(f"Missing {cfg}")

    cmd = [
        sys.executable,
        str(_QMLFF_ROOT / "scripts/train.py"),
        "--config",
        str(cfg),
        f"training.n_epochs={n_epochs}",
        f"training.checkpoint_dir={out / 'qmlff_native_checkpoints'}",
    ]
    logging.info("Running: %s", " ".join(cmd))
    subprocess.run(cmd, cwd=_QMLFF_ROOT, check=True)

    ckpt_root = out / "qmlff_native_checkpoints"
    run_dirs = sorted(ckpt_root.glob("run_*"), key=lambda p: p.stat().st_mtime)
    results_path = run_dirs[-1] / "results.json" if run_dirs else ckpt_root / "results.json"
    if not results_path.is_file():
        # train.py may write directly under checkpoint_dir
        alt = list(ckpt_root.rglob("results.json"))
        if not alt:
            raise FileNotFoundError(f"No results.json under {ckpt_root}")
        results_path = sorted(alt, key=lambda p: p.stat().st_mtime)[-1]

    payload = json.loads(results_path.read_text(encoding="utf-8"))
    test = payload.get("test_metrics") or payload.get("val_metrics") or {}
    return {
        "results_json": str(results_path),
        "test_metrics": test,
        "config": payload.get("config", {}),
    }


def main() -> int:
    args = _parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    results: dict[str, dict] = {}

    if not args.skip_native_qmlff:
        logging.info("=== (1) QML-FF native train.py on data/H2/train.extxyz ===")
        try:
            results["qmlff_native"] = _run_qmlff_native(out, args.n_epochs)
        except Exception as exc:
            logging.exception("QML-FF native benchmark failed")
            results["qmlff_native"] = {"error": str(exc)}

    logging.info("=== (2) md_bridge native recipe on qchem HF labels ===")
    dataset = _build_qchem_h2_dataset(_REPO_ROOT / args.experiment)
    results["md_bridge_native"] = _run_md_bridge_native(dataset, out, args.n_epochs)

    summary_path = out / "benchmark_summary.json"
    summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {summary_path}")
    for name, block in results.items():
        if "error" in block:
            print(f"  {name}: ERROR — {block['error']}")
        elif name == "md_bridge_native":
            print(f"  {name}: E_MAE={block['energy_mae_hartree']:.4f} Ha (n={block['n_frames']})")
        elif name == "qmlff_native":
            tm = block.get("test_metrics") or {}
            print(f"  {name}: test metrics = {tm}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
