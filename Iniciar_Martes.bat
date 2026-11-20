@echo off
cd /d "%~dp0"
if exist "Martes.exe" (
    start "" "Martes.exe"
) else (
    start "" pythonw mini_martes.py
)
exit
