#!/bin/bash
# ================================================================
# RUN DENSE NEURAL-SLAM: ORB-SLAM3 + DEPTH AI (ROV VIDEO)
# ================================================================
set -e

source /opt/ros/noetic/setup.bash
source "$HOME/catkin_ws/devel/setup.bash"

# Bersihkan sisa proses lama agar tidak ada port clash
killall -9 roscore rosmaster roslaunch rviz orb_slam3_odom_node 2>/dev/null || true

# Bersihkan file duplikat launch di root paket jika ada
rm -f "$HOME/catkin_ws/src/subsea_3d_mapping/live_orbslam_dense_mapping.launch" 2>/dev/null || true

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
    mkdir -p ~/catkin_ws/src/subsea_3d_mapping/launch
    cp /mnt/c/remote_ROV/live_orbslam_dense_mapping.launch ~/catkin_ws/src/subsea_3d_mapping/launch/
    mkdir -p ~/slam_ws
    cp /mnt/c/remote_ROV/webcam_640.yaml ~/slam_ws/webcam_640.yaml
    (cd ~/catkin_ws && catkin_make)
    source "$HOME/catkin_ws/devel/setup.bash"
fi

# Akselerasi OpenGL Hardware D3D12 untuk WSL2 (mencegah crash swrast_dri)
export GALLIUM_DRIVER=d3d12
export MESA_D3D12_DEFAULT_ADAPTER_NAME=AMD
export LIBGL_ALWAYS_SOFTWARE=0
export DISPLAY=${DISPLAY:-:0}

# Deteksi file video
if [ -n "$1" ]; then
    INPUT_VIDEO="$1"
else
    INPUT_VIDEO=$(ls -t /mnt/c/remote_ROV/videos/*.mp4 2>/dev/null | head -n 1)
    if [ -z "$INPUT_VIDEO" ]; then
        INPUT_VIDEO="/mnt/c/remote_ROV/videos/2026-11-16 16-01-50.mp4"
    fi
fi

# Salin video ke local WSL filesystem ~/slam_ws/current_test.mp4
mkdir -p "$HOME/slam_ws"
cp -f "$INPUT_VIDEO" "$HOME/slam_ws/current_test.mp4"

echo "=========================================================="
echo "  DENSE NEURAL-SLAM: REKAMAN VIDEO ROV BAWAH AIR"
echo "=========================================================="
echo "Video File : $INPUT_VIDEO"
echo "Local Copy : $HOME/slam_ws/current_test.mp4"
echo "Display    : $DISPLAY"
echo "=========================================================="
echo ""

roslaunch "$HOME/catkin_ws/src/subsea_3d_mapping/launch/live_orbslam_dense_mapping.launch" camera_source:="$HOME/slam_ws/current_test.mp4"
