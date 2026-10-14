@echo off
title BlueROV2 Subsea 3D Mapping Pipeline
echo ====================================================================
echo   LAUNCHING BLUEROV2 SUBSEA 3D MAPPING ^& SENSOR FUSION PIPELINE
echo   ROS Noetic + RTAB-Map SLAM + Bar30 + Ping1D + EKF + RViz
echo ====================================================================
echo.

wsl -d Ubuntu-20.04 bash -c "export DISPLAY=:0; export LIBGL_ALWAYS_INDIRECT=0; ~/run_subsea_mapping.sh"

pause
