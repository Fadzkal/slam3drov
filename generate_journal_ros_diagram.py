#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_journal_ros_diagram.py
=============================================================================
Menghasilkan Diagram Arsitektur Graf Komputasi ROS & Rantai Transformasi TF2
dengan Standar Publikasi Jurnal Internasional IEEE (T-RO / IROS / ICRA).
- Background Putih Murni (#FFFFFF)
- Zero-Overlap Layout (Penyusunan Teks & Panah Matematis Sangat Rapi)
- Panel (a): ROS Computational Graph (Node & Topik Terstruktur per Stage)
- Panel (b): Hierarchical TF2 Transform Tree (Lengkap dengan Offset Spasial Metrik)
=============================================================================
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

def create_diagram():
    fig = plt.figure(figsize=(19.2, 10.8), dpi=300, facecolor='#FFFFFF')
    ax = fig.add_axes([0, 0, 1, 1], facecolor='#FFFFFF')
    ax.set_xlim(0, 1920)
    ax.set_ylim(0, 1080)
    ax.axis('off')

    # -------------------------------------------------------------------------
    # PALET WARNA PROFESIONAL IEEE
    # -------------------------------------------------------------------------
    C_TEXT_MAIN = '#0F172A'    # Slate 900
    C_TEXT_MUTED = '#475569'   # Slate 600
    
    # Kategori Warna Node
    C_DRIVER_BG = '#F0F7FF'
    C_DRIVER_BORDER = '#2563EB'
    C_DRIVER_HDR = '#1E40AF'
    
    C_PERCEP_BG = '#F0FDFA'
    C_PERCEP_BORDER = '#0D9488'
    C_PERCEP_HDR = '#115E59'
    
    C_TRACK_BG = '#F0FDF4'
    C_TRACK_BORDER = '#16A34A'
    C_TRACK_HDR = '#166534'
    
    C_SLAM_BG = '#FAF5FF'
    C_SLAM_BORDER = '#9333EA'
    C_SLAM_HDR = '#6B21A8'
    
    C_VIS_BG = '#FFF1F2'
    C_VIS_BORDER = '#E11D48'
    C_VIS_HDR = '#9F1239'

    # -------------------------------------------------------------------------
    # HEADER UTAMA DIAGRAM
    # -------------------------------------------------------------------------
    ax.text(960, 1052, "ARSITEKTUR GRAF KOMPUTASI ROS & RANTAI TRANSFORMASI SPASIAL TF2",
            ha='center', va='center', fontsize=17.5, fontweight='bold', color=C_TEXT_MAIN,
            fontfamily='DejaVu Sans')
    ax.text(960, 1027, "Sistem Fusi Dense Neural-SLAM: Integrasi Pelacakan 6-DoF ORB-SLAM3, Estimasi Kedalaman AI MiDaS, dan RTAB-Map pada BlueROV2",
            ha='center', va='center', fontsize=11, fontstyle='italic', color=C_TEXT_MUTED,
            fontfamily='DejaVu Sans')

    # -------------------------------------------------------------------------
    # PANEL (a): ROS COMPUTATIONAL NODE GRAPH (Top 65% of Canvas)
    # -------------------------------------------------------------------------
    rect_a = FancyBboxPatch((40, 385), 1840, 620, boxstyle="round,pad=0,rounding_size=12",
                           facecolor='#FFFFFF', edgecolor='#94A3B8', linewidth=1.5, zorder=1)
    ax.add_patch(rect_a)
    
    ax.text(65, 985, "(a) Graf Komputasi ROS 1 (Asynchronous Distributed Node Pipeline & Topic Data Flow)",
            ha='left', va='center', fontsize=12.5, fontweight='bold', color='#1E293B',
            fontfamily='DejaVu Sans', zorder=2)

    # 4 Kolom Stage Background Shading
    stages = [
        ("STAGE 1: HARDWARE BRIDGES", 58, 385, "#F8FAFC"),
        ("STAGE 2: PRE-PROCESSING & AI PERCEPTION", 458, 435, "#F8FAFC"),
        ("STAGE 3: 6-DoF TRACKING & FUSION", 908, 440, "#F8FAFC"),
        ("STAGE 4: 3D SLAM & VISUALIZATION", 1363, 500, "#F8FAFC")
    ]
    for title, sx, sw, sbg in stages:
        s_rect = FancyBboxPatch((sx, 400), sw, 565, boxstyle="round,pad=0,rounding_size=8",
                                facecolor=sbg, edgecolor='#E2E8F0', linewidth=1, zorder=1)
        ax.add_patch(s_rect)
        ax.text(sx + sw/2, 945, title, ha='center', va='center',
                fontsize=9.5, fontweight='bold', color='#64748B', fontfamily='DejaVu Sans', zorder=2)

    # Fungsi pembantu untuk membuat ROS Node Card (dengan va='top' agar zero-overlap)
    def draw_node(x, y, w, h, node_name, pkg_name, role_desc, bg_col, bdr_col, hdr_col):
        card = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=6",
                              facecolor=bg_col, edgecolor=bdr_col, linewidth=1.8, zorder=3)
        ax.add_patch(card)
        # Header Bar
        hdr_rect = FancyBboxPatch((x, y + h - 24), w, 24, boxstyle="round,pad=0,rounding_size=6",
                                  facecolor=bdr_col, edgecolor=bdr_col, linewidth=0, zorder=4)
        ax.add_patch(hdr_rect)
        ax.text(x + w/2, y + h - 12, node_name, ha='center', va='center',
                fontsize=10, fontweight='bold', color='#FFFFFF', fontfamily='DejaVu Sans', zorder=5)
        # Subtitle
        ax.text(x + w/2, y + h - 36, pkg_name, ha='center', va='center',
                fontsize=8.5, fontweight='bold', color=hdr_col, fontfamily='DejaVu Sans', zorder=5)
        # Description flowing top-down
        ax.text(x + w/2, y + h - 49, role_desc, ha='center', va='top',
                fontsize=7.8, color='#334155', fontfamily='DejaVu Sans', multialignment='center',
                linespacing=1.25, zorder=5)

    # Fungsi pembantu untuk menggambar Badge Topik
    def draw_topic_badge(x, y, w, h, topic_name, msg_type):
        badge = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=5",
                               facecolor='#FFFFFF', edgecolor='#64748B', linewidth=1.2, zorder=4)
        ax.add_patch(badge)
        ax.text(x + w/2, y + h*0.64, topic_name, ha='center', va='center',
                fontsize=8, fontweight='bold', color='#0F172A', fontfamily='DejaVu Sans', zorder=5)
        ax.text(x + w/2, y + h*0.28, f"[{msg_type}]", ha='center', va='center',
                fontsize=7, color='#0284C7', fontfamily='DejaVu Sans', zorder=5)

    # Fungsi panah penghubung
    def draw_arrow(x1, y1, x2, y2, color='#334155', style="->", rad=0.0):
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                                connectionstyle=f"arc3,rad={rad}",
                                arrowstyle=style, mutation_scale=11,
                                color=color, linewidth=1.5, zorder=2)
        ax.add_patch(arrow)

    # --- NODE STAGE 1 (Hardware Bridges) ---
    draw_node(75, 795, 350, 115, "/mjpeg_webcam_bridge", "Package: subsea_3d_mapping (Python)",
              "Akuisisi Kamera ROV CMOS USB 1/2.7\"\nDirectShow CAP_PROP_BUFFERSIZE=1 (Latensi < 80ms)\nHTTP MJPEG Streaming Server Port 8088",
              C_DRIVER_BG, C_DRIVER_BORDER, C_DRIVER_HDR)

    draw_node(75, 635, 350, 125, "/blueos_live_bridge", "Package: subsea_3d_mapping (Python)",
              "Polling REST API MAVLink @ 192.168.2.2 (30 Hz)\nEkstraksi ATTITUDE, RAW_IMU, & VFR_HUD\nDeadband Orientasi (<0.85°) & Gyro (<1.5°/s)",
              C_DRIVER_BG, C_DRIVER_BORDER, C_DRIVER_HDR)

    draw_node(75, 425, 350, 175, "/depth_to_pose_publisher", "Package: subsea_3d_mapping (Python)",
              "Dual Redundant Depth & Sonar Bridge:\n• Fallback MAVROS /mavros/altitude\n• Bar30 Hydrostatic Z (±2mm, Cov: 1e-4 m²)\n• Ping1D 115kHz 5-Sample Median Filter\nKonversi Kedalaman ke ROS REP 103 (Z negatif)",
              C_DRIVER_BG, C_DRIVER_BORDER, C_DRIVER_HDR)

    # --- TOPIC BADGES DARI STAGE 1 ---
    draw_topic_badge(445, 840, 200, 36, "/camera/image_raw", "sensor_msgs/Image (30Hz)")
    draw_topic_badge(445, 690, 200, 36, "/mavros/imu/data", "sensor_msgs/Imu (30Hz)")
    draw_topic_badge(445, 520, 200, 36, "/bar30/pose_depth", "PoseWithCovariance (10Hz)")
    draw_topic_badge(445, 445, 200, 36, "/sonar/ping1d/range", "sensor_msgs/Range (10Hz)")

    # Panah Stage 1 -> Topik
    draw_arrow(425, 858, 445, 858)
    draw_arrow(425, 708, 445, 708)
    draw_arrow(425, 538, 445, 538)
    draw_arrow(425, 463, 445, 463)

    # --- NODE STAGE 2 (Perception & AI Depth) ---
    draw_node(665, 790, 215, 120, "/underwater_clahe", "Python Node (OpenCV)",
              "Arsitektur SVIn2 (IEEE IROS)\nKonversi BGR -> LAB\nCLAHE Kanal L (Clip: 2.5)\nRestorasi Kontras & Kekeruhan Air",
              C_PERCEP_BG, C_PERCEP_BORDER, C_PERCEP_HDR)

    draw_node(665, 435, 215, 310, "/monocular_depth_ai", "Python Node (ONNX Runtime)",
              "Model MiDaS DPT / Small (CPU/CUDA)\nInput ImageNet Norm (256x256)\nPercentile Clipping [2%, 98%]\n\nFormulasi Hiperbolik Metrik:\nZ(d) = 1 / (2.6349·d + 0.2222)\n\nPenguncian Skala Akustik:\nAnchor Median 10% Ping1D\nInner Masking 5% Anti-Flare\nExact Time Synchronizer",
              C_PERCEP_BG, C_PERCEP_BORDER, C_PERCEP_HDR)

    # Panah Topik Stage 1 -> Stage 2
    draw_arrow(645, 858, 665, 858)
    draw_arrow(645, 858, 665, 675, rad=-0.2)
    draw_arrow(645, 463, 665, 500, rad=0.1)

    # --- TOPIC BADGES DARI STAGE 2 ---
    draw_topic_badge(895, 830, 200, 36, "/camera/image_enhanced", "sensor_msgs/Image")
    draw_topic_badge(895, 640, 200, 36, "/camera/synced/depth", "Image 32FC1 Metrik")
    draw_topic_badge(895, 580, 200, 36, "/camera/synced/image", "sensor_msgs/Image")
    draw_topic_badge(895, 520, 200, 36, "/camera/synced/camera_info", "sensor_msgs/CameraInfo")
    draw_topic_badge(895, 445, 200, 36, "/camera/depth/points", "PointCloud2 (Real-time)")

    draw_arrow(880, 848, 895, 848)
    draw_arrow(880, 658, 895, 658)
    draw_arrow(880, 598, 895, 598)
    draw_arrow(880, 538, 895, 538)
    draw_arrow(880, 463, 895, 463)

    # --- NODE STAGE 3 (Tracking & State Estimation) ---
    draw_node(1115, 715, 220, 215, "/orb_slam3_odom", "C++ Node (ORB-SLAM3)",
              "Ekstraksi FAST & ORB 256-bit\nTightly-Coupled Visual BA\nState SE(3): T_w,c (30 Hz)\n\nRotasi Ortogonal R_align:\nRDF Optis -> ROS REP 103 ENU\n\nWireframe Marker Generator:\n• Merah (Pose Kamera Aktif)\n• Biru (Riwayat KeyFrames)\n• Hijau (Covisibility Graph)",
              C_TRACK_BG, C_TRACK_BORDER, C_TRACK_HDR)

    draw_node(1115, 435, 220, 230, "/ekf_localization", "Package: robot_localization",
              "Extended Kalman Filter (30 Hz)\nFusi Sensor Multi-Tingkat:\n• IMU (Roll, Pitch, Angular Vel)\n• Bar30 Absolute Z (Mahalanobis 2σ)\n• Visual Odometry (X, Y, Z, Yaw)\n\nOutput: /odometry/filtered\nPublish TF: odom -> base_link",
              C_SLAM_BG, C_SLAM_BORDER, C_SLAM_HDR)

    # Panah Stage 2 -> Stage 3
    draw_arrow(1095, 848, 1115, 848)
    draw_arrow(645, 708, 1115, 615, rad=-0.15) # IMU ke EKF
    draw_arrow(645, 538, 1115, 538) # Bar30 pose_depth ke EKF

    # Topik dari Stage 3
    draw_topic_badge(1355, 825, 180, 36, "/rtabmap/odom", "nav_msgs/Odometry")
    draw_topic_badge(1355, 755, 180, 36, "/orb_slam3/sparse_points", "PointCloud2 (RGB)")
    draw_topic_badge(1355, 545, 180, 36, "/odometry/filtered", "nav_msgs/Odometry (EKF)")

    draw_arrow(1335, 843, 1355, 843)
    draw_arrow(1335, 773, 1355, 773)
    draw_arrow(1335, 843, 1115, 570, rad=0.2) # Odom ORB-SLAM3 ke EKF
    draw_arrow(1335, 563, 1355, 563)

    # --- NODE STAGE 4 (3D Volumetric SLAM & Visualisasi) ---
    draw_node(1560, 715, 285, 215, "/rtabmap_slam", "Package: rtabmap_slam (C++)",
              "Dense RGB-D SLAM & Loop Closure Memory\n3-Stage Filtering Pipeline:\n1. PassThrough [0.35m - 4.50m]\n2. Statistical Outlier Removal (k=30, σ=1.0)\n3. OctoMap Voxel Grid (Cell Size: 0.05 m)\n\nDeteksi Loop Closure via DBoW2 / ORB\nGlobal Bundle Adjustment Optimization",
              C_SLAM_BG, C_SLAM_BORDER, C_SLAM_HDR)

    draw_node(1560, 560, 285, 135, "/egoexo_ground_surface", "Package: subsea_3d_mapping (Python)",
              "Estimasi Permukaan 2.5D (EgoExo++)\nZ_ground = min(Z_path) - 0.12 m\nLantai Planar Soft Teal (#5B8C9B, α=0.85)\nLintasan Kuning (#FFE600, +1.5cm offset)\nDatum Keselamatan Anti-Collision Pilot",
              C_VIS_BG, C_VIS_BORDER, C_VIS_HDR)

    draw_node(1560, 420, 285, 115, "/rov_trajectory_tracker", "Package: subsea_3d_mapping (Python)",
              "Pelacak Lintasan ROV 3D (/robot_path)\nAnti-Teleport Filter (>0.4m step rejected)\nModel Kubus Bodi BlueROV2 (45x34x25cm)\nPerhitungan Total Jarak Tempuh (m)",
              C_VIS_BG, C_VIS_BORDER, C_VIS_HDR)

    # Panah ke Stage 4
    draw_arrow(1535, 843, 1560, 843) # Odom ke RTAB-Map
    draw_arrow(1095, 658, 1560, 785, rad=-0.2) # Synced Depth ke RTAB-Map
    draw_arrow(1095, 598, 1560, 760, rad=-0.25) # Synced Image ke RTAB-Map
    draw_arrow(1535, 563, 1560, 478, rad=-0.1) # Odom filtered ke Trajectory tracker
    draw_arrow(1700, 535, 1700, 560) # Trajectory tracker (/robot_path) ke EgoExo surface

    # Topik /robot_path Badge
    draw_topic_badge(1705, 525, 125, 28, "/robot_path", "nav_msgs/Path")

    # -------------------------------------------------------------------------
    # PANEL (b): HIERARCHICAL TF2 TRANSFORM TREE (Bottom 33% of Canvas)
    # -------------------------------------------------------------------------
    rect_b = FancyBboxPatch((40, 25), 1840, 340, boxstyle="round,pad=0,rounding_size=12",
                           facecolor='#FFFFFF', edgecolor='#94A3B8', linewidth=1.5, zorder=1)
    ax.add_patch(rect_b)

    ax.text(65, 345, "(b) Rantai Hierarki Transformasi Koordinat Spasial TF2 Tree (Rigid Body Geometric Offsets)",
            ha='left', va='center', fontsize=12.5, fontweight='bold', color='#1E293B',
            fontfamily='DejaVu Sans', zorder=2)

    # Fungsi kartu frame TF (dengan va='top' agar zero-overlap)
    def draw_tf_frame(x, y, w, h, frame_id, frame_type, broadcaster, offset_text, bg_col, bdr_col):
        card = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=6",
                              facecolor=bg_col, edgecolor=bdr_col, linewidth=1.6, zorder=3)
        ax.add_patch(card)
        ax.text(x + w/2, y + h - 14, frame_id, ha='center', va='center',
                fontsize=10.5, fontweight='bold', color='#0F172A', fontfamily='DejaVu Sans', zorder=4)
        ax.text(x + w/2, y + h - 30, f"[{frame_type}]", ha='center', va='center',
                fontsize=8, fontweight='bold', color=bdr_col, fontfamily='DejaVu Sans', zorder=4)
        ax.text(x + w/2, y + h - 44, f"Broadcaster: {broadcaster}", ha='center', va='center',
                fontsize=7.5, color='#475569', fontfamily='DejaVu Sans', zorder=4)
        ax.text(x + w/2, y + h - 56, offset_text, ha='center', va='top',
                fontsize=7.5, color='#1E293B', fontfamily='DejaVu Sans', multialignment='center',
                linespacing=1.2, zorder=4)

    # 1. map
    draw_tf_frame(80, 180, 205, 120, "map", "Global Origin", "/rtabmap_slam",
                  "Datum Global Peta 3D\nZ-Up, X-East, Y-North\nOrigin Tetap di Titik Mulai",
                  '#F8FAFC', '#3B82F6')

    # 2. odom
    draw_tf_frame(380, 180, 225, 120, "odom", "Odometry Frame", "/ekf_localization",
                  "Kerangka Odometri Kontinu\nKoreksi Loop Closure RTAB-Map\nMenghilangkan Drift Akumulatif",
                  '#F8FAFC', '#6366F1')

    # 3. base_link
    draw_tf_frame(700, 180, 240, 120, "base_link", "Body Center", "/ekf_localization",
                  "Pusat Massa Fisik BlueROV2\nAcuan Rigid Body Seluruh Sensor\nt = [X_ekf, Y_ekf, Z_bar30]\nR = [Roll_imu, Pitch_imu, Yaw_vo]",
                  '#FEF2F2', '#EF4444')

    # Panah map -> odom -> base_link
    draw_arrow(285, 240, 380, 240, color='#2563EB', style="->")
    ax.text(332, 256, "T_map_odom\n(Loop Closure)", ha='center', va='center', fontsize=7.5, color='#2563EB', fontfamily='DejaVu Sans')

    draw_arrow(605, 240, 700, 240, color='#4F46E5', style="->")
    ax.text(652, 256, "T_odom_base\n(Fused EKF)", ha='center', va='center', fontsize=7.5, color='#4F46E5', fontfamily='DejaVu Sans')

    # Daun Sensorik dari base_link (Cabang ke 4 Sensor Fisik)
    draw_tf_frame(1030, 180, 240, 120, "camera_link", "Sensor Frame", "static_tf_publisher",
                  "Offset Fisik Kamera Depan:\nt = [+0.18, 0.00, +0.05] m\nR = [0.0°, 0.0°, 0.0°]\n(18 cm Depan, 5 cm Atas)",
                  '#F0FDF4', '#16A34A')

    draw_tf_frame(1355, 180, 250, 120, "camera_optical_link", "Optical Frame", "static_tf_publisher",
                  "Konvensi Optis Pinhole RDF:\nt = [0.0, 0.0, 0.0] m\nR = [-90.0°, 0.0°, -90.0°]\nZ Maju, X Kanan, Y Bawah",
                  '#F0FDF4', '#15803D')

    draw_tf_frame(1030, 45, 240, 105, "ping1d_sonar_link", "Acoustic Sensor", "static_tf_publisher",
                  "Offset Transduser Sonar 115kHz:\nt = [+0.15, 0.00, -0.05] m\nKerucut Akustik FOV 30° ke Bawah",
                  '#F0FDFA', '#0D9488')

    draw_tf_frame(1355, 45, 250, 105, "bar30_depth_link", "Pressure Sensor", "static_tf_publisher",
                  "Offset Port Diafragma Bar30:\nt = [0.00, 0.00, -0.08] m\nDatum Tekanan Hidrostatis Dasar",
                  '#EFF6FF', '#2563EB')

    draw_tf_frame(1670, 110, 195, 120, "base_imu_link", "Inertial Frame", "static_tf_publisher",
                  "Pixhawk Internal IMU:\nt = [0.0, 0.0, 0.0] m\nOrientasi Sumbu Koinsiden\ndengan base_link",
                  '#FAF5FF', '#9333EA')

    # Panah percabangan dari base_link
    draw_arrow(940, 240, 1030, 240, color='#16A34A', style="->")
    draw_arrow(1270, 240, 1355, 240, color='#15803D', style="->")
    draw_arrow(850, 180, 1030, 98, color='#0D9488', style="->", rad=-0.1) # base ke ping1d
    draw_arrow(870, 180, 1355, 95, color='#2563EB', style="->", rad=-0.15) # base ke bar30
    draw_arrow(940, 210, 1670, 170, color='#9333EA', style="->", rad=0.1) # base ke IMU

    # Simpan output dengan resolusi 300 DPI
    out_path = r"c:\remote_ROV\gambar_ta\gambar_arsitektur_ros_nodegraph_tf.png"
    plt.savefig(out_path, dpi=300, facecolor='#FFFFFF', edgecolor='none')
    plt.close()
    print(f"[OK] Diagram publikasi jurnal berhasil digenerate di: {out_path}")

if __name__ == '__main__':
    create_diagram()
