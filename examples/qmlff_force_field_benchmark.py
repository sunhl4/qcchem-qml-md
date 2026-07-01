"""Benchmark QML-FF backends on H2 bond-stretch labels (Phase 3 quantum comparison).

Labels geometries via qchem HF-SCF, then trains each backend and reports energy MAE
on the same frames. Does **not** run MD or active learning.

Usage::

    python examples/qmlff_force_field_benchmark.py \\
        --experiment configs/example_h2.yaml \\
        --output results/qmlff_h2_benchmark
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import qchem_stack.orchestration  # noqa: F401 — registers md_bridge pipeline runner

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--experiment", default="configs/example_h2.yaml")
    p.add_argument("--output", default="results/qmlff_h2_benchmark")
    p.add_argument(
        "--backends",
        nargs="+",
        default=["classical_h2", "qmlff_qmp_h2", "qmlff_angle", "qmlff_preset"],
        choices=["classical_h2", "qmlff_qmp_h2", "qmlff_angle", "qmlff_preset"],
    )
    p.add_argument("--n-epochs", type=int, default=30)
    p.add_argument("--seed-bond-min", type=float, default=0.8)
    p.add_argument("--seed-bond-max", type=float, default=2.2)
    p.add_argument("--n-seed", type=int, default=12)
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    import numpy as np

    from qchem_stack.md_bridge import (
        build_force_field_handle,
        label_base_geometry_only,
        label_geometries_with_pipeline,
        merge_qmef_datasets,
        predict_energy_forces_hartree,
        train_force_field_on_qmef,
    )
    from qchem_stack.md_bridge.md_validation_loop import _bond_stretch_geometries

    exp = Path(args.experiment)
    base = label_base_geometry_only(exp, energy_reference="scf", include_hf_nuclear_gradient=True)
    dataset = base.dataset
    base_pos = np.asarray(dataset.frames[0].positions_bohr, dtype=np.float64)
    seed_geoms = _bond_stretch_geometries(
        base_pos, n=args.n_seed, r_min_bohr=args.seed_bond_min, r_max_bohr=args.seed_bond_max
    )
    seed_result = label_geometries_with_pipeline(
        exp,
        extra_coordinates_bohr=seed_geoms,
        energy_reference="scf",
        theory_level="hf_scf",
        include_hf_nuclear_gradient=True,
        failure_isolation=True,
    )
    dataset = merge_qmef_datasets(dataset, seed_result.dataset)

    species = ["H"]
    results: dict[str, dict] = {}

    for backend in args.backends:
        logging.info("=== backend: %s ===", backend)
        handle = build_force_field_handle(
            species,
            backend=backend,
            preset="atomic_amplitude",
            builder_overrides={"n_qubits": 6, "n_layers": 2},
            qmp_h2_overrides={"cutoff": 5.0, "cg_l": 1, "n_radial_basis": 8, "seed": 42},
        )
        handle = train_force_field_on_qmef(
            handle,
            dataset,
            n_epochs=args.n_epochs if backend != "classical_h2" else 1,
            batch_size=1,
            learning_rate=1e-3 if backend != "qmlff_qmp_h2" else 1e-4,
            force_weight=10.0 if backend == "qmlff_preset" else 50.0,
            lr_scheduler="constant",
            warm_start=False,
            checkpoint_dir=out / f"checkpoints_{backend}",
        )

        errs: list[float] = []
        for fr in dataset.frames:
            pos = np.asarray(fr.positions_bohr, dtype=np.float64)
            zs = [int(z) for z in fr.atomic_numbers]
            e_pred, _ = predict_energy_forces_hartree(handle, positions_bohr=pos, atomic_numbers=zs)
            errs.append(abs(float(e_pred) - float(fr.energy_hartree)))

        results[backend] = {
            "n_frames": len(dataset.frames),
            "energy_mae_hartree": float(np.mean(errs)),
            "energy_max_hartree": float(np.max(errs)),
            "train_meta": dict(getattr(handle, "train_meta", {})),
        }
        logging.info(
            "%s: E_MAE=%.6f Ha max=%.6f Ha",
            backend,
            results[backend]["energy_mae_hartree"],
            results[backend]["energy_max_hartree"],
        )

    summary_path = out / "benchmark_summary.json"
    summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
