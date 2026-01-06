@echo off
REM Music Comment Desktop App Launcher (Windows)

cd /d "%~dp0\.."

if not exist ".venv" (
    echo Error: Virtual environment not found
    echo Please run: uv venv
    pause
    exit /b 1
)

if not exist "src\main.py" (
    echo Error: src\main.py not found
    pause
    exit /b 1
)

set PYTHONPATH=%CD%;%PYTHONPATH%

start "" /B .venv\Scripts\pythonw.exe src\main.py %*
