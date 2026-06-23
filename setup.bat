@echo off
REM Think2Seg Demo - Windows Development Setup Script

echo.
echo Think2Seg Demo - Development Setup
echo ====================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3.10+
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION%

REM Check Node
echo Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js not found. Please install Node.js 18+
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo [OK] Node.js %NODE_VERSION%

REM Backend Setup
echo.
echo Setting up Backend...
cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

if not exist ".env" (
    copy .env.example .env
    echo [INFO] Created .env file. Please update it with your configuration.
)

echo [OK] Backend setup complete

REM Frontend Setup
echo.
echo Setting up Frontend...
cd ..\frontend

echo Installing Node.js dependencies...
call npm install

echo [OK] Frontend setup complete

REM Final instructions
echo.
echo ======================================
echo [OK] Setup Complete!
echo.
echo To run the demo:
echo.
echo 1. Terminal 1 - Backend:
echo    cd backend
echo    venv\Scripts\activate.bat
echo    python main.py
echo.
echo 2. Terminal 2 - Frontend:
echo    cd frontend
echo    npm run dev
echo.
echo Then open:
echo    http://localhost:5173 (Frontend)
echo    http://localhost:8000 (Backend)
echo.
echo Note: First run will download models (15-20 minutes)
echo.
pause
