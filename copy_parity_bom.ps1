$ErrorActionPreference = "Stop"
$src = "\\wsl.localhost\Ubuntu\home\sunhl\projects\qchem_qml_md\results\h2_bondscan_ol_statevector_r12_8992\figures\h2_bondscan_ol_8992_training_parity.png"
$dst = "D:\Yaozheng\述职_合订本\figures\uqc\h2_bondscan_ol_8992_training_parity.png"
Copy-Item -LiteralPath $src -Destination $dst -Force
$info = Get-Item -LiteralPath $dst
Write-Host ("Copied {0} bytes" -f $info.Length)
$fs = [System.IO.File]::OpenRead($dst)
$buf = New-Object byte[] 4
$fs.Read($buf, 0, 4) | Out-Null
$fs.Close()
Write-Host ("header={0:X2}{1:X2}{2:X2}{3:X2}" -f $buf[0], $buf[1], $buf[2], $buf[3])
