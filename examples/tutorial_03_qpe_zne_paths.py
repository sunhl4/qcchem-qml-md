#!/usr/bin/env python3
"""Tutorial 3: ZNE circuit-fold YAML + QPE dual-track / packaged QPE references."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    env = {**__import__("os").environ, "PYTHONPATH": str(root / "src")}
    print("tutorial_03: config-only export for ZNE circuit-fold demo YAML")
    subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "export_parity_criteria_table.py"),
            str(root / "configs" / "example_h2_zne_circuit_fold.yaml"),
        ],
        cwd=str(root),
        check=True,
        env=env,
        stdout=subprocess.DEVNULL,
    )
    try:
        import pyscf  # noqa: F401
    except ImportError:
        print("tutorial_03: skip pipeline demos (PySCF missing); QPE script still runnable.")
    else:
        from qchem_stack.config import load_experiment_config
        from qchem_stack.orchestration.pipeline import run_pipeline_sync

        p_qpe = root / "configs" / "qpe_dual_track_demo.yaml"
        out = run_pipeline_sync(load_experiment_config(p_qpe), cfg_path=p_qpe)
        print("tutorial_03: qpe_demo_track schema", (out.get("qpe_demo_track") or {}).get("schema"))

        p_zne = root / "configs" / "example_h2_zne_circuit_fold.yaml"
        out_z = run_pipeline_sync(load_experiment_config(p_zne), cfg_path=p_zne)
        print("tutorial_03: zne_mode", (out_z.get("protocol_counts") or {}).get("zne_mode"))

    subprocess.run(
        [sys.executable, str(root / "scripts" / "run_qpe_track_demo.py")],
        cwd=str(root),
        check=True,
        env=env,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
