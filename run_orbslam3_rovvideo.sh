#!/bin/bash
# ================================================================
# RUN ORB-SLAM3 Monocular pada Rekaman Video ROV Bawah Air
# ================================================================
set -e

ORB_DIR="$HOME/slam_ws/ORB_SLAM3"
VOCAB="$ORB_DIR/Vocabulary/ORBvoc.txt"
CONFIG="$HOME/slam_ws/webcam_640.yaml"
VIDEO_FILE="/mnt/c/remote_ROV/videos/YTDown.com_YouTube_Media_g4bUv6Fx3Pk_Site-113-A-Steel-Container-from-a-BlueROV2_001_1080p.mp4"

# Pastikan config dan jam WSL2 tersinkronisasi
mkdir -p ~/slam_ws
cp /mnt/c/remote_ROV/webcam_640.yaml ~/slam_ws/webcam_640.yaml
sudo hwclock -s 2>/dev/null || true

# Set DISPLAY jika belum ada (WSLg default: :0)
export DISPLAY=${DISPLAY:-:0}
export LIBGL_ALWAYS_SOFTWARE=1

echo "=========================================================="
echo "   ORB-SLAM3: 3D Mapping Rekaman Video ROV Bawah Air      "
echo "=========================================================="
echo "Vocabulary  : $VOCAB"
echo "Config YAML : $CONFIG"
echo "Video Path  : $VIDEO_FILE"
echo "Display     : $DISPLAY"
echo "=========================================================="
echo ""

$ORB_DIR/Examples/Monocular/mono_live "$VOCAB" "$CONFIG" "$VIDEO_FILE"
