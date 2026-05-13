#!/usr/bin/env bash
# Minimal gate bundle for ninety-day plan (D88): pytest + parity export sampling.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python -m pytest -q
python scripts/check_parity_export_sample.py
python scripts/sample_pipeline_configs.py
echo "verify_ninety_day_gates: OK"
