$ErrorActionPreference = "Stop"
$src = "\\wsl.localhost\Ubuntu\home\sunhl\projects\qchem_qml_md\results\h2_bondscan_ol_statevector_r12_8992\figures\h2_bondscan_ol_8992_pes_comparison.png"
$dst = "D:\Yaozheng\述职_合订本\figures\uqc\h2_bondscan_ol_8992_pes_comparison.png"
Copy-Item -LiteralPath $src -Destination $dst -Force
$info = Get-Item -LiteralPath $dst
Write-Host ("Copied {0} bytes" -f $info.Length)
