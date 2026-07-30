$ErrorActionPreference = "Stop"
$files = @(
    "h2_bondscan_ol_8992_training_parity.png",
    "h2_bondscan_ol_8992_pes_comparison.png"
)
$srcBase = "\\wsl.localhost\Ubuntu\home\sunhl\projects\qchem_qml_md\results\h2_bondscan_ol_statevector_r12_8992\figures"
$dstDir = "D:\Yaozheng\述职_合订本\figures\uqc"
foreach ($f in $files) {
    Copy-Item -LiteralPath "$srcBase\$f" -Destination "$dstDir\$f" -Force
    $info = Get-Item -LiteralPath "$dstDir\$f"
    Write-Host ("{0}: {1} bytes" -f $f, $info.Length)
}
