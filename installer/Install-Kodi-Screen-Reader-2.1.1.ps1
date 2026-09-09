$ErrorActionPreference = 'Stop'

$packageRoot = Split-Path -Parent $PSCommandPath
$archive = Join-Path $packageRoot 'Kodi-Screen-Reader-2.1.1-Estuary.zip'
$destination = Join-Path $env:APPDATA 'Kodi\addons\service.xbmc.tts'
$staging = Join-Path $env:TEMP ('Kodi-Screen-Reader-2.1.1-' + [guid]::NewGuid().ToString())

if (Get-Process Kodi -ErrorAction SilentlyContinue) {
    throw 'Kodi is running. Close Kodi and run this installer again.'
}
if (-not (Test-Path -LiteralPath $archive)) {
    throw "The add-on package is missing: $archive"
}

try {
    New-Item -ItemType Directory -Path $staging -Force | Out-Null
    Expand-Archive -LiteralPath $archive -DestinationPath $staging -Force
    $source = Join-Path $staging 'service.xbmc.tts'
    $manifestPath = Join-Path $source 'addon.xml'
    $estuaryModule = Join-Path $source 'lib\windows\estuary.py'
    if (-not (Test-Path -LiteralPath $manifestPath) -or
        -not (Test-Path -LiteralPath $estuaryModule)) {
        throw 'The embedded add-on package is incomplete.'
    }

    [xml]$sourceManifest = Get-Content -LiteralPath $manifestPath
    if ($sourceManifest.addon.id -ne 'service.xbmc.tts' -or
        $sourceManifest.addon.version -ne '2.1.1') {
        throw 'The embedded add-on is not Kodi Screen Reader 2.1.1.'
    }

    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    & robocopy $source $destination /E /COPY:DAT /R:2 /W:1 /NFL /NDL /NJH /NJS | Out-Null
    if ($LASTEXITCODE -gt 7) {
        throw "Kodi add-on copy failed (robocopy exit code $LASTEXITCODE)."
    }

    [xml]$installedManifest = Get-Content -LiteralPath (Join-Path $destination 'addon.xml')
    if ($installedManifest.addon.version -ne '2.1.1' -or
        -not (Test-Path -LiteralPath (Join-Path $destination 'lib\windows\estuary.py'))) {
        throw 'Installation verification failed.'
    }

    Write-Host ''
    Write-Host 'Kodi Screen Reader 2.1.1 installed successfully.'
    Write-Host "Location: $destination"
    Write-Host 'Existing Kodi profile and screen-reader settings were preserved.'
    Write-Host 'Start your screen reader before starting Kodi.'
} finally {
    if (Test-Path -LiteralPath $staging) {
        Remove-Item -LiteralPath $staging -Recurse -Force
    }
}
