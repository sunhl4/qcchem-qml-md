$ErrorActionPreference = "Continue"
# Search D: drive for the report and figures
Write-Host "=== Searching D: for 述职报告 ==="
Get-ChildItem -Path "D:\" -Recurse -Filter "述职报告*.md" -Depth 6 -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty FullName
Write-Host "=== Searching D: for shuzhi folders ==="
Get-ChildItem -Path "D:\" -Recurse -Filter "shuzhi*" -Directory -Depth 5 -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty FullName
Write-Host "=== Searching D: for uqc figure folders ==="
Get-ChildItem -Path "D:\" -Recurse -Filter "uqc" -Directory -Depth 6 -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty FullName
