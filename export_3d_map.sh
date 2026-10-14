#!/usr/bin/env bash
set -e

echo "========================================================"
echo "   SUBSEA 3D SLAM EXPORTER (RTAB-MAP -> PLY 3D MODEL)   "
echo "========================================================"

DB_PATH="${HOME}/.ros/rtabmap.db"
EXPORT_DIR="/mnt/c/remote_ROV/export"
OUTPUT_PLY="${EXPORT_DIR}/subsea_3d_map.ply"
SNAPSHOT_DB="/tmp/rtabmap_export_snapshot.db"

if [ ! -f "$DB_PATH" ]; then
    echo "[ERROR] Database RTAB-Map tidak ditemukan di $DB_PATH"
    echo "Pastikan live mapping sudah pernah dijalankan minimal 1 frame."
    exit 1
fi

mkdir -p "$EXPORT_DIR"

echo "[1/3] Membuat snapshot database RTAB-Map (${DB_PATH})..."
# Copy to temporary file to avoid database lock if RTAB-Map is still running
cp -f "$DB_PATH" "$SNAPSHOT_DB"

echo "[2/3] Mengekspor Dense Point Cloud 3D menggunakan rtabmap-export..."
source /opt/ros/noetic/setup.bash 2>/dev/null || source /opt/ros/melodic/setup.bash 2>/dev/null || true

# rtabmap-export extracts the assembled colored point cloud with voxel grid filtering
rtabmap-export --ply --voxel 0.015 --decimation 2 --output_dir "$EXPORT_DIR" --output "subsea_3d_map" "$SNAPSHOT_DB"

# Check output file
if [ -f "$OUTPUT_PLY" ]; then
    FILE_SIZE=$(du -h "$OUTPUT_PLY" | cut -f1)
    echo "[3/3] BERHASIL! File 3D diekspor ke: $OUTPUT_PLY ($FILE_SIZE)"
    rm -f "$SNAPSHOT_DB"
elif [ -f "${EXPORT_DIR}/subsea_3d_map_mesh.ply" ]; then
    mv "${EXPORT_DIR}/subsea_3d_map_mesh.ply" "$OUTPUT_PLY"
    FILE_SIZE=$(du -h "$OUTPUT_PLY" | cut -f1)
    echo "[3/3] BERHASIL! File 3D diekspor ke: $OUTPUT_PLY ($FILE_SIZE)"
    rm -f "$SNAPSHOT_DB"
else
    # Check for any ply in export dir
    GENERATED_PLY=$(ls -t "${EXPORT_DIR}"/*.ply 2>/dev/null | head -n 1)
    if [ -n "$GENERATED_PLY" ]; then
        cp -f "$GENERATED_PLY" "$OUTPUT_PLY"
        echo "[3/3] File 3D ditemukan: $GENERATED_PLY -> $OUTPUT_PLY"
    else
        echo "[!] Peringatan: Ekspor manual mungkin diperlukan jika database sedang di-lock penuh."
    fi
    rm -f "$SNAPSHOT_DB"
fi

echo "========================================================"
echo "Selesai! Buka view_slam_3d_web.html di browser Anda."
echo "========================================================"
