#!/usr/bin/env python3
"""Run MD/ML active learning with selectable backend profile (UQC cloud / mock / simulators).

Default production path for InQuanto/UQC 内网云: ``--backend-profile uqc_cloud`` on
``configs/example_h2_uqc_cloud_sim_md_ml.yaml`` (requires ``UQC_API_TOKEN``).

Local CI / offline: ``--backend-profile uqc_mock``.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

DEFAULT_ACCURACY_THRESHOLD_HARTREE = 0.1
DEFAULT_EXP = REPO / "configs" / "example_h2_uqc_cloud_sim_md_ml.yaml"
DEFAULT_LOOP = REPO / "configs" / "example_h2_uqc_cloud_sim_qmlff_loop_5rounds.yaml"
DEFAULT_OUT = REPO / "results" / "uqc_cloud_sim_md_ml_optimized"
DEFAULT_PROFILE = "uqc_cloud"


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--experiment", type=Path, default=DEFAULT_EXP)
    ap.add_argument("--loop", type=Path, default=DEFAULT_LOOP)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    ap.add_argument(
        "--backend-profile",
        default=DEFAULT_PROFILE,
        help="Named backend preset (uqc_cloud, uqc_mock, statevector, cirq, braket, ...)",
    )
    ap.add_argument(
        "--list-backend-profiles",
        action="store_true",
        help="Print available backend profiles and exit",
    )
    ap.add_argument(
        "--accuracy-threshold-hartree",
        type=float,
        default=DEFAULT_ACCURACY_THRESHOLD_HARTREE,
    )
    args = ap.parse_args()

    from qchem_stack.backends.profiles import backend_profile_catalog_v1, list_backend_profile_ids

    if args.list_backend_profiles:
        print(json.dumps(backend_profile_catalog_v1(), indent=2, ensure_ascii=False))
        return 0

    profile_id = str(args.backend_profile).strip().lower()
    if profile_id not in list_backend_profile_ids():
        print(
            f"ERROR: unknown backend profile {profile_id!r}; use --list-backend-profiles",
            file=sys.stderr,
        )
        return 2

    if profile_id == "uqc_cloud":
        import os

        if not (os.environ.get("UQC_API_TOKEN") or os.environ.get("USER_TOKEN")):
            logging.warning(
                "uqc_cloud profile selected but UQC_API_TOKEN unset — "
                "cloud submit will fail unless token is provided via env or .env"
            )

    try:
        import pyscf  # noqa: F401
    except ImportError:
        print("ERROR: PySCF required. pip install -e '.[chem]'", file=sys.stderr)
        return 2
    try:
        import jax_md  # noqa: F401
        import qmlff  # noqa: F401
    except ImportError:
        print("ERROR: qmlff and jax-md required.", file=sys.stderr)
        return 2

    sys.path.insert(0, str(REPO / "scripts"))
    from backend_profile_helpers import (
        load_experiment_with_backend_profile,
        write_resolved_experiment_yaml,
    )

    import qchem_stack.orchestration  # noqa: F401 — registers default pipeline runner for MD/ML loop
    from qchem_stack.md_bridge import MdValidationLoopConfig, run_md_validation_loop

    cfg, prof, _ = load_experiment_with_backend_profile(args.experiment, profile_id)
    args.output.mkdir(parents=True, exist_ok=True)
    resolved_yaml = write_resolved_experiment_yaml(cfg, args.output, profile_id=profile_id)
    logging.info(
        "backend profile=%s provider=%s resolved_yaml=%s",
        prof.profile_id,
        prof.provider,
        resolved_yaml,
    )

    loop_cfg = MdValidationLoopConfig.from_yaml(args.loop)
    summary = run_md_validation_loop(
        resolved_yaml,
        config=loop_cfg,
        output_dir=args.output,
        accuracy_threshold_hartree=float(args.accuracy_threshold_hartree),
    )
    summary["backend_profile"] = prof.profile_id
    summary["backend_provider"] = prof.provider
    summary["backend_name"] = prof.name
    (args.output / "md_validation_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    logging.info(
        "Done. summary=%s converged=%s science_kpi_met=%s backend=%s",
        args.output / "md_validation_summary.json",
        summary.get("converged"),
        summary.get("science_kpi_met"),
        prof.profile_id,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
