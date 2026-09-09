# Kodi Screen Reader — Universal Tolk Edition

Version 2.1.1 is a Windows accessibility release of the original **Kodi TTS / Screen Reader** add-on (`service.xbmc.tts`) for Kodi 21.3. It keeps the original speech-event behaviour while modernizing configuration, focus tracking, and active-screen-reader output.

## What it does

- Uses the active screen reader through Tolk: NVDA, JAWS, Window-Eyes, System Access, and ZoomText are among Tolk's supported readers.
- Includes the official NVDA 2026.2 64-bit controller client, so the bundled NVDA path does not rely on Kodi's legacy SAPI output.
- Uses one dedicated speech thread. This prevents Kodi's UI thread from calling a screen-reader driver directly.
- Cancels obsolete navigation speech and 500 ms announcement pauses immediately when focus changes. Tolk checks focus every 40 ms by default; Kodi's existing poll-interval override is still respected.
- Keeps an explicitly selected Tolk backend selected if a reader is absent or restarting. It retries detection with a bounded delay and never silently changes to SAPI.
- Does **not** fall back to SAPI when the Tolk backend is selected. If no compatible reader is running, the add-on records the issue in `kodi.log` instead of unexpectedly speaking through SAPI.
- Includes the original Kodi TTS add-on files and its original `changelog.txt`.
- Provides native Kodi 21 settings for output, navigation verbosity, polling, reconnection, diagnostics, and keymaps.
- Keeps explicit commands and dialogs in a protected queue while rapid navigation coalesces to the newest item.
- Announces reliable list-item roles, positions, selected state, and checkbox/button roles in Kodi settings.
- Adds an Estuary-specific home reader that announces menu sections and widget areas, prefers the focused container over stale global labels, identifies utility buttons, and ignores invisible focus-transfer controls.

## Install the add-on ZIP

1. Close Kodi.
2. In Kodi, choose **Add-ons → Install from zip file** and select the release ZIP; or extract the `service.xbmc.tts` folder into Kodi's `addons` folder.
3. Start your screen reader before starting Kodi.
4. Open **My add-ons → Services → Kodi Screen Reader → Configure**. Choose **Tolk — active screen reader**. The full Kodi installer selects it automatically.

## Roll back

Close Kodi, then reinstall the rollback ZIP supplied with the 2.1 release. Your user settings are stored separately under `%APPDATA%\Kodi\userdata\addon_data\service.xbmc.tts` and are not removed.

## Important notes

- This release is for 64-bit Kodi on Windows.
- NVDA is the best-tested path. Other readers depend on the Tolk driver installed with or discoverable by that reader.
- If speech is silent, start the screen reader first, then restart Kodi and check the `Tolk active screen reader` line in `%APPDATA%\Kodi\kodi.log`.
- Turn on the add-on's existing verbose logging only when diagnosing responsiveness. It records focus detection, queue, cancellation, and Tolk dispatch timing; dispatch timing is not a measurement of audible speech latency.
- Duplicate list labels are distinguished using Kodi's focused container item identity and, when available, the item's database id or file path.
- Use **Speak backend status** in Configure to hear whether Tolk is connected and which screen reader it detected.

## Credits and licensing

The original Kodi TTS add-on is by Ruuk and is licensed under GPL-2.0. This distribution preserves its original licensing files. Tolk is licensed under LGPL-3.0; the NVDA controller client is distributed under NVDA's LGPL-2.1 licensing. See the upstream projects for complete terms and source.

Upstream projects: [Kodi TTS](https://github.com/ruuk/service.xbmc.tts), [Tolk](https://github.com/dkager/tolk), and [NVDA](https://github.com/nvaccess/nvda).
