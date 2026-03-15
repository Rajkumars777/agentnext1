@echo off
echo --- NEXUS Automation Setup ---

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.10+.
    exit /b 1
)

:: 2. Check for Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH. Please install Node.js 18+.
    exit /b 1
)

:: 3. Setup Python Backend
echo --- Setting up Backend ---
python -m venv venv
if exist venv\Scripts\activate (
    call venv\Scripts\activate
) else (
    echo [ERROR] Failed to create virtual environment.
    exit /b 1
)

echo [INFO] Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium

:: 4. Setup Node Frontend
echo --- Setting up Frontend ---
cd frontend
echo [INFO] Installing Node.js dependencies...
npm install
cd ..

:: 5. Setup .env
if not exist src\.env (
    echo [INFO] Creating .env from template...
    if exist .env.example (
        copy .env.example src\.env
    ) else (
        echo OPENAI_API_KEY=your_api_key_here > src\.env
        echo OPENROUTER_API_KEY=your_openrouter_api_key >> src\.env
        echo GEMINI_API_KEY=your_gemini_api_key >> src\.env
    )
    echo [WARNING] .env file created in src/. Please add your API keys.
)

echo --- Setup Complete! ---
echo Run 'run.bat' to start the project.
pause
