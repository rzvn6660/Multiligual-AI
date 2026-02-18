@echo off
title TRIEM AI Server
color 0A

echo ========================================================
echo        TRIEM AI - Tribal Intelligent Assistant
echo ========================================================
echo.
echo [1/3] Checking for existing instances...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq TRIEM AI Server" >nul 2>&1

echo [2/3] Starting AI Server (This may take a moment to load CUDA)...
echo        Please wait while models load...

:: Start server in separate window to keep it running
start "TRIEM_Backend" /min cmd /k "python server.py"

echo [3/3] Waiting for server to initialize...
timeout /t 15 >nul

echo.
echo Launching Interface...
start http://localhost:5000

echo.
echo ========================================================
echo        Success! The App is running.
echo        Do not close the "TRIEM_Backend" window.
echo ========================================================
pause
