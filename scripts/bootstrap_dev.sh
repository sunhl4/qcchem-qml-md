#!/usr/bin/env bash
# Create .venv and install qchem-stack with dev extras (CI-parity local setup).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PY="${QCHEM_STACK_PYTHON:-python3}"
if ! command -v "$PY" >/dev/null 2>&1; then
  echo "error: Python not found: $PY" >&2
  echo "hint: export QCHEM_STACK_PYTHON=/path/to/python3.10+" >&2
  exit 1
fi
"$PY" -m venv .venv
.venv/bin/pip install -U pip
.venv/bin/pip install -e ".[dev]"
echo "Done. Run: ./scripts/venv-run pytest tests -q --tb=short"
