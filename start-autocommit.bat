@echo off
powershell -WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -File "%~dp0autocommit.ps1"
echo Auto-commit script started in the background (hidden window).
echo You can check progress in "autocommit.log".
pause
