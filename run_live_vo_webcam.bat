@echo off
title Live Monocular Camera Tracking (CPU Only)
cd /d "%~dp0"
echo ===============================================================
echo   LIVE MONOCULAR CAMERA TRACKING (100%% CPU REAL-TIME)
echo ===============================================================
echo Terdeteksi kamera fisik di komputer Anda:
echo   Index 1: USB Camera (Webcam USB Eksternal)
echo   Index 0: c922 Pro Stream Webcam (Logitech)
echo   *Catatan: OBS Virtual Camera (Index 2) otomatis diblokir.
echo.
echo Pilih sumber kamera:
echo   [1] USB Camera (Index 1 - Default Webcam USB)
echo   [2] Logitech C922 (Index 0)
echo   [V] Uji Coba Video ROV Kontainer Bawah Air
echo.
set /p CAM_CHOICE="Pilih [1, 2, atau V - Default: 1]: "

if "%CAM_CHOICE%"=="" set CAM_CHOICE=1
if /i "%CAM_CHOICE%"=="v" goto run_video
if "%CAM_CHOICE%"=="1" set CAM_ID=1
if "%CAM_CHOICE%"=="2" set CAM_ID=0
if "%CAM_CHOICE%"=="0" set CAM_ID=0
if not defined CAM_ID set CAM_ID=1

echo.
echo Menjalankan tracking pada kamera ID %CAM_ID%...
python live_monocular_vo_webcam.py %CAM_ID%
goto end

:run_video
echo.
echo Menjalankan tracking pada rekaman video ROV...
python live_monocular_vo_webcam.py "videos/YTDown.com_YouTube_Media_g4bUv6Fx3Pk_Site-113-A-Steel-Container-from-a-BlueROV2_001_1080p.mp4"

:end
pause
