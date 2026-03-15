@echo off
echo --- Building NEXUS Tauri EXE ---

:: 1. Navigate to frontend
cd frontend

:: 2. Run Tauri Build
echo [INFO] This process may take several minutes (especially the first time)
echo [INFO] as Rust compiles the core application.
npm run tauri build

if %errorlevel% neq 0 (
    echo [ERROR] Tauri build failed.
    pause
    exit /b 1
)

echo.
echo --- Build Complete! ---
echo Your Tauri executable is located in:
echo frontend\src-tauri\target\release\bundle\msi\ (or similar)
echo.
pause
