"""Console entry points for qchem-stack (``qchem-run``, ``qchem-export-parity``)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from qchem_stack.exceptions import PipelineError


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
        "--scenario",
        metavar="ID",
        default=None,
        help="Run the primary YAML for an onboarding scenario (see --list-scenarios)",
    )
    ap.add_argument(
        "--set",
        action="append",
        default=[],
        metavar="KEY=VAL",
        help="Dotted override applied after --scenario (e.g. quantum.vqe.max_iter=50)",
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
    if args.config is not None and args.scenario is not None:
        ap.error("pass either a config path or --scenario, not both")
    if args.scenario is not None:
        from qchem_stack.config import ExperimentConfig
        from qchem_stack.config.migrations import migrate_config
        from qchem_stack.config.migrations_v2_to_v3 import compile_scenario_v3

        try:
            from qchem_stack.config.scenarios import scenario_base_config_path, scenario_config_path

            raw = compile_scenario_v3(
                scenario_id=args.scenario,
                dotted_sets=list(args.set or []),
            )
            raw = migrate_config(raw, from_version="3", to_version="2")
            cfg_path = scenario_config_path(args.scenario)
            geometry_base = scenario_base_config_path(args.scenario).parent
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        try:
            from qchem_stack.orchestration.pipeline import run_pipeline_sync

            cfg = ExperimentConfig.from_yaml_dict(raw, geometry_files_base_dir=geometry_base)
            out = run_pipeline_sync(cfg, cfg_path=cfg_path)
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
            print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    elif args.config is None:
        ap.error("config path or --scenario required unless --list-scenarios is set")
    else:
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
    ap = argparse.ArgumentParser(description="Export parity / falsifiability table fields.")
    ap.add_argument("config", type=Path, help="Experiment YAML path")
    ap.add_argument("--results", type=Path, default=None, help="Optional JSON with pipeline output")
    ap.add_argument(
        "--max-pauli-export",
        type=int,
        default=None,
        metavar="N",
        help="Cap exported hamiltonian_pauli_strings mirror list length when using --results",
    )
    args = ap.parse_args(argv)
    from qchem_stack.protocols.parity_criteria_export import export_parity_criteria_table

    out = export_parity_criteria_table(
        args.config,
        results_path=args.results,
        max_pauli_export=args.max_pauli_export,
    )
    json.dump(out, sys.stdout, indent=2, sort_keys=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main_run())
