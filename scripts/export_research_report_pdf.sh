#!/usr/bin/env bash
# Export docs/research/量子计算化学软件平台-行业与竞品调研报告.md to PDF via pandoc + XeLaTeX.
#
# Prerequisites (macOS):
#   brew install pandoc
#   brew install --cask mactex   # or: brew install basictex
#
# Chinese fonts (pick one installed on your system):
#   macOS: PingFang SC, Songti SC, STSong, Heiti SC
#   Linux: Noto Serif CJK SC, WenQuanYi Zen Hei
#
# Usage:
#   ./scripts/export_research_report_pdf.sh
#   ./scripts/export_research_report_pdf.sh /path/to/output.pdf

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INPUT="${ROOT}/docs/research/量子计算化学软件平台-行业与竞品调研报告.md"
OUTPUT="${1:-${ROOT}/docs/research/量子计算化学软件平台-行业与竞品调研报告.pdf}"

if [[ ! -f "${INPUT}" ]]; then
  echo "error: report not found: ${INPUT}" >&2
  exit 1
fi

if ! command -v pandoc >/dev/null 2>&1; then
  echo "error: pandoc not found. Install: brew install pandoc" >&2
  echo "Manual export: open the .md in Typora/VS Code and export to PDF." >&2
  exit 1
fi

# Prefer XeLaTeX for Unicode/CJK; fall back to wkhtmltopdf if no TeX.
PDF_ENGINE="xelatex"
if ! command -v xelatex >/dev/null 2>&1; then
  if command -v wkhtmltopdf >/dev/null 2>&1; then
    PDF_ENGINE="wkhtmltopdf"
  else
    echo "warning: xelatex not found; trying default pdflatex (CJK may fail)." >&2
    PDF_ENGINE="pdflatex"
  fi
fi

mkdir -p "$(dirname "${OUTPUT}")"

if [[ "${PDF_ENGINE}" == "xelatex" ]]; then
  HEADER="$(mktemp)"
  cat > "${HEADER}" <<'LATEX'
\usepackage{xeCJK}
\setCJKmainfont{PingFang SC}
\setCJKsansfont{PingFang SC}
\setCJKmonofont{PingFang SC}
LATEX
  pandoc "${INPUT}" \
    --from markdown \
    --to pdf \
    --pdf-engine=xelatex \
    -H "${HEADER}" \
    -V geometry:margin=2.5cm \
    -V fontsize=11pt \
    -V documentclass=article \
    --toc \
    --toc-depth=3 \
    --number-sections \
    -o "${OUTPUT}"
  rm -f "${HEADER}"
elif [[ "${PDF_ENGINE}" == "wkhtmltopdf" ]]; then
  pandoc "${INPUT}" \
    --from markdown \
    --to html5 \
    --standalone \
    --toc \
    --toc-depth=3 \
    -o "${OUTPUT%.pdf}.html"
  wkhtmltopdf "${OUTPUT%.pdf}.html" "${OUTPUT}"
else
  pandoc "${INPUT}" \
    --from markdown \
    --to pdf \
    --toc \
  -o "${OUTPUT}"
fi

echo "Wrote: ${OUTPUT}"

# Character count helper (Chinese hanzi only)
python3 - <<'PY' "${INPUT}"
import re, sys
text = open(sys.argv[1], encoding="utf-8").read()
han = len(re.findall(r"[\u4e00-\u9fff]", text))
print(f"Report Chinese characters (hanzi): {han}")
PY
