@echo off
REM build.bat – genera el ejecutable en Windows
setlocal

set VENV=venv
set PYTHON=%VENV%\Scripts\python.exe
set PIP=%VENV%\Scripts\pip.exe

echo =^> Comprobando entorno virtual...
if not exist "%PYTHON%" (
    echo Creando entorno virtual...
    python -m venv %VENV%
)

echo =^> Instalando dependencias...
%PIP% install --quiet pygame-ce pyinstaller

echo =^> Limpiando builds anteriores...
if exist build rmdir /s /q build
if exist dist  rmdir /s /q dist

echo =^> Compilando GimbernatBros...
%VENV%\Scripts\pyinstaller game.spec --clean --noconfirm

echo.
echo =============================================
echo   Ejecutable:  dist\GimbernatBros.exe
echo =============================================
pause
