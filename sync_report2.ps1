$ErrorActionPreference = "Stop"
$src = "\\wsl.localhost\Ubuntu\home\sunhl\projects\qchem_qml_md\docs\述职报告_合订本.md"
$dstDir = "D:\Yaozheng\述职_合订本"
$dst = Join-Path $dstDir "述职报告_合订本.md"
Copy-Item -LiteralPath $src -Destination $dst -Force
$info = Get-Item -LiteralPath $dst
Write-Host ("Copied {0} bytes" -f $info.Length)
$content = Get-Content -LiteralPath $dst -Raw -Encoding UTF8
if ($content -match "training_parity") {
    Write-Host "OK: training_parity reference found in report"
} else {
    Write-Host "WARN: training_parity reference NOT found"
}
