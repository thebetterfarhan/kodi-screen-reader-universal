# Compatibility and testing

Version 2.1.1 targets 64-bit Kodi 21.x on Windows. NVDA 2026.2 is the best-tested output path.

The included Tolk library has drivers for multiple screen readers, but inclusion is not the same as completed compatibility testing. JAWS and other Tolk-supported readers should be treated as community-tested until repeatable results are documented.

## Automated regression coverage

The mocked tests cover:

- rapid navigation queue replacement;
- cancellable announcement pauses;
- protected dialog and explicit-read groups;
- single-threaded Tolk shutdown and backend replacement;
- duplicate-label focus identity;
- Estuary container-label priority;
- Estuary section and widget-area descriptions;
- Estuary utility and invisible focus controls.

Run them with:

```powershell
python -m unittest discover -s tests -v
```

These tests validate internal behavior. They do not measure audible latency or replace hands-on testing with each screen reader and skin.

