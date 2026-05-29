#!/usr/bin/env python3
"""
Run two rounds of MD/ML active learning with UQC cloud ion-trap **simulator** (iontrap-sim).

Requires:
  - pip install -e ".[chem,quantum]" uqc-client
  - pip install -e /path/to/QML-FF && pip install jax-md
  - repo ``.env``: UQC_API_TOKEN (30 min), SERVER_HOST for intranet (e.g. 192.168.110.148)
  - preflight: ``python scripts/check_uqc_connectivity.py``

Does **not** use Matrix2 real hardware (backend.meta.uqc_target=iontrap-sim).
Public DNS cloud.unitaryqubit.com often times out; use intranet SERVER_HOST.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _load_dotenv() -> None:
    env_path = REPO / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = val


DEFAULT_EXP = REPO / "configs" / "example_h2_uqc_cloud_sim_md_ml.yaml"
DEFAULT_LOOP = REPO / "configs" / "example_h2_uqc_cloud_sim_qmlff_loop.yaml"
DEFAULT_OUT = REPO / "results" / "uqc_cloud_sim_md_ml_2rounds"


def _preflight_uqc(token: str, target: str) -> dict[str, object]:
    from uqc_client import UQC

    client = UQC(token=token)
    chips = client.get_chips()
    chip_info = client.get_chip_info()
    return {
        "chips": chips,
        "chip_info": chip_info,
        "target": target,
    }


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    _load_dotenv()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--experiment", type=Path, default=DEFAULT_EXP)
    ap.add_argument("--loop", type=Path, default=DEFAULT_LOOP)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    ap.add_argument(
        "--backend-profile",
        default="uqc_cloud",
        help="Backend preset (default uqc_cloud = 公司 UQC 内网真云)",
    )
    ap.add_argument("--token", default=None, help="UQC token (else UQC_API_TOKEN env)")
    ap.add_argument("--skip-preflight", action="store_true")
    args = ap.parse_args()

    token = (
        args.token or os.environ.get("UQC_API_TOKEN") or os.environ.get("USER_TOKEN") or ""
    ).strip()
    profile_id = str(args.backend_profile).strip().lower()
    if profile_id == "uqc_cloud" and not token:
        print(
            "ERROR: uqc_cloud profile requires UQC_API_TOKEN or --token (幺正云平台用户中心).",
            file=sys.stderr,
        )
        return 2
    if token:
        os.environ["UQC_API_TOKEN"] = token

    try:
        import pyscf  # noqa: F401
    except ImportError:
        print("ERROR: PySCF required. pip install -e '.[chem]'", file=sys.stderr)
        return 2
    try:
        import jax_md  # noqa: F401
        import qmlff  # noqa: F401
    except ImportError:
        print("ERROR: qmlff and jax-md required for online learning loop.", file=sys.stderr)
        return 2
    if profile_id == "uqc_cloud":
        try:
            import uqc_client  # noqa: F401
        except ImportError:
            print("ERROR: pip install uqc-client", file=sys.stderr)
            return 2

    from qchem_stack.backends.profiles import list_backend_profile_ids
    from qchem_stack.md_bridge import MdValidationLoopConfig, run_md_validation_loop

    if profile_id not in list_backend_profile_ids():
        print(f"ERROR: unknown backend profile {profile_id!r}", file=sys.stderr)
        return 2

    sys.path.insert(0, str(REPO / "scripts"))
    from backend_profile_helpers import (
        load_experiment_with_backend_profile,
        write_resolved_experiment_yaml,
    )

    exp_cfg, prof, _ = load_experiment_with_backend_profile(args.experiment, profile_id)
    args.output.mkdir(parents=True, exist_ok=True)
    resolved_yaml = write_resolved_experiment_yaml(exp_cfg, args.output, profile_id=profile_id)
    logging.info("backend profile=%s provider=%s", prof.profile_id, prof.provider)

    if prof.profile_id == "uqc_cloud" and prof.uqc_mode != "real":
        print("ERROR: uqc_cloud profile must use uqc_mode=real", file=sys.stderr)
        return 2
    target = str((exp_cfg.backend.meta or {}).get("uqc_target", "iontrap-sim"))

    server = os.environ.get("SERVER_HOST", "cloud.unitaryqubit.com")
    port = os.environ.get("SERVER_PORT", "8003")
    logging.info("UQC endpoint http://%s:%s", server, port)

    if profile_id == "uqc_cloud" and not args.skip_preflight:
        logging.info("UQC preflight (target=%s)...", target)
        try:
            info = _preflight_uqc(token, target)
            logging.info("UQC chips: %s", info.get("chips"))
            (args.output / "uqc_preflight.json").parent.mkdir(parents=True, exist_ok=True)
            (args.output / "uqc_preflight.json").write_text(
                json.dumps(info, indent=2, default=str), encoding="utf-8"
            )
        except Exception as exc:
            print(f"ERROR: UQC preflight failed: {exc}", file=sys.stderr)
            print(
                "Hint: company VPN / intranet may be required for cloud.unitaryqubit.com:8003",
                file=sys.stderr,
            )
            return 3

    loop_cfg = MdValidationLoopConfig.from_yaml(args.loop)
    if loop_cfg.max_rounds < 2:
        logging.warning("loop max_rounds=%s (expected 2 for this script)", loop_cfg.max_rounds)

    logging.info(
        "Starting MD validation loop (%s rounds, target=%s, output=%s)",
        loop_cfg.max_rounds,
        target,
        args.output,
    )
    summary = run_md_validation_loop(
        resolved_yaml,
        config=loop_cfg,
        output_dir=args.output,
    )
    summary["backend_profile"] = prof.profile_id
    summary["backend_provider"] = prof.provider
    (args.output / "md_validation_summary.json").write_text(
        json.dumps(summary, indent=2, default=str),
        encoding="utf-8",
    )
    out_json = args.output / "md_validation_summary.json"
    logging.info("Done. summary written to %s", out_json)
    logging.info(
        "converged=%s n_total_frames=%s", summary.get("converged"), summary.get("n_total_frames")
    )
    for r in summary.get("rounds") or []:
        logging.info(
            "round %s: md_frames=%s max_abs_delta=%s",
            r.get("round_index"),
            r.get("n_md_frames_sampled"),
            r.get("max_abs_delta_hartree"),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
