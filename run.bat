@echo off
setlocal
cd /d "%~dp0"

set "VENV_PYTHON=%~dp0.venv\Scripts\python.exe"

if not exist "%VENV_PYTHON%" (
    echo [ERREUR] Python du venv introuvable :
    echo   %VENV_PYTHON%
    echo Cree le venv avec : python -m venv .venv
    pause
    exit /b 1
)

"%VENV_PYTHON%" "%~dp0youtube_likes_mp3.py"
pause
