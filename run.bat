@echo off
setlocal
cd /d "%~dp0"

set "VENV_PYTHON=%~dp0.venv\Scripts\python.exe"

if not exist "%VENV_PYTHON%" (
    echo [ERREUR] Python du venv introuvable :
    echo   %VENV_PYTHON%
    echo Cree le venv avec : py -3.12 -m venv .venv
    pause
    exit /b 1
)

echo.
echo ==========================================
echo        YouTube vers MP3
echo ==========================================
echo   1. Mes videos J'aime (toutes les 5 min)
echo   2. Une playlist YouTube (une seule fois)
echo   3. Une playlist YouTube (toutes les 5 min)
echo.
choice /C 123 /N /M "Choisis 1, 2 ou 3 : "
if errorlevel 3 goto playlist_loop
if errorlevel 2 goto playlist_once

:likes
"%VENV_PYTHON%" "%~dp0youtube_likes_mp3.py"
goto end

:playlist_once
"%VENV_PYTHON%" "%~dp0youtube_likes_mp3.py" --playlist --once
goto end

:playlist_loop
"%VENV_PYTHON%" "%~dp0youtube_likes_mp3.py" --playlist

:end
pause
