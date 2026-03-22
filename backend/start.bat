@echo off
echo Starting LearnMate Backend...
echo.

REM 检查虚拟环境是否存在
if exist "venv\Scripts\python.exe" (
    echo Using virtual environment...
    venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
) else (
    echo Virtual environment not found. Using system Python...
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
)

