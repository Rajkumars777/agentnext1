@echo off
echo Starting OpenClaw Backend...
cd /d "%~dp0"
.\src\venv\Scripts\python.exe src\desktop_main.py
pause
