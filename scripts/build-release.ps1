param(
    [string]$Version = '2.1.1'
)

$ErrorActionPreference = 'Stop'
$repository = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$addon = Join-Path $repository 'addon\service.xbmc.tts'
$installer = Join-Path $repository 'installer'
$dist = Join-Path $repository 'dist'
$build = Join-Path $repository 'build'
$payload = Join-Path $build 'payload'
$zipName = "service.xbmc.tts-$Version.zip"
$exeName = "Kodi-Screen-Reader-$Version-Windows-Setup.exe"

[xml]$manifest = Get-Content -LiteralPath (Join-Path $addon 'addon.xml')
if ($manifest.addon.version -ne $Version) {
    throw "addon.xml contains version $($manifest.addon.version), expected $Version."
}

$sevenZip = Join-Path $env:ProgramFiles '7-Zip\7z.exe'
$sfx = Join-Path $env:ProgramFiles '7-Zip\7z.sfx'
if (-not (Test-Path -LiteralPath $sevenZip) -or -not (Test-Path -LiteralPath $sfx)) {
    throw '7-Zip with 7z.sfx is required to build the Windows installer.'
}

if (Test-Path -LiteralPath $dist) { Remove-Item -LiteralPath $dist -Recurse -Force }
if (Test-Path -LiteralPath $build) { Remove-Item -LiteralPath $build -Recurse -Force }
New-Item -ItemType Directory -Path $dist,$payload -Force | Out-Null

$zipPath = Join-Path $dist $zipName
Compress-Archive -LiteralPath $addon -DestinationPath $zipPath -CompressionLevel Optimal

Copy-Item -LiteralPath (Join-Path $installer 'Install-Kodi-Screen-Reader-2.1.1.ps1') -Destination $payload
Copy-Item -LiteralPath (Join-Path $installer 'Install-Kodi-Screen-Reader-2.1.1.cmd') -Destination $payload
Copy-Item -LiteralPath $zipPath -Destination (Join-Path $payload 'Kodi-Screen-Reader-2.1.1-Estuary.zip')

$payloadArchive = Join-Path $build 'installer-payload.7z'
& $sevenZip a -t7z $payloadArchive (Join-Path $payload '*') -mx=9 -y | Out-Null
if ($LASTEXITCODE -ne 0) { throw "7-Zip failed with exit code $LASTEXITCODE." }

$exePath = Join-Path $dist $exeName
$output = [System.IO.File]::Create($exePath)
try {
    foreach ($part in @($sfx, (Join-Path $installer 'sfx-config.txt'), $payloadArchive)) {
        $input = [System.IO.File]::OpenRead($part)
        try { $input.CopyTo($output) } finally { $input.Dispose() }
    }
} finally {
    $output.Dispose()
}

$hashLines = Get-ChildItem -LiteralPath $dist -File | Sort-Object Name | ForEach-Object {
    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash
    "$hash *$($_.Name)"
}
$hashLines | Set-Content -LiteralPath (Join-Path $dist 'SHA256SUMS.txt') -Encoding ASCII

Write-Host "Release $Version built in $dist"

