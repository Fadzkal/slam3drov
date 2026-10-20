@echo off
title FUSI ORB-SLAM3 + DEPTH AI (DENSE 3D SLAM)
cd /d "%~dp0"

echo ====================================================================
echo   FUSI DENSE NEURAL-SLAM: ORB-SLAM3 TRACKING + DEPTH AI + RTAB-MAP
echo ====================================================================
echo.
echo   [1] JALANKAN Live Webcam (ORB-SLAM3 + Depth AI + RViz 3D Padat)
echo   [2] JALANKAN Video ROV Kontainer (ORB-SLAM3 + Depth AI + RViz 3D Padat)
echo   [3] Ekspor Hasil Peta 3D ke File .PLY (Standard 3D Model)
echo   [4] Buka Three.js Web 3D Viewer
echo.
set /p OPT="Pilih [1-4 - Default 1]: "
if "%OPT%"=="" set OPT=1

if "%OPT%"=="1" goto live_webcam
if "%OPT%"=="2" goto rov_video
if "%OPT%"=="3" goto export_ply
if "%OPT%"=="4" goto web_viewer
echo Pilihan tidak valid.
pause
goto end

:live_webcam
echo.
echo Pilih Webcam yang ingin digunakan:
echo   [1] USB Camera (Index 1 - Default)
echo   [2] Logitech C922 (Index 0)
echo.
set /p CAM_CH="Pilih [1 atau 2 - Default 1]: "
set CAM_ARG=1
if "%CAM_CH%"=="2" set CAM_ARG=0
if "%CAM_CH%"=="0" set CAM_ARG=0

echo.
echo [*] Membuka MJPEG Webcam Bridge (Kamera Index %CAM_ARG%)...
start "MJPEG Webcam Bridge" python mjpeg_webcam_bridge.py %CAM_ARG%
echo Menunggu kamera siap (3 detik)...
timeout /t 3 /nobreak >nul

echo.
echo [*] Meluncurkan Pipeline Fusi: ORB-SLAM3 + Depth AI + RTAB-Map + RViz...
wsl -d Ubuntu-20.04 -- bash -c "export DISPLAY=:0 && ~/slam_ws/run_dense_orbslam_webcam.sh"
pause
goto end

:rov_video
echo.
echo [*] Menjalankan Fusi pada Rekaman Video ROV Kontainer Bawah Laut...
echo [*] Meluncurkan Pipeline: ORB-SLAM3 Tracking + Depth AI MiDaS + RTAB-Map...
wsl -d Ubuntu-20.04 -- bash -c "export DISPLAY=:0 && ~/slam_ws/run_dense_orbslam_rovvideo.sh"
pause
goto end

:export_ply
echo.
echo [*] Mengekstrak database 3D RTAB-Map menjadi file .PLY...
call export_3d_map.bat
goto end

:web_viewer
echo.
echo [*] Membuka Three.js Web Viewer...
call open_3d_web_viewer.bat
goto end

:end
