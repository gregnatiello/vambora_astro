@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Ambiente virtual nao encontrado. Execute primeiro:
    echo python -m venv .venv
    echo .venv\Scripts\python -m pip install -r requirements.txt
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m pip install pyinstaller
if errorlevel 1 goto :error

".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --windowed --name GeradorTikTok desktop_app.py
if errorlevel 1 goto :error

copy /Y "dist\GeradorTikTok.exe" ".\GeradorTikTok.exe" >nul
echo.
echo Executavel criado em:
echo %~dp0GeradorTikTok.exe
pause
exit /b 0

:error
echo Falha ao criar o executavel.
pause
exit /b 1