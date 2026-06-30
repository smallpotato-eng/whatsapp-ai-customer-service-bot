@echo off
title CS-AI Check
color 0E
echo ============================================
echo   CS-AI Environment Check
echo ============================================
echo.

echo [Node.js]
node --version 2>nul || echo   NOT INSTALLED
echo.

echo [npm]
npm --version 2>nul || echo   NOT INSTALLED
echo.

echo [Python]
python --version 2>nul || echo   NOT INSTALLED
echo.

echo [pip - flask]
python -c "import flask; print('  flask OK:', flask.__version__)" 2>nul || echo   NOT INSTALLED
echo.

echo [pip - fpdf2]
python -c "import fpdf; print('  fpdf2 OK')" 2>nul || echo   NOT INSTALLED
echo.

echo [n8n]
n8n --version 2>nul || echo   NOT INSTALLED
echo.

echo [WhatsApp node_modules]
if exist "%~dp0whatsapp\node_modules\@whiskeysockets" (
    echo   OK
) else (
    echo   NOT INSTALLED - need npm install in whatsapp folder
)
echo.

echo ============================================
echo   Check complete. Screenshot and send!
echo ============================================
echo.
pause
