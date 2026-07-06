#!/usr/bin/env bash
# Merge cheatsheets into one PDF via pandoc (requires pandoc + xelatex).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT="$ROOT/cheatsheets_all.pdf"

if ! command -v pandoc >/dev/null; then
  echo "ERROR: pandoc not found. Install: sudo apt-get install pandoc" >&2
  exit 1
fi

FILES=(
  "$ROOT/00_index.md"
  "$ROOT/cheatsheet_decision.md"
  "$ROOT/cheatsheet_many_body.md"
  "$ROOT/cheatsheet_qem_surrogate.md"
  "$ROOT/cheatsheet_hep.md"
  "$ROOT/cheatsheet_finance.md"
  "$ROOT/cheatsheet_life_chem_materials.md"
  "$ROOT/cheatsheet_cv_sensing_security.md"
)

pandoc "${FILES[@]}" -o "$OUT" \
  --pdf-engine=xelatex \
  -V geometry:margin=1.8cm \
  -V fontsize=10pt \
  -V CJKmainfont="Noto Sans CJK SC" \
  2>/dev/null || pandoc "${FILES[@]}" -o "$OUT" --pdf-engine=xelatex -V geometry:margin=1.8cm

echo "[ok] $OUT"
ls -lh "$OUT"
