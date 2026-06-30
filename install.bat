:: CS-AI Installer
@echo off
setlocal

echo ============================================
echo   CS-AI Installer
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install from https://python.org then re-run.
    goto end
)
for /f "tokens=*" %%v in ('python --version') do echo [OK] %%v

:: Install Python packages
echo Installing Python packages...
pip install flask fpdf2 requests
echo [OK] Python packages done.
echo.

:: Check n8n
n8n --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] n8n not installed.
    echo [!] Run install_n8n.bat as Administrator first, then come back.
) else (
    for /f "tokens=*" %%v in ('n8n --version') do echo [OK] n8n %%v
)
echo.

:: Create folders
if not exist "%~dp0db"         mkdir "%~dp0db"
if not exist "%~dp0quotations" mkdir "%~dp0quotations"

:: Init DB
cd /d "%~dp0api"
python -c "from app import init_db; init_db()" >nul 2>&1
echo [OK] Database ready.

echo.
echo ============================================
echo   Done. Run start.bat to launch.
echo ============================================

:end
echo.
pause
endlocal
