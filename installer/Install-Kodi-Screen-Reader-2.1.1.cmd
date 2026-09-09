@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-Kodi-Screen-Reader-2.1.1.ps1"
if errorlevel 1 (
  echo.
  echo Installation failed. Review the message above.
  pause
  exit /b 1
)
echo.
echo Installation completed successfully.
pause
