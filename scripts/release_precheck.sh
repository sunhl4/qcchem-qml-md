#!/usr/bin/env bash
# Pre-release quality gate (mirrors maintainer checklist; no git operations).
# Usage: ./scripts/release_precheck.sh [--quick]   # --quick skips docusaurus build
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

QUICK=0
for arg in "$@"; do
  case "$arg" in
    --quick) QUICK=1 ;;
    -h|--help)
      echo "usage: $0 [--quick]" >&2
      exit 0
      ;;
  esac
done

PY="${QCHEM_STACK_PYTHON:-python3}"
if [[ -x "$ROOT/.venv/bin/python" ]] && [[ -z "${QCHEM_STACK_PYTHON:-}" ]]; then
  PY="$ROOT/.venv/bin/python"
fi

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

echo "== openapi snapshot =="
"$PY" scripts/generate_openapi_snapshot.py --check

if [[ "${QCHEM_RELEASE_FULL:-}" == "1" ]]; then
  echo "== L3 benchmarks (QCHEM_RELEASE_FULL) =="
  if "$PY" -c "import pyscf" 2>/dev/null; then
    QCHEM_RUN_L3=1 "$PY" -m pytest -m l3 -q --tb=short
    "$PY" scripts/l3_algorithm_benchmark_report.py --output /tmp/l3_benchmark.json
  else
    echo "skip L3 (PySCF not installed)" >&2
  fi
fi

if [[ "$QUICK" -eq 0 ]] && command -v npm >/dev/null 2>&1 && [[ -f docusaurus-site/package.json ]]; then
  echo "== docusaurus build =="
  (cd docusaurus-site && npm ci && npm run build)
else
  echo "skip docusaurus (--quick or npm not available)"
fi

echo "release_precheck: OK"
