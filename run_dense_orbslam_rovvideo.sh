#!/bin/bash
# ================================================================
# RUN DENSE NEURAL-SLAM: ORB-SLAM3 + DEPTH AI (ROV VIDEO)
# ================================================================
set -e

source /opt/ros/noetic/setup.bash
source "$HOME/catkin_ws/devel/setup.bash"

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
