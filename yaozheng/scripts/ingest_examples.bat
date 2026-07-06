@echo off
setlocal
cd /d "%~dp0\.."
if not exist .venv\Scripts\python.exe (
  echo Run setup.bat first.
  exit /b 1
)
set PY=.venv\Scripts\python.exe
set CLI=survey_quantum_data_ml\schema\ingest_cli.py
set EX=survey_quantum_data_ml\schema\examples

"%PY%" "%CLI%" ingest "%EX%"
"%PY%" "%CLI%" list
exit /b 0
