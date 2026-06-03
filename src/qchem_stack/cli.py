"""Console entry points for qchem-stack (``qchem-run``, ``qchem-export-parity``)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from qchem_stack.exceptions import PipelineError


def _repo_root() -> Path:
    """Repository root (contains ``scripts/``), for export helper in editable installs."""
    here = Path(__file__).resolve().parent
    for candidate in (here.parent.parent, here.parent):
        if (candidate / "scripts" / "export_parity_criteria_table.py").is_file():
            return candidate
    raise SystemExit(
        "qchem-export-parity: scripts/export_parity_criteria_table.py not found. "
        "Use an editable install from the repository root, or run:\n"
        "  python scripts/export_parity_criteria_table.py <config.yaml>"
    )


def main_run(argv: list[str] | None = None) -> int:
    """Run the YAML pipeline (``qchem-run``)."""
    ap = argparse.ArgumentParser(description="Run qchem-stack pipeline from experiment YAML.")
    ap.add_argument(
        "config",
        type=Path,
        nargs="?",
        default=None,
        help="Path to ExperimentConfig YAML (omit with --list-scenarios)",
    )
    ap.add_argument(
        "--list-scenarios",
        action="store_true",
        help="Print onboarding scenario → config mapping and exit",
    )
    ap.add_argument(
        "--job-db",
        type=Path,
        default=None,
        help="Optional SQLite path to enqueue async Pauli protocol jobs",
    )
    ap.add_argument(
        "--json-summary",
        action="store_true",
        help="Print a small JSON summary (scf_energy, variational, pauli) to stdout",
    )
    args = ap.parse_args(argv)
    if args.list_scenarios:
        from qchem_stack.config.scenarios import list_scenarios_text

        print(list_scenarios_text(), end="")
        return 0
    if args.config is None:
        ap.error("config path required unless --list-scenarios is set")
    cfg_path = args.config.resolve()
    if not cfg_path.is_file():
        print(f"config not found: {cfg_path}", file=sys.stderr)
        return 2
    try:
        from qchem_stack.orchestration.pipeline import run_pipeline_from_config

        out = run_pipeline_from_config(cfg_path, job_db=args.job_db)
    except PipelineError as exc:
        print(f"pipeline failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"pipeline failed: {exc}", file=sys.stderr)
        return 1
    if args.json_summary:
        summary = {
            "experiment_id": out.get("experiment_id"),
            "scf_energy": out.get("scf_energy"),
            "energy_after_variational": out.get("energy_after_variational"),
            "energy_pauli_protocol": out.get("energy_pauli_protocol"),
        }
        json.dump(summary, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        scf = out.get("scf_energy")
        var = out.get("energy_after_variational")
        pauli = out.get("energy_pauli_protocol")
        print(f"scf_energy={scf}")
        if var is not None:
            print(f"energy_after_variational={var}")
        if pauli is not None:
            print(f"energy_pauli_protocol={pauli}")
    return 0


def main_export_parity(argv: list[str] | None = None) -> int:
    """Export parity / Methods table JSON (``qchem-export-parity``)."""
    root = _repo_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    from scripts.export_parity_criteria_table import main as export_main

    if argv is not None:
        sys.argv = ["qchem-export-parity", *argv]
    export_main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main_run())
