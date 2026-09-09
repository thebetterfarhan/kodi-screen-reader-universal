# Installation

## Requirements

- 64-bit Windows
- Kodi 21.x installed separately
- A supported screen reader; NVDA 2026.2 is the best-tested configuration

Close Kodi before using the Windows installer. Start the screen reader before starting Kodi after installation.

## Windows installer

1. Download `Kodi-Screen-Reader-2.1.1-Windows-Setup.exe` from the latest release.
2. Verify its SHA-256 value against `SHA256SUMS.txt`.
3. Close Kodi and run the installer.
4. Start NVDA or another supported screen reader.
5. Start Kodi.

The installer does not contain Kodi and does not require administrator access. It installs to `%APPDATA%\Kodi\addons\service.xbmc.tts`. Existing settings under Kodi's `userdata` directory are preserved.

The installer is currently unsigned, so Windows may display a reputation warning. Check the hash and obtain releases only from this repository.

## Install from Kodi ZIP

1. Download `service.xbmc.tts-2.1.1.zip` from the latest release.
2. In Kodi, open **Add-ons → Install from zip file**.
3. Select the downloaded ZIP and wait for the enabled notification.
4. Open **My add-ons → Services → Kodi Screen Reader → Configure**.
5. Choose **Tolk — active screen reader**.
6. Restart Kodi with the screen reader already running.

## Upgrade

Close Kodi and install the newer package over the existing add-on. User settings are stored separately and are not removed.

