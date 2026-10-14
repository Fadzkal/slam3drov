#!/bin/bash
source /opt/ros/noetic/setup.bash
source /home/fadzkal_luthfi/catkin_ws/devel/setup.bash
roslaunch subsea_3d_mapping live_rov_3d_mapping.launch &
LPID=$!
sleep 10
echo "=== TOPIC LIST ==="
rostopic list
echo "=== CHECKING /rtabmap/odom ==="
timeout 4 rostopic echo /rtabmap/odom/pose/pose/position -n 2 || true
echo "=== CHECKING /rtabmap/cloud_map ==="
timeout 4 rostopic hz /rtabmap/cloud_map || true
kill $LPID
pkill -f ros
