@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
  echo ERROR: Python not found. Install Python 3.10+ from https://www.python.org/
  exit /b 1
)

if not exist .venv (
  echo Creating virtual environment...
  python -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install -U pip
pip install -r requirements.txt

echo.
echo OK. Next steps:
echo   .venv\Scripts\activate.bat
echo   scripts\validate_examples.bat
echo   scripts\ingest_examples.bat
exit /b 0
