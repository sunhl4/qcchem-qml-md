#!/usr/bin/env bash
# Pre-release quality gate (mirrors maintainer checklist; no git operations).
# Usage:
#   ./scripts/release_precheck.sh              # full gate (coverage, docusaurus when npm present)
#   ./scripts/release_precheck.sh --quick      # skip docusaurus; still runs pytest + coverage
#   QCHEM_STACK_PYTHON=python ./scripts/release_precheck.sh   # use conda/venv interpreter
#   QCHEM_RELEASE_FULL=1 ./scripts/release_precheck.sh        # append L3 benchmarks when PySCF present
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

QUICK=0
for arg in "$@"; do
  case "$arg" in
    --quick) QUICK=1 ;;
    --check-code-health)
      echo "note: --check-code-health is deprecated; code health always runs" >&2
      ;;
    -h|--help)
      cat <<EOF
usage: $0 [--quick]

Environment:
  QCHEM_STACK_PYTHON   Python interpreter (default: python3 or .venv/bin/python)
  QCHEM_RELEASE_FULL=1   Also run L3 benchmarks when PySCF is installed
  QCHEM_PYRIGHT_FULL=1   Full-stack pyright (opt-in; default off for 1.1 — deferred to 1.2)

See docs/engineering/v1_1_acceptance.md and docs/engineering/pypi_release.md
EOF
      exit 0
      ;;
  esac
done

PY="${QCHEM_STACK_PYTHON:-python3}"
if [[ -x "$ROOT/.venv/bin/python" ]] && [[ -z "${QCHEM_STACK_PYTHON:-}" ]]; then
  PY="$ROOT/.venv/bin/python"
fi

PKG_VER="$("$PY" -c "import qchem_stack; print(qchem_stack.__version__)" 2>/dev/null || echo "?")"
PYPROJECT_VER="$("$PY" -c "
import tomllib
from pathlib import Path
data = tomllib.loads(Path('pyproject.toml').read_text(encoding='utf-8'))
print(data['project']['version'])
")"
echo "== interpreter: $PY (qchem_stack $PKG_VER; pyproject $PYPROJECT_VER) =="
if [[ "$PKG_VER" != "$PYPROJECT_VER" ]]; then
  echo "error: installed qchem_stack.__version__ ($PKG_VER) must match pyproject.toml version ($PYPROJECT_VER)" >&2
  echo "hint: export QCHEM_STACK_PYTHON=$ROOT/.venv/bin/python" >&2
  echo "hint: pip install -e \".[dev,chem]\" with that interpreter" >&2
  exit 1
fi

echo "== ruff check =="
"$PY" -m ruff check src/qchem_stack tests scripts examples

echo "== ruff format (check) =="
"$PY" -m ruff format --check src/qchem_stack tests scripts examples

echo "== import layers =="
"$PY" scripts/check_import_layers.py

echo "== test layout =="
"$PY" scripts/check_test_layout.py

echo "== code health regression =="
"$PY" scripts/check_code_health_regression.py

echo "== doc test paths (Tier-1) =="
"$PY" scripts/check_doc_test_paths.py

echo "== import linter contracts =="
if "$PY" -c "import importlinter" 2>/dev/null; then
  LINT_IMPORTS="$(dirname "$PY")/lint-imports"
  if [[ -x "$LINT_IMPORTS" ]]; then
    "$LINT_IMPORTS"
  elif command -v lint-imports >/dev/null 2>&1; then
    lint-imports
  else
    echo "skip lint-imports (lint-imports CLI not found beside QCHEM_STACK_PYTHON)" >&2
  fi
else
  echo "skip lint-imports (pip install import-linter)" >&2
fi

echo "== comparative backlog =="
"$PY" scripts/check_comparative_execution_backlog.py

echo "== product gap categories =="
"$PY" -c "from qchem_stack.protocols.product_contract import validate_product_gap_categories; errs=validate_product_gap_categories(); assert not errs, errs"

echo "== scenario-first CLI smoke =="
"$PY" -c "from qchem_stack.cli import main_run; raise SystemExit(main_run(['--scenario', 'minimal_vqe', '--json-summary']))"

echo "== precomputed pipeline smoke =="
"$PY" scripts/smoke_pipeline.py --precomputed-only

echo "== pytest (core + coverage) =="
"$PY" -m pytest tests -q --tb=short -m "not slow and not perf" --cov=src/qchem_stack --cov-report=html

echo "== api auth middleware =="
QCHEM_STACK_DISABLE_RATE_LIMIT=1 "$PY" -m pytest tests/api/test_api_auth_middleware.py -q --tb=short --no-cov

echo "== sdk doc sync =="
"$PY" scripts/check_sdk_docs_sync.py

echo "== parity export sample =="
"$PY" scripts/check_parity_export_sample.py

echo "== doc links =="
"$PY" scripts/check_doc_links.py

echo "== configs catalog snippet =="
"$PY" scripts/generate_configs_catalog.py
"$PY" scripts/generate_configs_catalog.py --check

echo "== examples gallery sync =="
"$PY" scripts/generate_examples_gallery.py
"$PY" scripts/generate_examples_gallery.py --check

echo "== tutorial verify blocks =="
"$PY" scripts/check_tutorial_verify_blocks.py

echo "== coverage thresholds (requires prior pytest --cov) =="
"$PY" scripts/check_coverage_thresholds.py || {
  echo "hint: run pytest tests --cov=src/qchem_stack first" >&2
  exit 1
}

echo "== openapi snapshot =="
"$PY" scripts/generate_openapi_snapshot.py --check

echo "== pipeline JSON schema snapshots =="
"$PY" scripts/generate_pipeline_schema_snapshot.py --check

echo "== pyright (config + repro + chem/solvers, mirrors CI typecheck-config) =="
"$PY" -m pyright src/qchem_stack/config src/qchem_stack/repro src/qchem_stack/exceptions.py
"$PY" -m pyright src/qchem_stack/chem/solvers

echo "== pyright (full stack) =="
if [[ "${QCHEM_PYRIGHT_FULL:-0}" == "1" ]]; then
  "$PY" -m pyright src/qchem_stack
else
  echo "skip full-stack pyright (QCHEM_PYRIGHT_FULL=0)" >&2
fi

echo "== pip-audit (dev install surface) =="
if "$PY" -m pip show pip-audit >/dev/null 2>&1; then
  pip-audit --skip-editable --desc on
else
  echo "skip pip-audit dev (pip install pip-audit)" >&2
fi

echo "== pip-audit (chem,api install surface) =="
if "$PY" -m pip show pip-audit >/dev/null 2>&1; then
  "$PY" -m pip install -q -e ".[chem,api]" 2>/dev/null || true
  pip-audit --skip-editable --desc on || {
    echo "warn: pip-audit chem,api reported issues (see pip-audit.toml allowlist)" >&2
  }
else
  echo "skip pip-audit chem,api (pip install pip-audit)" >&2
fi

echo "== pre-quantum docs sync =="
"$PY" scripts/sync_pre_quantum_docs.py
git diff --exit-code docs/pre_quantum_yaml_matrix.md "docs/技术文档_双线路经典输入与统一PreQuantumInput契约.md"

echo "== config reference snippets sync =="
"$PY" scripts/generate_config_reference_snippets.py --check

echo "== config combo matrix =="
"$PY" scripts/check_config_combo_matrix.py

echo "== constraints freshness =="
if "$PY" -c "import piptools" 2>/dev/null; then
  "$PY" scripts/check_constraints_freshness.py
else
  echo "skip constraints freshness (pip install pip-tools)" >&2
fi

echo "== examples importable =="
"$PY" scripts/check_examples_importable.py

echo "== examples tutorials smoke =="
"$PY" examples/run_all_smoke.py

if [[ "$QUICK" -eq 0 ]]; then
  echo "== notebook nbmake =="
  if "$PY" -c "import nbmake" 2>/dev/null; then
    "$PY" -m pytest --nbmake notebooks/ --nbmake-timeout=120 -q --no-cov
  else
    echo "skip nbmake (pip install nbmake)" >&2
  fi
else
  echo "skip nbmake (--quick)"
fi

if [[ "${QCHEM_RELEASE_FULL:-}" == "1" ]]; then
  echo "== note: QCHEM_RELEASE_FULL also expects test-cross-platform green on main (see v1_0_acceptance.md) =="
  echo "== L3 benchmarks (QCHEM_RELEASE_FULL) =="
  if "$PY" -c "import pyscf" 2>/dev/null; then
    QCHEM_RUN_L3=1 "$PY" -m pytest -m l3 -q --tb=short --no-cov
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
