@echo off
title BlueROV2 Live 3D Mapping & RViz Pipeline
echo ====================================================================
echo   BLUEROV2 LIVE 3D SLAM & RVIZ PIPELINE (FAST & SMOOTH)
echo   Direct Camera + MiDaS Depth + RTAB-Map SLAM + BlueOS Telemetry
echo ====================================================================
echo.

:: 1. Check if camera relay is running on port 8555
netstat -ano | findstr :8555 >nul
if %ERRORLEVEL% NEQ 0 (
    echo [*] Starting Camera Relay on port 8555...
    start /min "BlueROV2 Camera Relay" python "c:\remote_ROV\live_camera_relay.py"
    timeout /t 2 /nobreak >nul
) else (
    echo [*] Camera Relay is already active on port 8555.
)

:: 2. Launch WSL ROS pipeline
echo [*] Launching ROS Noetic + RTAB-Map SLAM + RViz...
wsl -d Ubuntu-20.04 bash -c "source /opt/ros/noetic/setup.bash; source ~/catkin_ws/devel/setup.bash; export DISPLAY=:0; export LIBGL_ALWAYS_INDIRECT=0; roslaunch subsea_3d_mapping live_rov_3d_mapping.launch"

pause
