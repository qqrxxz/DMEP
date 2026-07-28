@echo off
setlocal EnableExtensions
chcp 65001 >nul
title Build DataMobile Exchange Parser Portable

cd /d "%~dp0"

set "APP_DIR=%CD%\dist\DataMobile Exchange Parser"
set "APP_EXE=%APP_DIR%\DataMobile Exchange Parser.exe"
set "RELEASE_DIR=%CD%\releases"
set "ZIP_PATH=%RELEASE_DIR%\DataMobileExchangeParser_Portable_Windows.zip"

if not exist "%APP_EXE%" (
    echo ОШИБКА: готовое приложение не найдено.
    echo Ожидаемый файл:
    echo %APP_EXE%
    echo.
    echo Сначала запустите build_windows.bat
    echo.
    pause
    exit /b 1
)

if not exist "%RELEASE_DIR%" mkdir "%RELEASE_DIR%"
if exist "%ZIP_PATH%" del /q "%ZIP_PATH%"

echo Создание portable-архива...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
    "Compress-Archive -LiteralPath '%APP_DIR%' -DestinationPath '%ZIP_PATH%' -CompressionLevel Optimal -Force"

if errorlevel 1 (
    echo.
    echo ОШИБКА: portable-архив не создан.
    echo.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ==========================================
echo Portable-версия готова.
echo ==========================================
echo %ZIP_PATH%
echo.
pause
exit /b 0
