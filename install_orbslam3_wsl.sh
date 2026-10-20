#!/bin/bash
# ================================================================
# SKRIP INSTALASI OTOMATIS ORB-SLAM3 di WSL2 Ubuntu 20.04
# Untuk: Windows 11 + WSL2 + Webcam USB
# ================================================================
set -e  # Hentikan jika ada error

INSTALL_DIR="$HOME/slam_ws"
ORB_SLAM3_DIR="$INSTALL_DIR/ORB_SLAM3"
PANGOLIN_DIR="$INSTALL_DIR/Pangolin"

echo "========================================================"
echo "  INSTALASI ORB-SLAM3 OTOMATIS (WSL2 Ubuntu 20.04)    "
echo "========================================================"
echo "Install directory : $INSTALL_DIR"
echo ""

mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# ── LANGKAH 1: Install dependensi sistem ──
echo ""
echo "[1/6] Install dependensi sistem..."
sudo apt update -y
sudo apt install -y \
    build-essential pkg-config cmake git wget curl unzip \
    libatlas-base-dev libsuitesparse-dev \
    libgtk-3-dev ffmpeg \
    libavcodec-dev libavformat-dev libavutil-dev libswscale-dev \
    libtbb-dev libtbb2 \
    libyaml-cpp-dev \
    libboost-all-dev \
    libssl-dev \
    libusb-1.0-0-dev \
    v4l-utils \
    2>/dev/null || true
echo "[1/6] DONE: Dependensi sistem terinstall."

# ── LANGKAH 2: Install Pangolin (visualizer 3D ORB-SLAM3) ──
echo ""
echo "[2/6] Install Pangolin (Visualizer 3D)..."
if [ ! -d "$PANGOLIN_DIR" ]; then
    git clone --recursive https://github.com/stevenlovegrove/Pangolin.git "$PANGOLIN_DIR"
else
    echo "Pangolin sudah ada, skip clone."
fi

cd "$PANGOLIN_DIR"

# Hapus build lama jika ada agar tidak ada cache error
rm -rf build
mkdir -p build && cd build

cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_EXAMPLES=OFF \
    -DBUILD_TESTS=OFF \
    -DBUILD_PYPANGOLIN=OFF \
    -DPANGO_BUILD_EXAMPLES=OFF \
    -DPANGO_BUILD_TESTS=OFF \
    -DPANGO_WITH_PYTHON=OFF \
    -DCMAKE_CXX_FLAGS="-Wno-error" \
    ..

make -j$(nproc)
sudo make install
sudo ldconfig
echo "[2/6] DONE: Pangolin terinstall."


# ── LANGKAH 3: Clone ORB-SLAM3 ──
echo ""
echo "[3/6] Clone ORB-SLAM3..."
cd "$INSTALL_DIR"
if [ ! -d "$ORB_SLAM3_DIR" ]; then
    git clone https://github.com/UZ-SLAMLab/ORB_SLAM3.git "$ORB_SLAM3_DIR"
else
    echo "ORB-SLAM3 sudah ada, skip clone."
    cd "$ORB_SLAM3_DIR" && git pull
fi
cd "$ORB_SLAM3_DIR"
echo "[3/6] DONE: ORB-SLAM3 di-clone."

# ── LANGKAH 4: Patch kompatibilitas OpenCV 4.x ──
echo ""
echo "[4/6] Patching kompatibilitas OpenCV 4.x Ubuntu 20.04..."

# Patch CMakeLists.txt agar bisa menemukan OpenCV 4
if grep -q "find_package(OpenCV 4.4" CMakeLists.txt; then
    sed -i 's/find_package(OpenCV 4.4/find_package(OpenCV 4.2/' CMakeLists.txt
    echo "   -> Patch OpenCV minimum version: 4.4 -> 4.2"
fi

# Patch include yang sering error di Ubuntu 20.04
find . -name "*.cc" -o -name "*.cpp" -o -name "*.h" | xargs grep -l "include <System.h>" 2>/dev/null | while read f; do
    sed -i 's|#include <System.h>|#include "System.h"|' "$f"
done

echo "[4/6] DONE: Patch selesai."

# ── LANGKAH 5: Build ORB-SLAM3 ──
echo ""
echo "[5/6] Build ORB-SLAM3 (ini akan memakan waktu 10-20 menit)..."
chmod +x build.sh

# Jalankan build dengan -j paralel cores
CPU_CORES=$(nproc)
echo "   Menggunakan $CPU_CORES CPU cores untuk build..."

./build.sh

echo "[5/6] DONE: ORB-SLAM3 berhasil di-build!"

# ── LANGKAH 6: Setup launcher untuk webcam ──
echo ""
echo "[6/6] Membuat script peluncur webcam SLAM..."

VOCAB_FILE="$ORB_SLAM3_DIR/Vocabulary/ORBvoc.txt"

# Buat konfigurasi kamera untuk webcam USB 640x480
cat > "$INSTALL_DIR/webcam_640.yaml" << 'YAML_EOF'
%YAML:1.0

#--------------------------------------------------------------------------------------------
# Camera Parameters. Adjust with your actual webcam calibration!
#--------------------------------------------------------------------------------------------
Camera.type: "PinHole"

# Camera intrinsics (perkiraan awal untuk webcam 640x480)
# Untuk akurasi lebih baik, jalankan kalibrasi kamera OpenCV terlebih dahulu
Camera.fx: 535.0
Camera.fy: 535.0
Camera.cx: 320.0
Camera.cy: 240.0

# Distortion coefficients (perkiraan awal, kalibrasi untuk akurasi lebih baik)
Camera.k1: 0.0
Camera.k2: 0.0
Camera.p1: 0.0
Camera.p2: 0.0

Camera.width: 640
Camera.height: 480

# Camera frames per second
Camera.fps: 30.0

# Color order of the images (0: BGR, 1: RGB. It is ignored if images are grayscale)
Camera.RGB: 1

#--------------------------------------------------------------------------------------------
# ORB Parameters
#--------------------------------------------------------------------------------------------
ORBextractor.nFeatures: 1000
ORBextractor.scaleFactor: 1.2
ORBextractor.nLevels: 8
ORBextractor.iniThFAST: 20
ORBextractor.minThFAST: 7

#--------------------------------------------------------------------------------------------
# Viewer Parameters
#--------------------------------------------------------------------------------------------
Viewer.KeyFrameSize: 0.05
Viewer.KeyFrameLineWidth: 1
Viewer.GraphLineWidth: 0.9
Viewer.PointSize: 2
Viewer.CameraSize: 0.08
Viewer.CameraLineWidth: 3
Viewer.ViewpointX: 0
Viewer.ViewpointY: -0.7
Viewer.ViewpointZ: -1.8
Viewer.ViewpointF: 500
YAML_EOF

# Buat script runner utama
cat > "$INSTALL_DIR/run_orbslam3_webcam.sh" << SCRIPT_EOF
#!/bin/bash
# ORB-SLAM3 Live Webcam Runner
ORB_DIR="$ORB_SLAM3_DIR"
VOCAB="\$ORB_DIR/Vocabulary/ORBvoc.txt"
CONFIG="$INSTALL_DIR/webcam_640.yaml"

echo ""
echo "==========================================="
echo "  ORB-SLAM3 LIVE WEBCAM (Monocular SLAM)  "
echo "==========================================="
echo "Vocabulary : \$VOCAB"
echo "Camera config: \$CONFIG"
echo ""

# Cek apakah ada kamera di /dev/video*
if ls /dev/video* 1>/dev/null 2>&1; then
    echo "Kamera terdeteksi: \$(ls /dev/video*)"
else
    echo "[WARN] Tidak ada /dev/video* -- Coba stream dari Windows via MJPEG bridge"
    echo "[INFO] Jalankan dulu: python3 $INSTALL_DIR/mjpeg_bridge.py di WSL"
    echo "[INFO] Atau jalankan: run_mjpeg_bridge.bat di Windows untuk stream webcam"
fi

echo ""
echo "Mode: Monocular Live Camera"
echo "Jalankan ORB-SLAM3..."
echo ""

# Coba video0 pertama, jika gagal coba video2
CAMERA_DEV=0
if [ -e /dev/video0 ]; then
    CAMERA_DEV=0
elif [ -e /dev/video2 ]; then
    CAMERA_DEV=2
fi

\$ORB_DIR/Examples/Monocular/mono_webcam \$VOCAB \$CONFIG \$CAMERA_DEV
SCRIPT_EOF
chmod +x "$INSTALL_DIR/run_orbslam3_webcam.sh"

# Buat juga script untuk mode video file (test dengan rekaman ROV)
cat > "$INSTALL_DIR/run_orbslam3_rovvideo.sh" << SCRIPT_EOF2
#!/bin/bash
# ORB-SLAM3 ROV Video File Runner
ORB_DIR="$ORB_SLAM3_DIR"
VOCAB="\$ORB_DIR/Vocabulary/ORBvoc.txt"
CONFIG="$INSTALL_DIR/webcam_640.yaml"
VIDEO_FILE="/mnt/c/remote_ROV/videos/YTDown.com_YouTube_Media_g4bUv6Fx3Pk_Site-113-A-Steel-Container-from-a-BlueROV2_001_1080p.mp4"

echo ""
echo "==========================================="
echo "  ORB-SLAM3 ROV VIDEO (Monocular SLAM)    "
echo "==========================================="
echo "File: \$VIDEO_FILE"
echo ""
\$ORB_DIR/Examples/Monocular/mono_video \$VOCAB \$CONFIG "\$VIDEO_FILE"
SCRIPT_EOF2
chmod +x "$INSTALL_DIR/run_orbslam3_rovvideo.sh"

echo "[6/6] DONE: Script peluncur dibuat."
echo ""
echo "========================================================"
echo "  INSTALASI SELESAI!                                    "
echo "========================================================"
echo ""
echo "Cara menjalankan:"
echo "  1. Live Webcam : $INSTALL_DIR/run_orbslam3_webcam.sh"
echo "  2. Video ROV   : $INSTALL_DIR/run_orbslam3_rovvideo.sh"
echo ""
echo "Catatan: Untuk live webcam USB di WSL2, Anda perlu"
echo "         forward USB terlebih dahulu (lihat README)"
echo ""
