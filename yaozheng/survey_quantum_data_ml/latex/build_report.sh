#!/usr/bin/env bash
# Build LaTeX survey PDF. Tries local xelatex, then Docker texlive.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
DOCS="$(cd "$ROOT/../.." && pwd)"
BIB="$DOCS/quantum_data_ml_survey.bib"

cd "$ROOT"

build_local() {
  command -v xelatex >/dev/null && command -v bibtex >/dev/null
}

build_docker() {
  command -v docker >/dev/null && docker info >/dev/null 2>&1
}

run_local() {
  echo "[build] local xelatex + bibtex"
  xelatex -interaction=nonstopmode main.tex
  bibtex main
  xelatex -interaction=nonstopmode main.tex
  xelatex -interaction=nonstopmode main.tex
}

run_docker() {
  echo "[build] Docker texlive/texlive"
  docker run --rm \
    -v "$ROOT:/work" \
    -v "$DOCS:/docs:ro" \
    -w /work \
    texlive/texlive:latest \
    bash -lc '
      set -e
      ln -sf /docs/quantum_data_ml_survey.bib /work/quantum_data_ml_survey.bib 2>/dev/null || true
      xelatex -interaction=nonstopmode main.tex
      bibtex main || true
      xelatex -interaction=nonstopmode main.tex
      xelatex -interaction=nonstopmode main.tex
    '
}

if build_local; then
  run_local
elif build_docker; then
  run_docker
else
  cat >&2 <<EOF
ERROR: Neither local xelatex nor Docker texlive available.

Install locally (Debian/Ubuntu):
  sudo apt-get install texlive-xetex texlive-lang-chinese texlive-latex-recommended

Or install Docker and re-run:
  docker pull texlive/texlive:latest
  ./build_report.sh
EOF
  exit 1
fi

if [[ -f main.pdf ]]; then
  echo "[ok] $ROOT/main.pdf"
  ls -lh main.pdf
else
  echo "ERROR: main.pdf not produced" >&2
  exit 1
fi
