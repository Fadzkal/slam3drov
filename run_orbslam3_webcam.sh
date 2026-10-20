#!/bin/bash
# ================================================================
# RUN ORB-SLAM3 Monocular Live Webcam
# ================================================================
set -e

ORB_DIR="$HOME/slam_ws/ORB_SLAM3"
VOCAB="$ORB_DIR/Vocabulary/ORBvoc.txt"
CONFIG="$HOME/slam_ws/webcam_640.yaml"

export DISPLAY=${DISPLAY:-:0}

echo "=========================================================="
echo "   ORB-SLAM3: 3D Mapping Live Webcam (Monocular SLAM)     "
echo "=========================================================="
echo "Vocabulary  : $VOCAB"
echo "Config YAML : $CONFIG"
echo "Display     : $DISPLAY"
echo "=========================================================="
echo ""

# Baca port bridge jika tersedia
PORT=8088
if [ -f /mnt/c/remote_ROV/bridge_port.txt ]; then
    PORT=$(cat /mnt/c/remote_ROV/bridge_port.txt | tr -d '\r\n')
fi

# Deteksi sumber kamera
SOURCE=""

# 1. Cek apakah ada /dev/video* di Linux
if [ -e /dev/video0 ]; then
    echo "[INFO] Kamera USB langsung terdeteksi di /dev/video0"
    SOURCE="0"
elif [ -e /dev/video2 ]; then
    echo "[INFO] Kamera USB langsung terdeteksi di /dev/video2"
    SOURCE="2"
else
    # 2. Cari IP Windows Host
    # A. Gateway WSL2
    GW_IP=$(ip route | grep default | awk '{print $3}' | head -1)
    # B. Nameserver di resolv.conf
    NS_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}' | head -1)

    echo "[INFO] Tidak ada /dev/video* di dalam WSL2."
    echo "[INFO] Mencoba MJPEG Bridge Windows pada Port $PORT..."

    CANDIDATES=("localhost" "$GW_IP" "$NS_IP" "192.168.0.110")
    FOUND=""

    for IP in "${CANDIDATES[@]}"; do
        if [ -n "$IP" ]; then
            echo -n "  Cek http://$IP:$PORT/ ... "
            if curl -s --connect-timeout 1 "http://$IP:$PORT/" >/dev/null 2>&1; then
                echo "OK!"
                FOUND="$IP"
                break
            else
                echo "tidak merespon"
            fi
        fi
    done

    if [ -n "$FOUND" ]; then
        SOURCE="http://$FOUND:$PORT/stream.mjpg"
        echo "[OK] Terhubung ke MJPEG Bridge via $SOURCE"
    else
        echo ""
        echo "[WARN] MJPEG Bridge di Windows belum siap atau belum aktif."
        echo "Pastikan 'mjpeg_webcam_bridge.py' sedang berjalan di Windows."
        echo "Mencoba default: http://$GW_IP:$PORT/stream.mjpg"
        SOURCE="http://${GW_IP:-localhost}:$PORT/stream.mjpg"
    fi
fi

echo ""
echo "Menggunakan input: $SOURCE"
echo "Membuka Pangolin 3D Viewer..."
echo ""

$ORB_DIR/Examples/Monocular/mono_live "$VOCAB" "$CONFIG" "$SOURCE"
