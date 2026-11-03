@echo off
cd /d "%~dp0"
where node >nul 2>&1
if errorlevel 1 (
  echo [LOI] Can cai Node.js LTS hoac mo trang qua GitHub Pages.
  pause
  exit /b 1
)
start "Drone Data Studio Server" cmd /k "node server.cjs"
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8080"
