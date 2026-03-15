@echo off
echo --- Tauri & Rust Environment Check ---

:: 1. Check for Rust
rustc --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [MISSING] Rust is not installed. Please visit https://rustup.rs/
) else (
    echo [OK] Rust is installed.
    rustc --version
)

:: 2. Check for Cargo
cargo --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [MISSING] Cargo is not installed.
) else (
    echo [OK] Cargo is installed.
)

:: 3. Check for MSVC (C++ Build Tools)
where cl.exe >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] C++ Build Tools (cl.exe) not found in PATH. 
    echo This is often normal if you haven't run from a "Developer Command Prompt", 
    echo but ensure "Desktop development with C++" is installed in Visual Studio.
) else (
    echo [OK] C++ Compiler found.
)

:: 4. Check for WebView2
reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3C4FE00-EFC5-4029-9886-A7E940248839}" /v pv >nul 2>&1
if %errorlevel% neq 0 (
    echo [MISSING] WebView2 Runtime not detected. (Required for Tauri)
) else (
    echo [OK] WebView2 Runtime detected.
)

echo.
echo If everything is [OK], you can run:
echo cd frontend
echo npm run tauri init
pause
