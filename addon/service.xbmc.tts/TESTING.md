# Kodi Screen Reader 2.1 test report

Automated on 2026-09-09 using Python 3 with mocked Kodi/Tolk interfaces:

- 12 regression tests passed.
- 500 ms pause cancellation wake-up, 100 runs: median 0.436 ms; 95th percentile 0.662 ms; maximum 1.069 ms.
- Newest-generation replacement enqueue, 1,000 runs: median 0.059 ms; 95th percentile 0.070 ms; maximum 0.332 ms.
- XML parsing and Python compilation passed for the changed files.
- The bundled native Tolk DLL loaded with `__cdecl`, `Tolk_IsLoaded=True`, and SAPI disabled in a no-speech probe.

These measurements exclude Kodi focus polling, Tolk dispatch, NVDA processing, synthesizer output, audio buffering, and human-perceived latency. Live audible testing must be done in Kodi with the intended screen reader running.

Recommended live checks: single arrow presses, held arrows, rapid reversals, navigation during an announcement pause, duplicate adjacent labels, dialogs, explicit repeat/extra commands, screen-reader restart, backend replacement, and Kodi shutdown.
