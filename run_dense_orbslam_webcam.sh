#!/bin/bash
# ================================================================
# RUN DENSE NEURAL-SLAM: ORB-SLAM3 + DEPTH AI (MiDaS) + RTAB-MAP
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

echo "=========================================================="
echo "  DENSE NEURAL-SLAM: ORB-SLAM3 + DEPTH AI + RTAB-MAP       "
echo "=========================================================="

PORT=8088
if [ -f /mnt/c/remote_ROV/bridge_port.txt ]; then
    PORT=$(cat /mnt/c/remote_ROV/bridge_port.txt | tr -d '\r\n')
fi

SOURCE=""

# 1. Cek apakah ada /dev/video* di Linux
if [ -e /dev/video0 ]; then
    echo "[INFO] Kamera USB langsung terdeteksi di /dev/video0"
    SOURCE="0"
elif [ -e /dev/video2 ]; then
    echo "[INFO] Kamera USB langsung terdeteksi di /dev/video2"
    SOURCE="2"
else
    # 2. Cari IP Windows Host (Gateway WSL2)
    GW_IP=$(ip route | grep default | awk '{print $3}' | head -1)
    NS_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}' | head -1)

    echo "[INFO] Mencari koneksi MJPEG Webcam Bridge Windows (Port $PORT)..."

    CANDIDATES=("$GW_IP" "$NS_IP" "localhost" "192.168.0.110")
    FOUND=""

    for attempt in 1 2 3 4 5; do
        for IP in "${CANDIDATES[@]}"; do
            if [ -n "$IP" ]; then
                if curl -s --connect-timeout 1 "http://$IP:$PORT/" >/dev/null 2>&1; then
                    FOUND="$IP"
                    break 2
                fi
            fi
        done
        echo "  [Percobaan $attempt/5] Menunggu MJPEG Bridge merespon..."
        sleep 1
    done

    if [ -n "$FOUND" ]; then
        SOURCE="http://$FOUND:$PORT/stream.mjpg"
        echo "[OK] Terhubung ke MJPEG Bridge via: $SOURCE"
    else
        echo ""
        echo "[PERINGATAN] Bridge tidak merespon di kandidat IP."
        echo "Menggunakan default Gateway WSL2: http://${GW_IP:-172.19.32.1}:$PORT/stream.mjpg"
        SOURCE="http://${GW_IP:-172.19.32.1}:$PORT/stream.mjpg"
    fi
fi

echo ""
echo "[INFO] Meluncurkan Fusi Dense Neural-SLAM..."
echo "[INFO] Input Camera: $SOURCE"
echo "[INFO] Membuka jendela Pangolin + RViz 3D Visualizer..."
echo ""

roslaunch subsea_3d_mapping live_orbslam_dense_mapping.launch camera_source:="$SOURCE"
