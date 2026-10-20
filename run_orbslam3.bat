@echo off
title ORB-SLAM3 Setup & Launcher
cd /d "%~dp0"

echo ================================================================
echo   ORB-SLAM3 LAUNCHER (WSL2 Ubuntu 20.04)
echo ================================================================
echo.
echo Pilih aksi:
echo   [1] JALANKAN ORB-SLAM3 Video ROV (Sangat disarankan untuk tes awal!)
echo   [2] JALANKAN ORB-SLAM3 Live Webcam
echo   [3] MULAI MJPEG Bridge Saja (Window terpisah)
echo   [4] Cek Status WSL2 + GPU OpenGL + Kamera
echo.
set /p CHOICE="Pilih [1-4]: "

if "%CHOICE%"=="1" goto rovvideo
if "%CHOICE%"=="2" goto webcam
if "%CHOICE%"=="3" goto bridge
if "%CHOICE%"=="4" goto status
echo Pilihan tidak valid.
pause
goto end

:rovvideo
echo.
echo [VIDEO] Menjalankan ORB-SLAM3 pada rekaman video ROV bawah air...
echo [INFO] Jendela Pangolin 3D Viewer akan segera muncul...
wsl -d Ubuntu-20.04 -- bash -c "export DISPLAY=:0 && ~/slam_ws/run_orbslam3_rovvideo.sh"
pause
goto end

:webcam
echo.
echo Pilih Webcam yang ingin digunakan:
echo   [1] USB Camera (Index 1 - Default Webcam USB)
echo   [2] Logitech C922 (Index 0)
echo.
set /p CAM_ORB="Pilih [1 atau 2 - Default 1]: "
set CAM_ARG=1
if "%CAM_ORB%"=="2" set CAM_ARG=0
if "%CAM_ORB%"=="0" set CAM_ARG=0

echo.
echo [WEBCAM] Membuka MJPEG Webcam Bridge (Kamera Index %CAM_ARG%) di jendela baru...
start "MJPEG Webcam Bridge" python mjpeg_webcam_bridge.py %CAM_ARG%
echo Menunggu kamera siap (3 detik)...
timeout /t 3 /nobreak >nul
echo.
echo [INFO] Menjalankan ORB-SLAM3 di WSL2...
echo [INFO] Jendela Pangolin 3D Viewer akan segera muncul...
wsl -d Ubuntu-20.04 -- bash -c "export DISPLAY=:0 && ~/slam_ws/run_orbslam3_webcam.sh"
pause
goto end

:bridge
echo.
echo Pilih Webcam untuk Bridge:
echo   [1] USB Camera (Index 1 - Default Webcam USB)
echo   [2] Logitech C922 (Index 0)
echo.
set /p CAM_BR="Pilih [1 atau 2 - Default 1]: "
set CAM_ARG=1
if "%CAM_BR%"=="2" set CAM_ARG=0
if "%CAM_BR%"=="0" set CAM_ARG=0

echo [BRIDGE] Memulai MJPEG Webcam Bridge (Kamera Index %CAM_ARG%)...
echo Port otomatis dipilih (default: 8088).
echo Tekan Ctrl+C untuk berhenti.
python mjpeg_webcam_bridge.py %CAM_ARG%
pause
goto end

:status
echo.
echo [STATUS] Cek WSL2 + GPU OpenGL + Library...
wsl -d Ubuntu-20.04 -- bash -c "echo '=== WSL OpenGL Direct3D12 ===' && glxinfo -B 2>&1 | head -10 && echo '' && echo '=== ORB-SLAM3 Binary ===' && ls -lh ~/slam_ws/ORB_SLAM3/Examples/Monocular/mono_live ~/slam_ws/ORB_SLAM3/lib/libORB_SLAM3.so"
pause
goto end

:end
