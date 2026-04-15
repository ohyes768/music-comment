@echo off
echo Starting NetEase Music...
start "" "C:\Program Files\NetEase\CloudMusic\cloudmusic.exe"

echo Waiting for NetEase Music to fully start (10 seconds)...
timeout /t 10 /nobreak > nul

echo Starting Comment App...
cd /d F:\github\person_project\music-comment
call .venv\Scripts\activate.bat
start "" python -m src.main

echo Done!
