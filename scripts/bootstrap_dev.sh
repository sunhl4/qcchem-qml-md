#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

.venv/bin/python -m pip install -U pip
.venv/bin/pip install -e ".[dev]"

export QCHEM_STACK_PYTHON="$ROOT/.venv/bin/python"
"$ROOT/scripts/venv-run" python "$ROOT/scripts/smoke_pipeline.py" --precomputed-only

echo "Bootstrap OK. Use: export QCHEM_STACK_PYTHON=$ROOT/.venv/bin/python"
