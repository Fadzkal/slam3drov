#!/usr/bin/env bash
# =============================================================================
# run_subsea_mapping.sh
# BlueROV2 Subsea 3D Mapping & Multi-Sensor SLAM Launch Helper
# =============================================================================

set -e

ROV_IP="192.168.2.2"
RTSP_URL="rtsp://${ROV_IP}:8554/video"

echo "=========================================================="
echo "    BlueROV2 Subsea 3D Mapping & Sensor Fusion Pipeline   "
echo "=========================================================="
echo "1. Checking tether connectivity to ROV (${ROV_IP})..."

if ping -c 1 -W 1 "${ROV_IP}" > /dev/null 2>&1; then
    echo "   [OK] ROV is reachable at ${ROV_IP}!"
else
    echo "   [WARNING] ROV is not responding to ping at ${ROV_IP}."
    echo "             Pastikan kabel tether tercolok dan IP adapter laptop di-set ke 192.168.2.1/24."
    echo "             Jika ingin menjalankan offline/dry-run, pipeline tetap akan berjalan."
fi

echo ""
echo "2. Verifying BlueROV2 Video Stream Relay (Port 8555)..."
if curl -s -m 2 http://192.168.2.1:8555/video | head -c 10 > /dev/null 2>&1; then
    echo "   [OK] Live Video Stream Relay is ACTIVE on http://192.168.2.1:8555/video!"
else
    echo "   [INFO] Starting Windows Camera Relay (live_camera_relay.py)..."
    powershell.exe -Command "Start-Process python -ArgumentList 'c:\remote_ROV\live_camera_relay.py' -WindowStyle Hidden" 2>/dev/null || true
    sleep 3
    if curl -s -m 2 http://192.168.2.1:8555/video | head -c 10 > /dev/null 2>&1; then
        echo "   [OK] Camera Relay started successfully!"
    else
        echo "   [WARNING] Camera stream not detected yet. Pastikan UDP stream port 5600 aktif di BlueOS."
    fi
fi

echo ""
echo "2. Sourcing ROS Noetic & Catkin Workspace..."
source /opt/ros/noetic/setup.bash
source ~/catkin_ws/devel/setup.bash

echo "3. Verifying package subsea_3d_mapping..."
PKG_DIR=$(rospack find subsea_3d_mapping)
echo "   Package found at: ${PKG_DIR}"

echo ""
echo "4. Menjalankan Subsea 3D Mapping..."
echo "   Pipeline:"
echo "   - MAVROS MAVLink Telemetry (UDP 14550)"
echo "   - HD Video Stream (RTSP / OpenCV)"
echo "   - CLAHE Underwater Contrast Enhancement"
echo "   - Bar30 Hydrostatic Pressure (Z-lock) & Ping1D Sonar (Range & Metric Anchor)"
echo "   - MiDaS ONNX Metric Monocular Depth"
echo "   - RTAB-Map RGB-D Odometry (ORB features)"
echo "   - robot_localization EKF (fusi IMU + Bar30 + Visual Odometry)"
echo "   - RTAB-Map SLAM (Dense 3D Mapping & Loop Closure)"
echo "   - ROV Trajectory Path Tracker & 3D Body Marker"
echo "   - RViz 3D Visualizer"
echo ""

roslaunch subsea_3d_mapping subsea_3d_mapping.launch "$@"
