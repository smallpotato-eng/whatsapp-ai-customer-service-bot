:: WARNING: This script is for generic production use. Ensure environment variables are set before deployment.
@echo off
setlocal

:: ── CONFIG ──────────────────────────────────────────────
set FLASK_PORT=5050
set N8N_PORT=5678
set WA_PORT=3000
:: ─────────────────────────────────────────────────────────

set ROOT=%~dp0

echo ============================================
echo   CS-AI System Startup
echo ============================================
echo.

:: 1. Flask API
echo [1/3] Starting Flask API (port %FLASK_PORT%)...
start "Flask API" cmd /k "cd /d %ROOT%api && python app.py"
timeout /t 3 /nobreak >nul
echo [OK] Flask started.

:: 2. n8n
echo [2/3] Starting n8n (port %N8N_PORT%)...
start "n8n" cmd /k "n8n start"
echo [OK] n8n started.

:: 3. WhatsApp service
echo [3/3] Starting WhatsApp service (port %WA_PORT%)...
start "WhatsApp" cmd /k "cd /d %ROOT%whatsapp && node index.js"
echo [OK] WhatsApp started.

:: Wait for n8n then open browser
echo.
echo Waiting for n8n to be ready...
:wait_n8n
powershell -Command "try{(New-Object Net.Sockets.TcpClient('localhost',%N8N_PORT%)).Close();exit 0}catch{exit 1}" >nul 2>&1
if %errorlevel% neq 0 (
    timeout /t 2 /nobreak >nul
    goto wait_n8n
)
echo [OK] Opening browser...
start "" "http://localhost:%N8N_PORT%"

echo.
echo ============================================
echo   All services running
echo   Flask  : http://localhost:%FLASK_PORT%
echo   n8n    : http://localhost:%N8N_PORT%
echo   WA     : http://localhost:%WA_PORT%
echo ============================================
echo.
echo Scan the QR code in the WhatsApp window!
echo.
echo NOTE: Place client SOP.txt at:
echo   C:\Users\%USERNAME%\.n8n-files\SOP.txt

:end
echo.
pause
endlocal
