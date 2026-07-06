@echo off
setlocal
cd /d "%~dp0\..\survey_quantum_data_ml\latex"

where xelatex >nul 2>&1
if errorlevel 1 (
  echo ERROR: xelatex not found.
  echo Install MiKTeX or TeX Live for Windows, then add bin to PATH.
  echo   https://miktex.org/download
  exit /b 1
)

xelatex -interaction=nonstopmode main.tex
bibtex main
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex

if exist main.pdf (
  echo [ok] main.pdf
) else (
  echo ERROR: main.pdf not produced
  exit /b 1
)
exit /b 0
