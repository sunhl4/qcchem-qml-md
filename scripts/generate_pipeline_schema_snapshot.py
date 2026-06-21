#!/usr/bin/env python3
"""Write pipeline / run-summary JSON Schema snapshots under docs/generated/."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "generated"

PIPELINE_RESULT_V1_SCHEMA: dict[str, object] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://github.com/sunhl4/qcchem-qml-md/schemas/pipeline_result_v1.schema.json",
    "title": "pipeline_result_v1",
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "schema": {"const": "pipeline_result_v1"},
        "scf_energy": {"type": "number"},
        "energy_after_variational": {"type": "number"},
        "energy_pauli_protocol": {"type": "number"},
        "angles": {"type": "array", "items": {"type": "number"}},
        "nfev": {"type": "integer"},
        "algorithm": {"type": "string"},
        "pre_quantum_input": {"type": "object", "additionalProperties": True},
        "resource_summary": {
            "type": "object",
            "additionalProperties": True,
            "properties": {
                "n_circuits": {"type": "integer"},
                "sum_shots": {"type": "integer"},
                "n_qubits": {"type": "integer"},
                "pauli_averaging_protocol_ran": {"type": "boolean"},
            },
        },
        "repro": {
            "type": "object",
            "additionalProperties": True,
            "properties": {
                "parity_snapshot": {"type": "object", "additionalProperties": True},
                "run_summary": {"$ref": "run_summary_v1.schema.json"},
                "run_context": {"type": "object", "additionalProperties": True},
                "pipeline_profile": {"type": "object", "additionalProperties": True},
            },
        },
        "protocol_counts": {"type": "object", "additionalProperties": True},
        "job": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "job_id": {"type": "string"},
                "protocol_hash": {"type": "string"},
                "store": {"type": "string"},
            },
            "required": ["job_id", "protocol_hash", "store"],
        },
    },
    "required": ["repro"],
}

RUN_SUMMARY_V1_SCHEMA: dict[str, object] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://github.com/sunhl4/qcchem-qml-md/schemas/run_summary_v1.schema.json",
    "title": "run_summary_v1",
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "stages_completed": {"type": "array", "items": {"type": "string"}},
        "scf_energy": {"type": "number"},
        "energy_pauli_protocol": {"type": "number"},
        "quantum_algorithm": {"type": "string"},
        "quantum_algorithm_yaml": {"type": "string"},
        "pipeline_total_wall_ms": {"type": "number"},
        "pipeline_slowest_stage": {"type": "string"},
        "protocol_total_shots_budget": {"type": "integer"},
        "protocol_n_measurement_circuits": {"type": "integer"},
        "protocol_shots_per_circuit_effective": {"type": "number"},
        "protocol_energy_stderr": {"type": "number"},
        "protocol_expectation_source": {"type": "string"},
        "protocol_zne_mode": {"type": "string"},
        "stage_failed": {"type": "string"},
        "error_type": {"type": "string"},
        "error_message": {"type": "string"},
    },
}


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_snapshots() -> dict[str, dict[str, object]]:
    return {
        "pipeline_result_v1.schema.json": PIPELINE_RESULT_V1_SCHEMA,
        "run_summary_v1.schema.json": RUN_SUMMARY_V1_SCHEMA,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if on-disk snapshots differ from current schema definitions.",
    )
    args = parser.parse_args(argv)
    snapshots = _build_snapshots()
    if args.check:
        for name, expected in snapshots.items():
            path = OUT_DIR / name
            if not path.is_file():
                print(f"missing snapshot {path.relative_to(ROOT)}", file=sys.stderr)
                return 1
            on_disk = json.loads(path.read_text(encoding="utf-8"))
            if on_disk != expected:
                print(f"stale snapshot {path.relative_to(ROOT)}", file=sys.stderr)
                return 1
        print("pipeline_schema_snapshots_ok")
        return 0

    for name, payload in snapshots.items():
        _write(OUT_DIR / name, payload)
        print(f"wrote docs/generated/{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
