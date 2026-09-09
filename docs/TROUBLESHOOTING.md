# Troubleshooting

## No speech

1. Close Kodi.
2. Start NVDA or the intended screen reader.
3. Start Kodi again.
4. Confirm that the add-on is enabled under **My add-ons → Services**.
5. In Configure, select **Tolk — active screen reader**.
6. Activate **Speak backend status**.

The Kodi log is normally `%APPDATA%\Kodi\kodi.log`. Look for `service.xbmc.tts`, `Tolk loaded`, and `Tolk active screen reader` messages.

## Speech comes from SAPI

Select Tolk explicitly instead of Automatic or SAPI. Version 2.1.1 does not silently replace an explicitly selected Tolk backend with SAPI when a screen reader restarts or is unavailable.

## Estuary reads an old item

Confirm that version 2.1.1 or newer is installed. This version queries the focused Estuary container before global Kodi labels. Restart Kodi after upgrading so the new reader module is loaded.

## Speech is too verbose

Disable automatic item details, list counts, selected state, or item position as preferred. Reducing Estuary Home widgets also reduces region changes.

## Reporting a problem

Include the Kodi version, add-on version, Windows version, skin, screen reader and version, exact navigation steps, expected speech, actual speech, and a short relevant log excerpt. Logs can contain usernames, paths, media names, and network addresses; remove private information before posting.

