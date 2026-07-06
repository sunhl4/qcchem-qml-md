@echo off
setlocal
cd /d "%~dp0\.."
if not exist .venv\Scripts\python.exe (
  echo Run setup.bat first.
  exit /b 1
)
set PY=.venv\Scripts\python.exe
set SCHEMA=survey_quantum_data_ml\schema

"%PY%" "%SCHEMA%\validate_record.py" "%SCHEMA%\examples\hybrid_many_body.json"
if errorlevel 1 exit /b 1
"%PY%" "%SCHEMA%\validate_record.py" "%SCHEMA%\examples\native_shadow_only.json"
echo All examples OK.
exit /b 0
