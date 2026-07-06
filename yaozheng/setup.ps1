# Standalone venv setup (PowerShell)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python not found. Install Python 3.10+ and retry."
}

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

& .\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt

Write-Host "`nOK. Activate: .\.venv\Scripts\Activate.ps1"
Write-Host "Then run: scripts\validate_examples.bat"
