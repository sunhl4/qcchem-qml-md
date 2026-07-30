$ErrorActionPreference = "Stop"
$src = "\\wsl.localhost\Ubuntu\home\sunhl\projects\qchem_qml_md\results\h2_bondscan_ol_statevector_r12_8992\figures\h2_bondscan_ol_8992_training_parity.png"
$dstDir = "D:\Yaozheng\述职_合订本\figures\uqc"
$dst = "$dstDir\h2_bondscan_ol_8992_training_parity.png"
if (-not (Test-Path $dstDir)) { New-Item -ItemType Directory -Path $dstDir -Force | Out-Null }
Copy-Item -LiteralPath $src -Destination $dst -Force
$bytes = [System.IO.File]::ReadAllBytes($dst)
Write-Host ("Copied {0} bytes, header={1:X2} {2:X2} {3:X2} {4:X2}" -f $bytes.Length, $bytes[0], $bytes[1], $bytes[2], $bytes[3])
