#!/usr/bin/env bash
set -e
source /opt/ros/noetic/setup.bash
source ~/catkin_ws/devel/setup.bash
export DISPLAY=:0
export LIBGL_ALWAYS_INDIRECT=0
echo "Membuka Live BlueROV2 3D Mapping & RViz..."
roslaunch subsea_3d_mapping live_rov_3d_mapping.launch "$@"
