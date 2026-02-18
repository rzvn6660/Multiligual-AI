@echo off
title Fix Mobile Connection
color 1F

echo ========================================================
echo        TRIEM AI - Network & Firewall Fixer
echo ========================================================
echo.
echo This script will:
echo 1. Open Port 5000 in Windows Firewall so your iPhone can connect.
echo 2. Show you the exact IP address to type.
echo.
echo [IMPORTANT] A popup may ask for "Administrator" permission. 
echo             Please click YES/ALLOW to fix the network.
echo.
pause

:: Check for Admin rights
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [Admin Rights Confirmed]
) else (
    echo [Requesting Admin Rights...]
    powershell -Command "Start-Process '%~0' -Verb RunAs"
    exit /b
)

echo.
echo [1/2] Adding Firewall Rule for TRIEM (Port 5000)...
netsh advfirewall firewall add rule name="TRIEM_AI_Mobile" dir=in action=allow protocol=TCP localport=5000
echo       Done.

echo.
echo [2/2] Your Computer's IP Addresses:
echo ========================================================
ipconfig | findstr /i "IPv4"
echo ========================================================
echo.
echo HOW TO CONNECT ON IPHONE:
echo 1. Make sure iPhone is on the SAME WiFi as this PC.
echo 2. Open Safari.
echo 3. Type: http://YOUR_IP_ADDRESS:5000
echo    (Example: http://192.168.1.5:5000)
echo.
echo NOTE: Since this is a local connection (HTTP), iPhone might block the Microphone.
echo       If the page loads but Mic doesn't work, you need HTTPS.
echo       For now, let's just get the page to LOAD.
echo.
pause
