@echo off
setlocal EnableExtensions
chcp 65001 >nul
title Build DataMobile Exchange Parser installer

cd /d "%~dp0"

set "APP_EXE=%CD%\dist\DataMobile Exchange Parser\DataMobile Exchange Parser.exe"
set "ISS_FILE=%CD%\installer\DataMobileExchangeParser.iss"
set "EXPECTED_SETUP=%CD%\releases\DataMobileExchangeParserSetup.exe"

if not exist "%APP_EXE%" (
    echo ОШИБКА: приложение не найдено.
    echo Сначала запустите build_windows.bat
    echo Ожидаемый файл:
    echo %APP_EXE%
    echo.
    pause
    exit /b 1
)

if not exist "%ISS_FILE%" (
    echo ОШИБКА: не найден сценарий Inno Setup:
    echo %ISS_FILE%
    echo.
    pause
    exit /b 1
)

set "ISCC="
for /f "delims=" %%I in ('where ISCC.exe 2^>nul') do (
    set "ISCC=%%I"
    goto :found_iscc
)

if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
    goto :found_iscc
)

if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
    set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
    goto :found_iscc
)

echo ОШИБКА: компилятор Inno Setup 6 не найден.
echo Установите Inno Setup 6 и повторите запуск.
echo.
pause
exit /b 1

:found_iscc
if not exist "releases" mkdir "releases"

echo Используется:
echo %ISCC%
echo.
echo Создание установщика...
"%ISCC%" "%ISS_FILE%"

if errorlevel 1 (
    echo.
    echo ОШИБКА: установщик не создан. Код: %ERRORLEVEL%
    echo.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ==========================================
echo Установщик готов.
echo ==========================================
echo %EXPECTED_SETUP%
echo.
pause
exit /b 0
