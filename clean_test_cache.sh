#!/usr/bin/env bash
# =============================================================================
# Skrip Pembersih Database & Cache SLAM (Reset Pengujian Gagal)
# Proyek: Subsea ROV 3D SLAM - Fadzkal Luthfi Mayzanio
# =============================================================================

echo "=========================================================="
echo "    PEMBERSIH DATABASE SLAM & CACHE PENGUJIAN GAGAL       "
echo "=========================================================="

echo "[1/3] Menghapus database RTAB-Map lama (~/.ros/rtabmap.db)..."
if [ -f "${HOME}/.ros/rtabmap.db" ]; then
    DB_SIZE=$(du -h "${HOME}/.ros/rtabmap.db" | cut -f1)
    rm -f "${HOME}/.ros/rtabmap.db"
    echo "      Berhasil menghapus rtabmap.db (Ukuran sebelumnya: ${DB_SIZE})"
else
    echo "      Database rtabmap.db sudah bersih."
fi

echo "[2/3] Membersihkan log ROS (~/.ros/log)..."
if command -v rosclean &> /dev/null; then
    rosclean purge -y
else
    rm -rf "${HOME}/.ros/log/*"
fi
echo "      Log ROS berhasil dibersihkan."

echo "[3/3] Selesai! Ruang disk telah dibebaskan."
echo "      Database baru yang bersih akan dibuat saat mapping dijalankan lagi."
echo "=========================================================="
