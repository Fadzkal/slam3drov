@echo off
echo ====================================================================
echo   LAUNCHING UNDERWATER VISUAL-INERTIAL SLAM (VINS-Mono + CLAHE)
echo   Based on IEEE IROS Paper SVIn2 (Rahman, Quattrini Li, Rekleitis)
echo ====================================================================
echo.

wsl -d Ubuntu-20.04 bash -c "source /opt/ros/noetic/setup.bash; source ~/catkin_ws/devel/setup.bash; export DISPLAY=:0; export LIBGL_ALWAYS_INDIRECT=0; roslaunch subsea_3d_mapping live_underwater_vins.launch"

pause
