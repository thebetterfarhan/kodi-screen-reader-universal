# Contributing

Bug reports and accessibility test results are welcome. Search existing issues first, then provide reproducible navigation steps and sanitized logs. Do not post personal media-library information or credentials.

Code contributions should preserve Python 3 compatibility, avoid blocking Kodi's UI thread, keep every Tolk call on the dedicated worker, and include regression coverage when behavior changes.

Before opening a pull request, run:

```powershell
python -m unittest discover -s tests -v
```

