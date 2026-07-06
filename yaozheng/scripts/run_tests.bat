@echo off
setlocal
cd /d "%~dp0\.."
if not exist .venv\Scripts\python.exe (
  echo Run setup.bat first.
  exit /b 1
)
set PY=.venv\Scripts\python.exe
"%PY%" -m pytest survey_quantum_data_ml\schema\test_quantum_data_store.py -q
exit /b %ERRORLEVEL%
