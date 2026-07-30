$ErrorActionPreference = "Continue"
# List the uqc figure directories on D:
$dirs = Get-ChildItem -Path "D:\Yaozheng" -Recurse -Filter "uqc" -Directory -Depth 6 -ErrorAction SilentlyContinue
foreach ($d in $dirs) {
    Write-Host "=== $($d.FullName) ==="
    Get-ChildItem -Path $d.FullName -ErrorAction SilentlyContinue | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize
}
# Also check for the report markdown files
Write-Host "=== Looking for .md reports in D:\Yaozheng ==="
Get-ChildItem -Path "D:\Yaozheng" -Recurse -Filter "*.md" -Depth 6 -ErrorAction SilentlyContinue |
    Select-Object FullName, Length, LastWriteTime | Format-Table -AutoSize
