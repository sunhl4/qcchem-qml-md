#!/usr/bin/env bash
# Pre-release quality gate (mirrors maintainer checklist; no git operations).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PY="${QCHEM_STACK_PYTHON:-python3}"

echo "== ruff check =="
"$PY" -m ruff check src/qchem_stack tests scripts examples

echo "== ruff format (check) =="
"$PY" -m ruff format --check src/qchem_stack tests scripts examples

echo "== import layers =="
"$PY" scripts/check_import_layers.py

echo "== comparative backlog =="
"$PY" scripts/check_comparative_execution_backlog.py

echo "== pytest (core) =="
"$PY" -m pytest tests -q --tb=short -m "not slow and not perf"

echo "== parity export sample =="
"$PY" scripts/check_parity_export_sample.py

echo "== doc links =="
"$PY" scripts/check_doc_links.py

echo "== configs catalog snippet =="
"$PY" scripts/generate_configs_catalog.py
"$PY" scripts/generate_configs_catalog.py --check

echo "== coverage thresholds (requires prior pytest --cov) =="
"$PY" scripts/check_coverage_thresholds.py || {
  echo "hint: run pytest tests --cov=src/qchem_stack first" >&2
  exit 1
}

if command -v npm >/dev/null 2>&1 && [[ -f docusaurus-site/package.json ]]; then
  echo "== docusaurus build =="
  (cd docusaurus-site && npm ci && npm run build)
else
  echo "skip docusaurus (npm not available)"
fi

echo "release_precheck: OK"
