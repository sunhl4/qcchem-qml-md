@echo off
setlocal
cd /d "%~dp0\..\survey_quantum_data_ml\cheatsheets"

where pandoc >nul 2>&1
if errorlevel 1 (
  echo ERROR: pandoc not found. Install from https://pandoc.org/installing.html
  exit /b 1
)

pandoc 00_index.md cheatsheet_decision.md cheatsheet_many_body.md cheatsheet_qem_surrogate.md cheatsheet_hep.md cheatsheet_finance.md cheatsheet_life_chem_materials.md cheatsheet_cv_sensing_security.md -o cheatsheets_all.pdf --pdf-engine=xelatex -V geometry:margin=1.8cm -V fontsize=10pt

if exist cheatsheets_all.pdf (
  echo [ok] cheatsheets_all.pdf
) else (
  echo ERROR: PDF not produced
  exit /b 1
)
exit /b 0
