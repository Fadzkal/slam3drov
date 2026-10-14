@echo off
title Buka 3D SLAM Web Viewer
echo ====================================================================
echo   BLUEROV2 - BUKA THREE.JS 3D SLAM WEB VIEWER
echo ====================================================================
echo.

netstat -ano | findstr :8888 >nul
if %ERRORLEVEL% NEQ 0 (
    echo [*] Menjalankan server web lokal port 8888...
    start /min "ROV 3D Web Server" python -m http.server 8888 --directory "c:\remote_ROV"
    timeout /t 2 /nobreak >nul
) else (
    echo [*] Web server lokal port 8888 sudah aktif.
)

echo [*] Membuka Browser...
start "" "http://localhost:8888/view_slam_3d_web.html"

echo.
echo [V] Web Viewer telah dibuka di browser.
pause
