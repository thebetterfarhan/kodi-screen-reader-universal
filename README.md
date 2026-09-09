# Kodi Screen Reader — Universal Tolk Edition

An unofficial accessibility-focused continuation of the Kodi TTS add-on for 64-bit Kodi 21 on Windows. It sends Kodi navigation speech to the active screen reader through Tolk and includes focused compatibility improvements for NVDA and Kodi's Estuary skin.

> This project is independent of and is not endorsed by the Kodi Foundation, NV Access, or the Tolk maintainers. Kodi is not included.

## Highlights

- Active-screen-reader output through Tolk, with NVDA as the best-tested path.
- Official NVDA 2026.2 64-bit Controller Client included.
- Dedicated speech worker because Tolk is not thread-safe.
- Rapid navigation replaces obsolete queued labels.
- No silent switch to SAPI when Tolk is explicitly selected.
- List-item roles, position, selected state, and accessible Kodi settings.
- Estuary Home support with section and widget-area context and protection against stale widget labels.
- Confluence and generic-skin behavior retained.

## Download and install

Use the latest GitHub Release. Most Kodi users should install `service.xbmc.tts-2.1.1.zip` from **Add-ons → Install from zip file**. Windows users can instead run `Kodi-Screen-Reader-2.1.1-Windows-Setup.exe`, which installs only the add-on for the current user.

Read [Installation](docs/INSTALLATION.md), [Configuration](docs/CONFIGURATION.md), and [Troubleshooting](docs/TROUBLESHOOTING.md) before reporting a problem.

## Compatibility

| Component | Status |
|---|---|
| Kodi 21.x, 64-bit Windows | Supported target |
| NVDA 2026.2 | Best-tested screen reader |
| JAWS and other Tolk readers | Expected to work; community testing needed |
| Estuary | Dedicated Home compatibility layer |
| Confluence | Supported through generic reader plus existing workaround |
| Other Kodi skins | Generic label and window parsing |
| 32-bit Kodi or Windows | Not included in this build |

See [Compatibility and testing](docs/COMPATIBILITY.md) for the scope of these claims.

## Source and releases

The Kodi add-on source is under `addon/service.xbmc.tts`. The standalone installer source is under `installer`, and regression tests are under `tests`. Run `scripts/build-release.ps1` on Windows to create the release assets in `dist`.

## Credits and license

This project is based on Rick Phillips' original [Kodi TTS add-on](https://github.com/ruuk/service.xbmc.tts). The add-on and modifications are distributed under GPL-2.0. Tolk is distributed under LGPL-3.0, and the bundled NVDA Controller Client is covered by NVDA's LGPL-2.1 terms. See [Third-party notices](THIRD-PARTY-NOTICES.md) and the `licenses` directory.

