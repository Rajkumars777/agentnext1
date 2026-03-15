@echo off
echo --- Starting NEXUS ---

:: Start Backend in a new window
start "NEXUS Backend" cmd /k "call venv\Scripts\activate && cd src && python main.py"

:: Start Frontend in a new window
start "NEXUS Frontend" cmd /k "cd frontend && npm run dev"

echo NEXUS is starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
