@echo off
echo ==========================================
echo   🚀 Starting NEXUS AI Agent
echo ==========================================

echo [1/2] Starting Backend...
start "NEXUS Backend" cmd /k "cd src && .\venv\Scripts\activate && python main.py"

echo [2/2] Starting Frontend...
start "NEXUS Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ✅ Done! Both services are starting in separate windows.
echo Keep those windows open while using the agent.
echo.
pause
