#!/usr/bin/env bash
# Bootstrap a local editable install for contributors.
# Usage: ./scripts/bootstrap_dev.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PY="${QCHEM_STACK_PYTHON:-python3}"
if [[ ! -d .venv ]]; then
  echo "== create .venv =="
  "$PY" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -U pip
echo "== pip install -e '.[dev]' (no uqc by default; use .[dev-uqc] for cloud) =="
pip install -e ".[dev]"

cat <<'EOF'

Next steps:
  ./scripts/release_precheck.sh --quick
  qchem-run --list-scenarios
  cd docusaurus-site && npm ci && npm start   # docs at /qcchem-qml-md/

Optional:
  pip install -e ".[dev-uqc]"     # UQC experimental
  pip install -e ".[gqe]"         # GPT-QE / JAX
EOF
