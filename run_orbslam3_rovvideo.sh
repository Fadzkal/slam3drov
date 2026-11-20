#!/bin/bash
# ================================================================
# RUN ORB-SLAM3 Monocular pada Rekaman Video ROV Bawah Air
# ================================================================
set -e

ORB_DIR="$HOME/slam_ws/ORB_SLAM3"
VOCAB="$ORB_DIR/Vocabulary/ORBvoc.txt"
CONFIG="$HOME/slam_ws/webcam_640.yaml"
# Deteksi file video: gunakan argumen $1 jika ada, atau cari video terbaru di folder videos
if [ -n "$1" ]; then
    INPUT_VIDEO="$1"
else
    INPUT_VIDEO=$(ls -t /mnt/c/remote_ROV/videos/*.mp4 2>/dev/null | head -n 1)
    if [ -z "$INPUT_VIDEO" ]; then
        INPUT_VIDEO="/mnt/c/remote_ROV/videos/2026-11-16 16-01-50.mp4"
    fi
fi

# Buat symlink bersih tanpa spasi di /tmp/rov_test_video.mp4 agar aman
ln -sf "$INPUT_VIDEO" /tmp/rov_test_video.mp4

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
echo "Video Input : $INPUT_VIDEO"
echo "Active Link : /tmp/rov_test_video.mp4"
echo "Display     : $DISPLAY"
echo "=========================================================="
echo ""

$ORB_DIR/Examples/Monocular/mono_live "$VOCAB" "$CONFIG" /tmp/rov_test_video.mp4
