#!/bin/bash
# ================================================================
# RUN DENSE NEURAL-SLAM: ORB-SLAM3 + DEPTH AI (ROV VIDEO)
# ================================================================
set -e

source /opt/ros/noetic/setup.bash
source "$HOME/catkin_ws/devel/setup.bash"

# Auto-sync files from Windows workspace and build
if [ -f /mnt/c/remote_ROV/src/orb_slam3_odom_node.cpp ]; then
    echo "[BUILD] Menyinkronkan update C++, RViz, dan launch file..."
    cp /mnt/c/remote_ROV/src/orb_slam3_odom_node.cpp ~/catkin_ws/src/subsea_3d_mapping/src/
    cp /mnt/c/remote_ROV/monocular_depth_node.py ~/catkin_ws/src/subsea_3d_mapping/scripts/
    cp /mnt/c/remote_ROV/CMakeLists.txt ~/catkin_ws/src/subsea_3d_mapping/
    cp /mnt/c/remote_ROV/package.xml ~/catkin_ws/src/subsea_3d_mapping/
    cp /mnt/c/remote_ROV/subsea_mapping.rviz ~/catkin_ws/src/subsea_3d_mapping/subsea_mapping.rviz
    mkdir -p ~/catkin_ws/src/subsea_3d_mapping/rviz
    cp /mnt/c/remote_ROV/subsea_mapping.rviz ~/catkin_ws/src/subsea_3d_mapping/rviz/subsea_mapping.rviz
    cp /mnt/c/remote_ROV/live_orbslam_dense_mapping.launch ~/catkin_ws/src/subsea_3d_mapping/launch/
    (cd ~/catkin_ws && catkin_make)
    source "$HOME/catkin_ws/devel/setup.bash"
fi

export DISPLAY=${DISPLAY:-:0}

VIDEO_PATH="/mnt/c/remote_ROV/videos/YTDown.com_YouTube_Media_g4bUv6Fx3Pk_Site-113-A-Steel-Container-from-a-BlueROV2_001_1080p.mp4"

echo "=========================================================="
echo "  DENSE NEURAL-SLAM: REKAMAN VIDEO ROV KONTAINER BAWAH LAUT"
echo "=========================================================="
echo "Video File : $VIDEO_PATH"
echo "Display    : $DISPLAY"
echo "=========================================================="
echo ""

roslaunch subsea_3d_mapping live_orbslam_dense_mapping.launch camera_source:="$VIDEO_PATH"
