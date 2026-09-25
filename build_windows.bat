@echo off
setlocal EnableExtensions
chcp 65001 >nul
title Build DataMobile Exchange Parser

cd /d "%~dp0"

set "PYTHON_CMD="
where py.exe >nul 2>nul
if %ERRORLEVEL% EQU 0 set "PYTHON_CMD=py -3"

if not defined PYTHON_CMD (
    where python.exe >nul 2>nul
    if %ERRORLEVEL% EQU 0 set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
    echo ОШИБКА: Python 3 не найден.
    echo Установите Python 3.10–3.13 с сайта python.org.
    echo При установке включите пункт Add python.exe to PATH.
    echo.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Создание виртуального окружения...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 goto :error
)

set "VENV_PYTHON=%CD%\.venv\Scripts\python.exe"

echo Установка инструментов сборки...
"%VENV_PYTHON%" -m pip install --upgrade --no-compile "pip==25.0.1"
if errorlevel 1 goto :error

"%VENV_PYTHON%" -m pip install --no-compile -r requirements.txt
if errorlevel 1 goto :error

echo Сборка приложения...
"%VENV_PYTHON%" -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --windowed ^
    --name "DataMobile Exchange Parser" ^
    --add-data "config;config" ^
    --add-data "specs;specs" ^
    --add-data "assets;assets" ^
    main.py
if errorlevel 1 goto :error

echo.
echo ==========================================
echo Сборка завершена.
echo ==========================================
echo Приложение:
echo %CD%\dist\DataMobile Exchange Parser\DataMobile Exchange Parser.exe
echo.
pause
exit /b 0

:error
echo.
echo ОШИБКА: сборка не выполнена. Код: %ERRORLEVEL%
echo.
pause
exit /b %ERRORLEVEL%
