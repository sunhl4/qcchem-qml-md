$ErrorActionPreference = "Stop"
$src = "\\wsl.localhost\Ubuntu\home\sunhl\projects\qchem_qml_md\docs\述职报告_合订本.md"
$dst = "D:\Yaozheng\述职_合订本\述职报告_合订本.md"
Copy-Item -LiteralPath $src -Destination $dst -Force
$bytes = [System.IO.File]::ReadAllBytes($dst)
Write-Host ("Copied {0} bytes" -f $bytes.Length)
# Verify the training_parity reference is present
$content = [System.IO.File]::ReadAllText($dst, [System.Text.Encoding]::UTF8)
if ($content -match "training_parity") {
    Write-Host "OK: training_parity reference found in report"
} else {
    Write-Host "WARN: training_parity reference NOT found"
}
