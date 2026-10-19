@echo off
title AeroMem Live Demo Launcher
echo =====================================================================
echo    AeroMem: Decentralized Episodic Vector Memory Bridge Demo
echo =====================================================================
echo Starting Streamlit Dashboard and Public Cloudflare Tunnel...
echo.

REM Start Streamlit in a new background process
start "AeroMem Streamlit" /min python -m streamlit run dashboard.py --server.port 8501 --server.headless true

timeout /t 3 /nobreak >nul

REM Check for cloudflared
if exist "%TEMP%\cloudflared.exe" (
    echo Cloudflare tunnel binary detected. Launching public tunnel...
    "%TEMP%\cloudflared.exe" tunnel --url http://127.0.0.1:8501
) else (
    echo Downloading cloudflared...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile '$env:TEMP\cloudflared.exe' -UseBasicParsing"
    "%TEMP%\cloudflared.exe" tunnel --url http://127.0.0.1:8501
)
pause
