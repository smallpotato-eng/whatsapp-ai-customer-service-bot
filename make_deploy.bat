@echo off
set SRC=${PROJECT_ROOT}\cs-ai
set DST=C:\Users\%USERNAME%\Desktop\CS-AI-Deploy

echo Preparing CS-AI-Deploy on Desktop...

if exist "%DST%" rmdir /s /q "%DST%"
mkdir "%DST%"

robocopy "%SRC%\api"         "%DST%\api"         /E /XD __pycache__ /XF *.pyc >nul
robocopy "%SRC%\clients"     "%DST%\clients"     /E >nul
robocopy "%SRC%\db"          "%DST%\db"          /E /XF *.db >nul
robocopy "%SRC%\n8n-exports" "%DST%\n8n-exports" /E >nul
robocopy "%SRC%\whatsapp"    "%DST%\whatsapp"    /E /XD node_modules >nul

copy "%SRC%\install.bat" "%DST%\install.bat" >nul
copy "%SRC%\start.bat"   "%DST%\start.bat"   >nul

mkdir "%DST%\quotations"

echo.
echo Done! CS-AI-Deploy folder is ready on your Desktop.
echo Copy the whole CS-AI-Deploy folder to any client computer, then run install.bat
echo.
pause
