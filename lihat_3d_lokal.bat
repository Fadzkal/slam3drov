@echo off
title 3D SLAM Local Viewer - BlueROV2
echo ====================================================================
echo   BLUEROV2 - 3D SLAM WEB VIEWER LOKAL (THREE.JS)
echo ====================================================================
echo.

:: 1. Cek / Jalankan Web Server lokal port 8888
netstat -ano | findstr :8888 >nul
if %ERRORLEVEL% NEQ 0 (
    echo [*] Memulai Local Web Server di Port 8888...
    start /min "ROV 3D Web Server" python -m http.server 8888 --directory "c:\remote_ROV"
    timeout /t 2 /nobreak >nul
) else (
    echo [V] Web Server port 8888 sudah aktif.
)

:: 2. Buka Browser
echo [*] Membuka 3D Viewer di Browser...
start "" "http://localhost:8888/view_slam_3d_web.html"

echo.
echo ====================================================================
echo [V] Browser telah dibuka: http://localhost:8888/view_slam_3d_web.html
echo - Klik tombol "Dense 3D" untuk melihat hasil padat (117k titik + warna)
echo - Klik tombol "Sparse ORB" untuk melihat fitur tracking (30k titik)
echo - Klik tombol "Solid Mesh" untuk melihat permukaan 3D poligon
echo - Anda juga bisa Drag & Drop file .PLY apa saja langsung ke browser!
echo ====================================================================
timeout /t 5
