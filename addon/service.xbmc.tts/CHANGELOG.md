# Universal Tolk Edition changelog

## 2.1.1 — 2026-09-09

### Estuary compatibility

- Added a dedicated reader for Estuary's Home window while retaining the generic reader for all other Estuary windows.
- Added spoken section and widget-area context for Movies, TV shows, Music, Add-ons, Videos, TV, Radio, Weather, Music videos, Pictures, Games, and Favourites.
- Changed Estuary Home label lookup to prefer the focused container, preventing stale titles from another widget from being announced during rapid navigation.
- Added stable container-based focus identity for Estuary widgets, utility-button roles, and suppression of invisible focus-transfer controls.
- Added active-skin refresh when Kodi changes skins without restarting the screen-reader service.
- Added mocked regression coverage for container-label priority, region descriptions, utility controls, and hidden controls.

## 2.1.0 — 2026-09-09

### Kodi 21 configuration

- Rebuilt `resources/settings.xml` with Kodi's versioned section/category/group format while preserving existing setting IDs and saved choices.
- Added clear settings for Tolk, explicit SAPI, automatic selection, diagnostics, navigation replacement, roles, item position, selected state, polling, and reconnect timing.
- Added a **Speak backend status** action and updated add-on metadata for Kodi 21.

### Speech scheduling and recovery

- Added a protected queue for dialogs, notifications, and explicit read commands. Rapid navigation is prioritized and reduced to the newest valid focus without discarding protected announcements.
- Kept every Tolk load, output, silence, detection, and unload call on one worker thread. Backend replacement waits for the previous worker to finish.
- Retained bounded reader-restart detection with rate-limited diagnostics and no SAPI fallback when Tolk is explicitly selected.

### Richer accessible output

- Added reliable list-item roles, current/total position, selected state, and settings checkbox/button roles with user controls for each verbosity feature.
- Kept focus identity separate from spoken text so duplicate labels, in-place changes, database items, and scrolling remain distinguishable.

### Verification

- Added twelve mocked regression tests for queue replacement, cancellable pauses, race handling, protected groups, duplicate labels, shutdown, and backend replacement.
- Added a repeatable queue benchmark. Its results cover internal Python queue/event mechanics only and do not represent audible NVDA latency.

## 2.0.0-universal.3 — 2026-09-09

### Tolk initialization and recovery

- Corrected the Tolk C binding to use the `__cdecl` calling convention and the upstream `void` return type for `Tolk_Load`.
- Verify initialization with `Tolk_IsLoaded`, then independently verify an active speech-capable screen reader with `Tolk_DetectScreenReader` and `Tolk_HasSpeech`.
- Kept all Tolk calls on its worker thread and balanced the final silence/unload sequence.
- When Tolk is explicitly selected, no longer fall back to SAPI because a reader is unavailable. The worker retries detection with a bounded 0.5–5 second backoff and rate-limited diagnostics.

### Focus identity

- Replaced text-and-time comparison with a focus identity containing Kodi's focused container item, window/control context, and available database/path identity. This allows adjacent duplicate labels and list scrolling to be announced without treating a visible row position as the item identity.

## 2.0.0-universal.2 — 2026-09-09

### Responsive navigation

- Made Tolk's queued 500 ms pauses cancellable. A new navigation announcement wakes the pause immediately instead of waiting for it to finish.
- Added generation-based queue replacement: interrupting navigation removes obsolete queued labels, sends Tolk silence on the speech thread, and then sends the newest label.
- Retained grouped announcements, dialogs, explicit read commands, and non-interrupting speech as queued groups.
- Reduced Tolk's default focus polling interval from 100 ms to 40 ms. Users who enabled Kodi's poll-interval override keep their chosen value.
- Added optional verbose timing diagnostics for focus detection, enqueueing, cancellation, and Tolk dispatch. These diagnose software dispatch only, not audible speech latency.

## 2.0.0-universal.1 — 2026-09-09

### Windows screen-reader update

- Added the **Tolk (active screen reader)** backend for Kodi on Windows.
- Added a dedicated, single speech thread for Tolk. Tolk is not thread-safe, so all load, output, silence, and unload calls stay on that thread.
- Bundled the official NVDA 2026.2 64-bit controller client in both names expected by common Tolk builds.
- Disabled the old automatic SAPI fallback for the selected Tolk path. This keeps speech with the active screen reader and makes an unavailable reader visible in Kodi's log instead of changing output methods unexpectedly.
- Added explicit diagnostic logging for loading Tolk, detecting the active reader, and speech-backend startup/shutdown.

### Packaging and installation

- Added a clean add-on ZIP with one top-level `service.xbmc.tts` folder.
- Added a full Kodi 21.3 Windows installer that embeds this add-on and chooses the Confluence skin and Tolk backend by default.
- Added a plain-language README and kept the original Kodi TTS `changelog.txt` in the add-on unchanged.

### Original Kodi TTS project

This distribution is based on Ruuk's `service.xbmc.tts`, whose purpose is to provide text-to-speech for Kodi using the speech engines available on each platform. Its original source and release history remain available in the upstream repository and the included `changelog.txt`.

The original project is GPL-2.0. The Windows universal changes above are compatibility and packaging updates; they do not replace the original project's attribution or licensing.
