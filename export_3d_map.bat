@echo off
title Ekspor 3D SLAM Map ke Web Viewer
echo ====================================================================
echo   BLUEROV2 - EKSPOR 3D SLAM MAP KE THREE.JS WEB VIEWER
echo   Mengekstrak RTAB-Map Point Cloud (.db) -^> Standard 3D (.ply)
echo ====================================================================
echo.

:: 1. Jalankan ekspor di WSL Ubuntu-20.04
echo [*] Mengekstrak 3D Point Cloud dari database RTAB-Map...
wsl -d Ubuntu-20.04 bash -c "chmod +x /mnt/c/remote_ROV/export_3d_map.sh && /mnt/c/remote_ROV/export_3d_map.sh"

echo.
echo [*] Menyiapkan Web Server lokal port 8888...
netstat -ano | findstr :8888 >nul
if %ERRORLEVEL% NEQ 0 (
    start /min "ROV 3D Web Server" python -m http.server 8888 --directory "c:\remote_ROV"
    timeout /t 2 /nobreak >nul
)

:: 2. Buka Browser
echo [*] Membuka Three.js 3D Viewer di Browser...
start "" "http://localhost:8888/view_slam_3d_web.html"

echo.
echo [V] Selesai! Browser telah terbuka.
echo Anda juga dapat Drag ^& Drop file .ply kapan saja ke jendela browser.
echo.
pause
