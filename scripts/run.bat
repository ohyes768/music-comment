@echo off
REM Music Comment Desktop App Launcher (Windows)

REM Change to project root directory
cd /d "%~dp0\.."

echo ==========================================
echo Music Comment Desktop App
echo ==========================================
echo Current directory: %CD%
echo.

REM Check virtual environment
if not exist ".venv" (
    echo Error: Virtual environment not found
    echo Please run: uv venv
    pause
    exit /b 1
)

REM Check if main.py exists
if not exist "src\main.py" (
    echo Error: src\main.py not found
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Set PYTHONPATH to project root
set PYTHONPATH=%CD%;%PYTHONPATH%

REM Run application
echo Starting application...
.venv\Scripts\python.exe src\main.py %*

pause
