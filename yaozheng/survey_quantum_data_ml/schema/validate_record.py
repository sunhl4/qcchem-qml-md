#!/usr/bin/env python3
"""Validate quantum experiment record JSON against Pydantic model."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running from repo root or schema directory
_SCHEMA_DIR = Path(__file__).resolve().parent
if str(_SCHEMA_DIR) not in sys.path:
    sys.path.insert(0, str(_SCHEMA_DIR))

from quantum_experiment_record import QuantumExperimentRecord  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", type=Path, help="Record JSON to validate")
    args = parser.parse_args()

    payload = json.loads(args.json_file.read_text(encoding="utf-8"))
    record = QuantumExperimentRecord.model_validate(payload)
    print(f"OK: {record.id} path_type={record.path_type.value} domain={record.problem.domain.value}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"VALIDATION FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
