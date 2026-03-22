@echo off
echo ========================================
echo LearnMate Backend Setup
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

echo [1/3] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment!
    pause
    exit /b 1
)

echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/3] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Create .env file with your API keys
echo 2. Run: start.bat
echo.
pause






