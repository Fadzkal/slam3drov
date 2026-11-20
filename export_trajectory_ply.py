#!/usr/bin/env python3
"""
export_trajectory_ply.py
=============================================================================
Skrip generator ekspor Trajectory ORB-SLAM3 ke format 3D PLY (Polyline & Frustums)
dan menggabungkannya dengan Map Points (.PLY).

Kompatibel dengan CloudCompare, MeshLab, Blender, dan WebGL Viewer.
Sesuai konvensi ROS REP 103 ENU (X maju, Y kiri, Z atas) via R_align.
=============================================================================
"""

import os
import sys
import math
import numpy as np

# Matriks R_align (RDF optical -> ROS ENU)
# X_enu = Z_opt, Y_enu = -X_opt, Z_enu = -Y_opt
R_ALIGN = np.array([
    [ 0.0,  0.0,  1.0],
    [-1.0,  0.0,  0.0],
    [ 0.0, -1.0,  0.0]
], dtype=np.float32)

def quat_to_rot_matrix(qx, qy, qz, qw):
    """Konversi quaternion ke matriks rotasi 3x3."""
    # Normalisasi quaternion
    norm = math.sqrt(qx*qx + qy*qy + qz*qz + qw*qw)
    if norm < 1e-6:
        return np.eye(3, dtype=np.float32)
    qx, qy, qz, qw = qx/norm, qy/norm, qz/norm, qw/norm
    
    R = np.array([
        [1.0 - 2.0*(qy*qy + qz*qz), 2.0*(qx*qy - qz*qw),       2.0*(qx*qz + qy*qw)],
        [2.0*(qx*qy + qz*qw),       1.0 - 2.0*(qx*qx + qz*qz), 2.0*(qy*qz - qx*qw)],
        [2.0*(qx*qz - qy*qw),       2.0*(qy*qz + qx*qw),       1.0 - 2.0*(qx*qx + qy*qy)]
    ], dtype=np.float32)
    return R

def read_trajectory_tum(traj_file):
    """Membaca file TUM trajectory: timestamp tx ty tz qx qy qz qw."""
    poses = []
    if not os.path.isfile(traj_file):
        print(f"[ERROR] File trajectory '{traj_file}' tidak ditemukan.")
        return poses

    with open(traj_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 8:
                t = float(parts[0])
                tx, ty, tz = float(parts[1]), float(parts[2]), float(parts[3])
                qx, qy, qz, qw = float(parts[4]), float(parts[5]), float(parts[6]), float(parts[7])
                
                # Translasi dalam koordinat optik TUM
                t_tum = np.array([tx, ty, tz], dtype=np.float32)
                R_tum = quat_to_rot_matrix(qx, qy, qz, qw)
                
                # Transformasi ke ROS ENU odom frame
                t_odom = R_ALIGN @ t_tum
                R_odom = R_ALIGN @ R_tum
                
                poses.append({
                    "timestamp": t,
                    "t": t_odom,
                    "R": R_odom,
                    "raw_t": t_tum
                })
    return poses

def create_frustum_wireframe(t, R, scale=0.04):
    """Membuat 5 titik dan 8 rusuk piramida kamera frustum."""
    w = scale
    h = w * 0.75
    z = w * 0.6
    
    # 5 verteks lokal
    V_local = np.array([
        [0.0, 0.0, 0.0],
        [-w,  -h,  z],
        [ w,  -h,  z],
        [ w,   h,  z],
        [-w,   h,  z]
    ], dtype=np.float32)
    
    # Transformasi ke global
    V_global = []
    for v in V_local:
        V_global.append(t + R @ v)
        
    edges = [
        (0, 1), (0, 2), (0, 3), (0, 4),
        (1, 2), (2, 3), (3, 4), (4, 1)
    ]
    return V_global, edges

def export_trajectory_ply(poses, out_ply):
    """Menyimpan lintasan dan piramida kamera ke format PLY dengan garis (edges)."""
    if not poses:
        print("[WARN] Tidak ada pose untuk diekspor.")
        return False
        
    vertices = []
    colors = []
    edges = []
    
    # 1. Tambahkan titik-titik lintasan (Polyline)
    poly_start_idx = 0
    total_len = 0.0
    for i, p in enumerate(poses):
        t = p["t"]
        vertices.append(t)
        if i == 0:
            # Titik Awal: Hijau cerah
            colors.append((16, 185, 129))
        elif i == len(poses) - 1:
            # Titik Akhir: Merah cerah
            colors.append((239, 68, 68))
        else:
            # Titik Lintasan: Cyan cerah
            colors.append((6, 182, 212))
            
        if i > 0:
            edges.append((poly_start_idx + i - 1, poly_start_idx + i))
            d = np.linalg.norm(poses[i]["t"] - poses[i-1]["t"])
            total_len += d

    # 2. Tambahkan piramida kamera untuk setiap KeyFrame
    for i, p in enumerate(poses):
        is_last = (i == len(poses) - 1)
        scale = 0.05 if not is_last else 0.08
        col = (239, 68, 68) if is_last else (37, 99, 235) # Merah utk kamera aktif, Biru utk KeyFrames
        
        v_frustum, e_frustum = create_frustum_wireframe(p["t"], p["R"], scale=scale)
        curr_offset = len(vertices)
        for vf in v_frustum:
            vertices.append(vf)
            colors.append(col)
        for e in e_frustum:
            edges.append((curr_offset + e[0], curr_offset + e[1]))

    # Tulis file ASCII PLY dengan elemen vertex dan edge
    with open(out_ply, "w") as f:
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write(f"element vertex {len(vertices)}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        f.write("property uchar red\n")
        f.write("property uchar green\n")
        f.write("property uchar blue\n")
        f.write(f"element edge {len(edges)}\n")
        f.write("property int vertex1\n")
        f.write("property int vertex2\n")
        f.write("property uchar red\n")
        f.write("property uchar green\n")
        f.write("property uchar blue\n")
        f.write("end_header\n")
        
        for v, c in zip(vertices, colors):
            f.write(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f} {c[0]} {c[1]} {c[2]}\n")
            
        for e in edges:
            f.write(f"{e[0]} {e[1]} 6 182 212\n")
            
    print(f"[OK] Trajectory diekspor ke: {out_ply}")
    print(f"     - Total KeyFrames : {len(poses)}")
    print(f"     - Total Verteks   : {len(vertices)}")
    print(f"     - Total Rusuk     : {len(edges)}")
    print(f"     - Panjang Lintasan: {total_len:.4f} meter")
    return True

def export_merged_map_and_trajectory(map_ply_file, traj_file, out_merged_file):
    """Menggabungkan KeyFrameMapPoints.ply dan lintasan kamera ke dalam satu file PLY."""
    if not os.path.isfile(map_ply_file):
        print(f"[WARN] Map file '{map_ply_file}' tidak ditemukan.")
        return False
        
    poses = read_trajectory_tum(traj_file)
    if not poses:
        print("[WARN] Tidak ada pose untuk digabungkan.")
        return False

    # Baca Map Points
    map_vertices = []
    map_colors = []
    with open(map_ply_file, "r") as f:
        in_header = True
        for line in f:
            line = line.strip()
            if in_header:
                if line == "end_header":
                    in_header = False
                continue
            parts = line.split()
            if len(parts) >= 6:
                map_vertices.append((float(parts[0]), float(parts[1]), float(parts[2])))
                map_colors.append((int(parts[3]), int(parts[4]), int(parts[5])))

    # Siapkan verteks & edges trajectory
    traj_vertices = []
    traj_colors = []
    traj_edges = []
    
    poly_start_idx = len(map_vertices)
    for i, p in enumerate(poses):
        traj_vertices.append(p["t"])
        if i == 0:
            traj_colors.append((16, 185, 129)) # Start
        elif i == len(poses) - 1:
            traj_colors.append((239, 68, 68))  # End
        else:
            traj_colors.append((6, 182, 212))  # Trajectory Line
        if i > 0:
            traj_edges.append((poly_start_idx + i - 1, poly_start_idx + i))
            
    # Tambahkan piramida kamera
    for i, p in enumerate(poses):
        is_last = (i == len(poses) - 1)
        scale = 0.04 if not is_last else 0.07
        col = (239, 68, 68) if is_last else (37, 99, 235)
        
        v_frustum, e_frustum = create_frustum_wireframe(p["t"], p["R"], scale=scale)
        curr_offset = len(map_vertices) + len(traj_vertices)
        for vf in v_frustum:
            traj_vertices.append(vf)
            traj_colors.append(col)
        for e in e_frustum:
            traj_edges.append((curr_offset + e[0], curr_offset + e[1]))

    all_vertices = map_vertices + [tuple(v) for v in traj_vertices]
    all_colors = map_colors + traj_colors

    with open(out_merged_file, "w") as f:
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write(f"element vertex {len(all_vertices)}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        f.write("property uchar red\n")
        f.write("property uchar green\n")
        f.write("property uchar blue\n")
        f.write(f"element edge {len(traj_edges)}\n")
        f.write("property int vertex1\n")
        f.write("property int vertex2\n")
        f.write("property uchar red\n")
        f.write("property uchar green\n")
        f.write("property uchar blue\n")
        f.write("end_header\n")
        
        for v, c in zip(all_vertices, all_colors):
            f.write(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f} {c[0]} {c[1]} {c[2]}\n")
            
        for e in traj_edges:
            f.write(f"{e[0]} {e[1]} 6 182 212\n")

    print(f"[OK] Peta + Trajectory digabung sukses: {out_merged_file}")
    print(f"     - Titik Map Points : {len(map_vertices)}")
    print(f"     - Titik Lintasan   : {len(traj_vertices)}")
    print(f"     - Total Rusuk/Edge : {len(traj_edges)}")
    return True

if __name__ == "__main__":
    traj_path = "KeyFrameTrajectory.txt" if len(sys.argv) < 2 else sys.argv[1]
    map_path = "KeyFrameMapPoints.ply" if len(sys.argv) < 3 else sys.argv[2]
    
    if os.path.isfile(traj_path):
        poses = read_trajectory_tum(traj_path)
        export_trajectory_ply(poses, "KeyFrameTrajectory.ply")
        export_trajectory_ply(poses, "export/KeyFrameTrajectory.ply")
        
        if os.path.isfile(map_path):
            export_merged_map_and_trajectory(map_path, traj_path, "KeyFrameMapAndTrajectory.ply")
            export_merged_map_and_trajectory(map_path, traj_path, "export/KeyFrameMapAndTrajectory.ply")
    else:
        print(f"Gunakan: python export_trajectory_ply.py [trajectory.txt] [map_points.ply]")
