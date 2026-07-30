$ErrorActionPreference = "Continue"
# Find the report on Windows side
$candidates = @(
    "C:\Users\Administrator\Documents",
    "C:\Users\Administrator\Desktop",
    "C:\Users\Public\Documents",
    "D:\",
    "E:\"
)
foreach ($base in $candidates) {
    if (Test-Path $base) {
        Get-ChildItem -Path $base -Recurse -Filter "述职报告_合订本.md" -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty FullName
    }
}
# Also check common WSL-linked paths
Get-ChildItem -Path "C:\Users" -Recurse -Filter "述职报告_合订本.md" -Depth 5 -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty FullName
