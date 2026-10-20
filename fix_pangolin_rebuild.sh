#!/bin/bash
# ================================================================
# FIX DEFINITIF Pangolin: Hapus pango_python component
# Error: PyObject_Vectorcall was not declared in this scope
# ================================================================
set -e

PANGOLIN_DIR="$HOME/slam_ws/Pangolin"

echo "========================================================"
echo "  FIX DEFINITIF PANGOLIN: Remove pango_python           "
echo "========================================================"

if [ ! -d "$PANGOLIN_DIR" ]; then
    echo "[ERROR] Pangolin belum ada. Clone dulu:"
    echo "  git clone https://github.com/stevenlovegrove/Pangolin.git ~/slam_ws/Pangolin"
    exit 1
fi

cd "$PANGOLIN_DIR"

# ── Step 1: Hapus folder pango_python sepenuhnya ──
echo ""
echo "[1/4] Menghapus komponen pango_python yang bermasalah..."
rm -rf components/pango_python
echo "      DONE: pango_python dihapus."

# ── Step 2: Patch CMakeLists.txt agar tidak memanggil pango_python ──
echo ""
echo "[2/4] Patch CMakeLists.txt agar skip pango_python..."

# Komentar baris add_subdirectory pango_python jika ada
if grep -q "pango_python" CMakeLists.txt; then
    sed -i 's/.*pango_python.*/#REMOVED_pango_python/' CMakeLists.txt
    echo "      DONE: pango_python dikomentari dari CMakeLists.txt."
else
    echo "      INFO: pango_python tidak ada di CMakeLists.txt root."
fi

# Cek juga di components/CMakeLists.txt
if [ -f "components/CMakeLists.txt" ]; then
    if grep -q "pango_python" components/CMakeLists.txt; then
        sed -i 's/.*pango_python.*/#REMOVED_pango_python/' components/CMakeLists.txt
        echo "      DONE: pango_python dikomentari dari components/CMakeLists.txt."
    fi
fi

# ── Step 3: Bersihkan build cache lama ──
echo ""
echo "[3/4] Membersihkan build cache lama..."
rm -rf build
mkdir -p build && cd build

echo "      CMake configure..."
cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_EXAMPLES=OFF \
    -DBUILD_TESTS=OFF \
    ..

# ── Step 4: Build Pangolin ──
echo ""
echo "[4/4] Build Pangolin ($(nproc) cores)..."
make -j$(nproc)
sudo make install
sudo ldconfig

echo ""
echo "========================================================"
echo "  PANGOLIN BERHASIL DIINSTALL!                         "
echo "========================================================"
echo ""
echo "Langkah selanjutnya — Build ORB-SLAM3:"
echo "  cd ~/slam_ws/ORB_SLAM3"
echo "  chmod +x build.sh && ./build.sh"
echo ""
