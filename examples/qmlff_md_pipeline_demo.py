"""End-to-end demo: qchem-stack → QML-FF training → JAX-MD → active learning.

Usage (H2 starter)::

    pip install -e .                                  # qchem-stack itself
    pip install -e /path/to/QML-FF                    # QML-FF (sibling project)
    pip install jax-md                                # MD backend

    python examples/qmlff_md_pipeline_demo.py \\
        --experiment configs/example_h2.yaml \\
        --loop       configs/example_h2_qmlff_md.yaml \\
        --output     results/qmlff_md_h2

What this does
--------------
1. Cold-starts on the H2 base geometry: a single ``run_pipeline_sync`` produces
   a 1-frame :class:`~qchem_stack.md_bridge.QMEFDataset` (Hartree/Bohr).
2. Optionally jitters a few seed geometries and labels them via the same
   pipeline so the QML-FF model has something to fit before MD begins.
3. For each round: warm-start trains the QML-FF model on the cumulative
   dataset, runs JAX-MD using the model, samples K candidate frames, re-labels
   them via qchem (cheap HF screening + optional ``full_pipeline`` top-K),
   measures |E_qml − E_qchem|, and either declares convergence or merges the
   worst frames into the dataset for the next round.

All artefacts (per-round extxyz, validation JSON, MD trajectory, final
summary) land under ``--output``.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Make the in-tree qchem_stack importable when invoked from a fresh checkout.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument(
        "--experiment",
        default="configs/example_h2.yaml",
        help="qchem-stack experiment YAML (chemistry side).",
    )
    p.add_argument(
        "--loop",
        default="configs/example_h2_qmlff_md.yaml",
        help="MdValidationLoopConfig YAML (orchestration / MD / QML-FF side).",
    )
    p.add_argument(
        "--output",
        default="results/qmlff_md_h2",
        help="Output directory for per-round artefacts + summary.",
    )
    p.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="Python logging level.",
    )
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
    )

    from qchem_stack.md_bridge import (
        MdValidationLoopConfig,
        run_md_validation_loop,
    )

    loop_cfg = MdValidationLoopConfig.from_yaml(args.loop)
    summary = run_md_validation_loop(
        args.experiment,
        config=loop_cfg,
        output_dir=args.output,
    )

    print("=" * 70)
    print(f"MD validation loop finished — output_dir = {summary['output_dir']}")
    print(f"  experiment_yaml   = {summary['experiment_yaml']}")
    print(f"  qmlff_preset      = {summary['qmlff_preset']}")
    print(f"  species_list      = {summary['species_list']}")
    print(f"  n_total_frames    = {summary['n_total_frames']}")
    print(f"  converged         = {summary['converged']}")
    for r in summary["rounds"]:
        print(
            f"  round {r['round_index']}: n_train {r['n_train_before']} → {r['n_train_after']}, "
            f"n_md_frames={r['n_md_frames_sampled']}, "
            f"max|ΔE|={r['max_abs_delta_hartree']:.6f} Ha, "
            f"mean|ΔE|={r['mean_abs_delta_hartree']:.6f} Ha, "
            f"converged={r['converged']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
