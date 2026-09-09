# Configuration

Open **My add-ons → Services → Kodi Screen Reader → Configure**.

## Recommended NVDA settings

- Backend: **Tolk — active screen reader**
- Reader off: disabled
- Replace obsolete navigation speech: enabled
- Speak control roles: enabled
- Speak item position: enabled
- Speak selected state: enabled
- Automatically read item details: disabled initially
- Custom polling interval: disabled initially; Tolk uses the responsive default

Use **Speak backend status** to confirm that Tolk is connected and identifies the active reader.

## Estuary

Version 2.1.1 adds a dedicated reader for Estuary's Home window. It announces the Home section, widget area, focused item, role, position, and selected state where Kodi exposes those values. Other Estuary windows continue to use the standard window readers.

For concise speech, use list views, hide home categories you do not use, reduce optional home widgets, and disable automatically read item details.

## Other screen readers

Tolk can support several Windows screen readers, but this release has been exercised primarily with NVDA. Select Tolk, use **Speak backend status**, and report the reader name and relevant sanitized log lines when testing another reader.

