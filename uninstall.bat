@echo off
title CS-AI Uninstaller
color 0C
echo ============================================
echo   CS-AI Uninstaller
echo ============================================
echo.
echo This will delete the CS-AI-Deploy folder.
echo.
set /p confirm=Type YES to confirm:
if /i not "%confirm%"=="YES" (
    echo Cancelled.
    goto end
)

echo.
echo Deleting CS-AI-Deploy...
rd /s /q "%~dp0CS-AI-Deploy" 2>nul
if exist "%~dp0CS-AI-Deploy" (
    echo   FAILED - close any open files inside the folder and try again.
) else (
    echo   Done.
)

:end
echo.
pause
