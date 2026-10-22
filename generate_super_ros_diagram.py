#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_super_ros_diagram.py
=============================================================================
Menghasilkan Diagram Publikasi Ilmiah Standar IEEE Transactions / IROS / ICRA:
1. Resolusi Tinggi 300 DPI, Background Putih Murni (#FFFFFF), Zero-Overlap.
2. Panel (a): Distributed ROS Computational Architecture (Stage 1 s/d 4)
   - Bus routing ortogonal presisi melalui celah antar-node (bebas potong node).
   - Badge topik berbentuk kapsul dengan tipe pesan & laju transfer.
   - Komputasi komprehensif (DirectShow, MAVLink, CUDA FP16, C++, EKF, OctoMap).
3. Panel (b): Rantai Hierarki Transformasi Spasial TF2 & Skematik Fisik BlueROV2
   - Grid 5-kolom simetris sempurna dengan celah 90 px bebas tabrakan (Zero Text Overlap).
   - Skematik vektor bodi BlueROV2 dengan callout fisik sensor metrik rapi di dalam kartu.
   - 3D Coordinate Axis Gizmo (X=Merah, Y=Hijau, Z=Biru) pada area bebas di setiap frame.
   - Penjelasan visual dan matematis rotasi ortogonal R_align ke RDF.
   - Legenda formal standar jurnal internasional.
=============================================================================
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Polygon, Wedge

def draw_shadowed_card(ax, x, y, w, h, bg_color, border_color, radius=8, border_w=1.6):
    """Menggambar kartu dengan drop-shadow halus bergradasi untuk estetika modern."""
    shadow = FancyBboxPatch((x + 2.5, y - 2.5), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
                            facecolor='#000000', edgecolor='none', alpha=0.04, zorder=2)
    ax.add_patch(shadow)
    card = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
                          facecolor=bg_color, edgecolor=border_color, linewidth=border_w, zorder=3)
    ax.add_patch(card)
    return card

def draw_axis_gizmo(ax, cx, cy, scale=15, is_optical=False):
    """
    Menggambar 3D coordinate frame triad (X=Red, Y=Green, Z=Blue).
    Standar robotika: Merah = X, Hijau = Y, Biru = Z.
    """
    p_origin = (cx, cy)
    if not is_optical:
        # Standard ROS REP 103 ENU / Body: X forward (kiri-bawah), Y left (kanan), Z up (atas)
        # Z axis (Blue) -> Up
        ax.annotate('', xy=(cx, cy + scale*1.12), xytext=p_origin,
                    arrowprops=dict(arrowstyle="-|>", color="#2563EB", lw=1.8, mutation_scale=6), zorder=8)
        ax.text(cx, cy + scale*1.28, "Z", color="#2563EB", fontsize=6.8, fontweight='bold', ha='center', va='center', zorder=9)
        # Y axis (Green) -> Right (Left lateral in vehicle)
        ax.annotate('', xy=(cx + scale*0.95, cy + scale*0.1), xytext=p_origin,
                    arrowprops=dict(arrowstyle="-|>", color="#16A34A", lw=1.8, mutation_scale=6), zorder=8)
        ax.text(cx + scale*1.12, cy + scale*0.1, "Y", color="#16A34A", fontsize=6.8, fontweight='bold', ha='center', va='center', zorder=9)
        # X axis (Red) -> Left-down (Forward surge)
        ax.annotate('', xy=(cx - scale*0.75, cy - scale*0.55), xytext=p_origin,
                    arrowprops=dict(arrowstyle="-|>", color="#DC2626", lw=1.8, mutation_scale=6), zorder=8)
        ax.text(cx - scale*0.92, cy - scale*0.68, "X", color="#DC2626", fontsize=6.8, fontweight='bold', ha='center', va='center', zorder=9)
    else:
        # Pinhole Optical Frame RDF: X Right (kanan), Y Down (bawah), Z Forward/Depth (kanan-atas)
        # X axis (Red) -> Right
        ax.annotate('', xy=(cx + scale*1.0, cy), xytext=p_origin,
                    arrowprops=dict(arrowstyle="-|>", color="#DC2626", lw=1.8, mutation_scale=6), zorder=8)
        ax.text(cx + scale*1.18, cy, "X(R)", color="#DC2626", fontsize=6.5, fontweight='bold', ha='left', va='center', zorder=9)
        # Y axis (Green) -> Down
        ax.annotate('', xy=(cx, cy - scale*1.0), xytext=p_origin,
                    arrowprops=dict(arrowstyle="-|>", color="#16A34A", lw=1.8, mutation_scale=6), zorder=8)
        ax.text(cx, cy - scale*1.18, "Y(D)", color="#16A34A", fontsize=6.5, fontweight='bold', ha='center', va='top', zorder=9)
        # Z axis (Blue) -> Forward/Depth
        ax.annotate('', xy=(cx + scale*0.72, cy + scale*0.62), xytext=p_origin,
                    arrowprops=dict(arrowstyle="-|>", color="#2563EB", lw=1.8, mutation_scale=6), zorder=8)
        ax.text(cx + scale*0.88, cy + scale*0.76, "Z(F)", color="#2563EB", fontsize=6.5, fontweight='bold', ha='center', va='bottom', zorder=9)
        
    dot = Circle((cx, cy), radius=2.2, facecolor='#0F172A', edgecolor='none', zorder=10)
    ax.add_patch(dot)

def draw_tech_node(ax, x, y, w, h, node_name, pkg_tag, engine_tag, bullets, bg_col, bdr_col, hdr_col):
    """Menggambar node komputasi ROS berpenampilan sangat profesional dan modern."""
    draw_shadowed_card(ax, x, y, w, h, bg_col, bdr_col, radius=8, border_w=1.8)
    
    # Header bar
    hdr = FancyBboxPatch((x, y + h - 28), w, 28, boxstyle="round,pad=0,rounding_size=8",
                         facecolor=hdr_col, edgecolor=hdr_col, linewidth=0, zorder=4)
    ax.add_patch(hdr)
    fill_rect = patches.Rectangle((x, y + h - 28), w, 10, facecolor=hdr_col, edgecolor=hdr_col, linewidth=0, zorder=4)
    ax.add_patch(fill_rect)
    
    # Font size calculation based on string length
    n_font = 9.2 if len(node_name) > 20 else 10.2
    ax.text(x + 10, y + h - 14, node_name, ha='left', va='center',
            fontsize=n_font, fontweight='bold', color='#FFFFFF', fontfamily='DejaVu Sans', zorder=5)
    
    # Engine Badge
    eb_w = len(engine_tag) * 6.2 + 14
    eb = FancyBboxPatch((x + w - eb_w - 8, y + h - 22), eb_w, 16, boxstyle="round,pad=0,rounding_size=4",
                        facecolor='#FFFFFF', edgecolor='none', alpha=0.92, zorder=5)
    ax.add_patch(eb)
    ax.text(x + w - eb_w/2 - 8, y + h - 14, engine_tag, ha='center', va='center',
            fontsize=7, fontweight='bold', color=hdr_col, fontfamily='DejaVu Sans', zorder=6)
    
    # Package Subtitle
    ax.text(x + 10, y + h - 42, pkg_tag, ha='left', va='center',
            fontsize=8.2, fontweight='bold', color=bdr_col, fontfamily='DejaVu Sans', zorder=5)
    
    # Divider line
    ax.plot([x + 10, x + w - 10], [y + h - 51, y + h - 51], color=bdr_col, lw=0.75, alpha=0.35, zorder=5)
    
    # Bullets
    cur_y = y + h - 65
    for b in bullets:
        if b.startswith("•"):
            ax.text(x + 10, cur_y, b, ha='left', va='center',
                    fontsize=7.7, color='#0F172A', fontfamily='DejaVu Sans', zorder=5)
            cur_y -= 13.5
        elif b.startswith("  -"):
            ax.text(x + 18, cur_y, b, ha='left', va='center',
                    fontsize=7.2, color='#475569', fontfamily='DejaVu Sans', zorder=5)
            cur_y -= 12.0
        elif b == "":
            cur_y -= 3.5
        else:
            ax.text(x + 10, cur_y, b, ha='left', va='center',
                    fontsize=7.6, fontweight='bold', color='#1E293B', fontfamily='DejaVu Sans', zorder=5)
            cur_y -= 13.5

def draw_topic_pill(ax, x, y, w, h, topic_name, msg_type, rate=""):
    """Menggambar badge topik ROS format kapsul rapi."""
    draw_shadowed_card(ax, x, y, w, h, '#FFFFFF', '#64748B', radius=5, border_w=1.2)
    # Left colored accent line
    bar = FancyBboxPatch((x, y), 5, h, boxstyle="round,pad=0,rounding_size=2",
                         facecolor='#0284C7', edgecolor='#0284C7', linewidth=0, zorder=4)
    ax.add_patch(bar)
    
    ax.text(x + 10, y + h*0.65, topic_name, ha='left', va='center',
            fontsize=8.0, fontweight='bold', color='#0F172A', fontfamily='DejaVu Sans', zorder=5)
    
    sub_text = f"[{msg_type}]" if not rate else f"[{msg_type} • {rate}]"
    ax.text(x + 10, y + h*0.28, sub_text, ha='left', va='center',
            fontsize=6.8, color='#0369A1', fontfamily='DejaVu Sans', zorder=5)

def draw_smart_arrow(ax, pts, color='#334155', lw=1.5, style="-|>", rad=0.0):
    """Menggambar panah berbelok halus ortogonal / segmented."""
    for i in range(len(pts) - 1):
        p1 = pts[i]
        p2 = pts[i+1]
        is_last = (i == len(pts) - 2)
        arrow_style = style if is_last else "-"
        arr = FancyArrowPatch(p1, p2, connectionstyle=f"arc3,rad={rad}",
                              arrowstyle=arrow_style, mutation_scale=9,
                              color=color, linewidth=lw, zorder=2)
        ax.add_patch(arr)

def draw_subsea_rov_silhouette(ax, cx, cy, scale=1.0):
    """Menggambar siluet visual BlueROV2 dengan callout fisik sensor yang 100% rapi di dalam batas kartu."""
    # Main Tube Chassis (Dark Blue / Slate)
    hull = FancyBboxPatch((cx - 65*scale, cy - 22*scale), 130*scale, 44*scale,
                          boxstyle="round,pad=0,rounding_size=12",
                          facecolor='#1E293B', edgecolor='#0EA5E9', linewidth=2.0*scale, zorder=5)
    ax.add_patch(hull)
    
    # Internal Electronics Enclosure Tube (Transparent Cyan Ring)
    inner_tube = FancyBboxPatch((cx - 55*scale, cy - 15*scale), 110*scale, 30*scale,
                               boxstyle="round,pad=0,rounding_size=8",
                               facecolor='#0F172A', edgecolor='#38BDF8', linewidth=1.0*scale, linestyle=':', zorder=6)
    ax.add_patch(inner_tube)
    
    # Front Acrylic Dome Lens (Camera)
    dome = Wedge((cx + 65*scale, cy), 18*scale, -90, 90,
                 facecolor='#38BDF8', edgecolor='#0284C7', linewidth=1.6*scale, alpha=0.85, zorder=7)
    ax.add_patch(dome)
    # Camera lens inside dome
    lens = Circle((cx + 67*scale, cy), radius=6.0*scale, facecolor='#0284C7', edgecolor='#E0F2FE', linewidth=1.2*scale, zorder=8)
    ax.add_patch(lens)
    
    # Leader line to Front Camera Dome (stays inside card bounds, going up-right within bounds)
    ax.plot([cx + 70*scale, cx + 55*scale], [cy + 12*scale, cy + 48*scale], color='#0284C7', lw=1.2*scale, zorder=8)
    ax.text(cx + 55*scale, cy + 54*scale, "Front Camera Dome\nt=[+0.18, 0, +0.05] m", color='#0284C7',
            fontsize=6.2*scale, fontweight='bold', ha='center', va='bottom', zorder=9)
    
    # Buoyancy Foam Block (Yellow top fairing)
    foam = FancyBboxPatch((cx - 55*scale, cy + 20*scale), 110*scale, 16*scale,
                          boxstyle="round,pad=0,rounding_size=6",
                          facecolor='#EAB308', edgecolor='#CA8A04', linewidth=1.5*scale, zorder=6)
    ax.add_patch(foam)
    ax.text(cx, cy + 28*scale, "BlueROV2 Heavy Chassis", color='#713F12',
            fontsize=6.2*scale, fontweight='bold', ha='center', va='center', zorder=7)
    
    # Thruster Ducts (Left & Right)
    t1 = FancyBboxPatch((cx - 78*scale, cy + 4*scale), 14*scale, 22*scale, boxstyle="round,pad=0,rounding_size=3",
                         facecolor='#475569', edgecolor='#334155', linewidth=1*scale, zorder=4)
    t2 = FancyBboxPatch((cx - 78*scale, cy - 26*scale), 14*scale, 22*scale, boxstyle="round,pad=0,rounding_size=3",
                         facecolor='#475569', edgecolor='#334155', linewidth=1*scale, zorder=4)
    ax.add_patch(t1)
    ax.add_patch(t2)
    
    # Sonar Transducer (Bottom front)
    sonar = FancyBboxPatch((cx + 25*scale, cy - 32*scale), 16*scale, 12*scale, boxstyle="round,pad=0,rounding_size=3",
                           facecolor='#0D9488', edgecolor='#042F2E', linewidth=1.4*scale, zorder=6)
    ax.add_patch(sonar)
    # Acoustic beam cone (translucent cyan)
    beam = Polygon([[cx + 28*scale, cy - 32*scale], [cx + 39*scale, cy - 32*scale],
                    [cx + 54*scale, cy - 60*scale], [cx + 13*scale, cy - 60*scale]],
                   closed=True, facecolor='#14B8A6', edgecolor='#0D9488', alpha=0.35, linestyle='--', linewidth=1*scale, zorder=4)
    ax.add_patch(beam)
    # Leader line to Sonar
    ax.plot([cx + 33*scale, cx + 55*scale], [cy - 38*scale, cy - 62*scale], color='#0D9488', lw=1.2*scale, zorder=8)
    ax.text(cx + 58*scale, cy - 62*scale, "Ping1D Sonar (115 kHz)\nt=[+0.15, 0, -0.05] m", color='#0D9488',
            fontsize=6.2*scale, fontweight='bold', ha='left', va='center', zorder=9)

    # Bar30 Pressure Sensor (Bottom center)
    bar30 = Circle((cx - 15*scale, cy - 25*scale), radius=4.5*scale, facecolor='#2563EB', edgecolor='#1E3A8A', linewidth=1.4*scale, zorder=7)
    ax.add_patch(bar30)
    # Leader line to Bar30
    ax.plot([cx - 15*scale, cx - 40*scale], [cy - 27*scale, cy - 62*scale], color='#2563EB', lw=1.2*scale, zorder=8)
    ax.text(cx - 43*scale, cy - 62*scale, "Bar30 Depth Sensor\nt=[0, 0, -0.08] m", color='#2563EB',
            fontsize=6.2*scale, fontweight='bold', ha='right', va='center', zorder=9)

    # Base_link Center of Gravity (CoG) & Pixhawk IMU
    cog = Circle((cx, cy), radius=4.0*scale, facecolor='#EF4444', edgecolor='#B91C1C', linewidth=1.6*scale, zorder=9)
    ax.add_patch(cog)
    ax.text(cx, cy - 9*scale, "base_link / Pixhawk IMU\n(CoG t=[0,0,0])", color='#DC2626',
            fontsize=6.0*scale, fontweight='bold', ha='center', zorder=10)

def generate_diagram():
    fig = plt.figure(figsize=(24.0, 13.5), dpi=300, facecolor='#FFFFFF')
    ax = fig.add_axes([0, 0, 1, 1], facecolor='#FFFFFF')
    ax.set_xlim(0, 2400)
    ax.set_ylim(0, 1350)
    ax.axis('off')

    # Color Palette Tokens
    C_TEXT_MAIN = '#0F172A'    # Slate 900
    C_TEXT_MUTED = '#475569'   # Slate 600

    # -------------------------------------------------------------------------
    # MAIN HEADER & TITLE
    # -------------------------------------------------------------------------
    ax.text(1200, 1318, "ARSITEKTUR GRAF KOMPUTASI ROS & RANTAI TRANSFORMASI SPASIAL TF2",
            ha='center', va='center', fontsize=20, fontweight='bold', color=C_TEXT_MAIN,
            fontfamily='DejaVu Sans')
    ax.text(1200, 1290, "Sistem Fusi Dense Neural-SLAM: Integrasi Pelacakan 6-DoF ORB-SLAM3, Estimasi Kedalaman AI MiDaS, dan RTAB-Map pada BlueROV2",
            ha='center', va='center', fontsize=12, fontstyle='italic', color=C_TEXT_MUTED,
            fontfamily='DejaVu Sans')
    
    # Publication Meta Tag Badge
    meta_tag = FancyBboxPatch((2080, 1285), 260, 32, boxstyle="round,pad=0,rounding_size=6",
                              facecolor='#F1F5F9', edgecolor='#94A3B8', linewidth=1.2, zorder=3)
    ax.add_patch(meta_tag)
    ax.text(2210, 1301, "IEEE Standard Format • 300 DPI", ha='center', va='center',
            fontsize=8.5, fontweight='bold', color='#334155', fontfamily='DejaVu Sans', zorder=4)

    # -------------------------------------------------------------------------
    # PANEL (a): ROS COMPUTATIONAL NODE GRAPH (Top 65%)
    # -------------------------------------------------------------------------
    panel_a = FancyBboxPatch((40, 480), 2320, 785, boxstyle="round,pad=0,rounding_size=12",
                             facecolor='#FFFFFF', edgecolor='#64748B', linewidth=1.6, zorder=1)
    ax.add_patch(panel_a)

    ax.text(65, 1238, "(a) Graf Komputasi ROS 1 (Asynchronous Multi-Threaded Node Pipeline & Topic Data Flow)",
            ha='left', va='center', fontsize=14, fontweight='bold', color='#0F172A',
            fontfamily='DejaVu Sans', zorder=2)

    # 4 Column Stage Shading Panels
    stages = [
        ("STAGE 1: HARDWARE BRIDGES & SENSORS", 60, 540, "#F8FAFC", "#2563EB"),
        ("STAGE 2: PRE-PROCESSING & AI DEPTH", 625, 545, "#F8FAFC", "#0D9488"),
        ("STAGE 3: 6-DoF TRACKING & FUSION", 1195, 540, "#F8FAFC", "#7C3AED"),
        ("STAGE 4: 3D SLAM & DIGITAL TWIN", 1760, 580, "#F8FAFC", "#DB2777")
    ]

    for title, sx, sw, sbg, scol in stages:
        s_rect = FancyBboxPatch((sx, 500), sw, 715, boxstyle="round,pad=0,rounding_size=8",
                                facecolor=sbg, edgecolor='#CBD5E1', linewidth=1.2, zorder=1)
        ax.add_patch(s_rect)
        hdr_bar = FancyBboxPatch((sx, 1185), sw, 26, boxstyle="round,pad=0,rounding_size=6",
                                facecolor='#FFFFFF', edgecolor=scol, linewidth=1.4, zorder=2)
        ax.add_patch(hdr_bar)
        ax.text(sx + sw/2, 1198, title, ha='center', va='center',
                fontsize=9.5, fontweight='bold', color=scol, fontfamily='DejaVu Sans', zorder=3)

    # Category Colors
    C_BLUE_BG = '#EFF6FF'; C_BLUE_BDR = '#3B82F6'; C_BLUE_HDR = '#1D4ED8'
    C_TEAL_BG = '#F0FDFA'; C_TEAL_BDR = '#14B8A6'; C_TEAL_HDR = '#0F766E'
    C_PURP_BG = '#FAF5FF'; C_PURP_BDR = '#A855F7'; C_PURP_HDR = '#7E22CE'
    C_ROSE_BG = '#FFF1F2'; C_ROSE_BDR = '#F43F5E'; C_ROSE_HDR = '#BE123C'
    C_GREEN_BG = '#F0FDF4'; C_GREEN_BDR = '#22C55E'; C_GREEN_HDR = '#15803D'

    # -------------------------------------------------------------------------
    # STAGE 1 NODES & TOPICS
    # -------------------------------------------------------------------------
    draw_tech_node(ax, 75, 1010, 325, 155, "/mjpeg_webcam_bridge", "subsea_3d_mapping (Node)", "DShow / HTTP",
                   ["• Akuisisi Sensor CMOS USB 1/2.7\"",
                    "• DirectShow Buffer Size = 1",
                    "• Latensi Akuisisi < 80 ms (Realtime)",
                    "• HTTP MJPEG Streaming Server: 8088",
                    "• Rate Publikasi: 30.0 FPS Kontinu"],
                   C_BLUE_BG, C_BLUE_BDR, C_BLUE_HDR)

    draw_tech_node(ax, 75, 800, 325, 175, "/blueos_live_bridge", "subsea_3d_mapping (Node)", "REST MAVLink",
                   ["• Polling Endpoint HTTP Port 80 @ 192.168.2.2",
                    "• MAVLink Parsing Frekuensi 30 Hz:",
                    "  - ATTITUDE: Roll, Pitch, Yaw",
                    "  - RAW_IMU: Ax, Ay, Az, Gx, Gy, Gz",
                    "  - VFR_HUD: Heading & Baro Alt",
                    "• Deadband Stabilizer (<0.85° noise cutoff)"],
                   C_BLUE_BG, C_BLUE_BDR, C_BLUE_HDR)

    draw_tech_node(ax, 75, 525, 325, 240, "/depth_to_pose_publisher", "subsea_3d_mapping (Node)", "Dual Bridge",
                   ["• Dual Redundant Depth Architecture:",
                    "  1. Fallback MAVROS: /mavros/altitude",
                    "  2. Direct Bar30 I2C Driver:",
                    "     - Presisi Metrik: ±2 mm air laut",
                    "     - Covariance: 1e-4 m² (High Trust)",
                    "• Ping1D 115 kHz Altimeter Sonar:",
                    "  - 5-Sample Rolling Median Window",
                    "  - Outlier Reject (> 10 m / Low Confidence)",
                    "• Konversi Koordinat ke ROS REP 103 (Z -)"],
                   C_BLUE_BG, C_BLUE_BDR, C_BLUE_HDR)

    # Topic Pills Stage 1
    draw_topic_pill(ax, 415, 1070, 175, 42, "/camera/image_raw", "sensor_msgs/Image", "30 Hz")
    draw_topic_pill(ax, 415, 865, 175, 42, "/mavros/imu/data", "sensor_msgs/Imu", "30 Hz")
    draw_topic_pill(ax, 415, 675, 175, 42, "/bar30/pose_depth", "PoseWithCovariance", "10 Hz")
    draw_topic_pill(ax, 415, 570, 175, 42, "/sonar/ping1d/range", "sensor_msgs/Range", "10 Hz")

    draw_smart_arrow(ax, [(400, 1091), (415, 1091)])
    draw_smart_arrow(ax, [(400, 886), (415, 886)])
    draw_smart_arrow(ax, [(400, 696), (415, 696)])
    draw_smart_arrow(ax, [(400, 591), (415, 591)])

    # -------------------------------------------------------------------------
    # STAGE 2 NODES & TOPICS
    # -------------------------------------------------------------------------
    draw_tech_node(ax, 640, 1005, 320, 160, "/underwater_clahe", "subsea_3d_mapping (Node)", "OpenCV 4",
                   ["• Arsitektur SVIn2 (IEEE IROS Standard)",
                    "• Konversi Warna BGR ke Ruang LAB",
                    "• CLAHE pada Kanal Luminansi (L):",
                    "  - Clip Limit = 2.5, Tile Grid = 8x8",
                    "• Restorasi Redudansi Backscatter & Debu Air",
                    "• Output Kontras Tinggi untuk ORB Extractor"],
                   C_TEAL_BG, C_TEAL_BDR, C_TEAL_HDR)

    draw_tech_node(ax, 640, 525, 320, 445, "/monocular_depth_ai", "subsea_3d_mapping (Node)", "CUDA FP16",
                   ["• Dense Neural Depth Inference (MiDaS DPT)",
                    "• Tensor Input Resizing: 256 x 256 ImageNet",
                    "• Normalisasi Disparitas Relatif d_norm ∈ [0, 1]:",
                    "  - Percentile Outlier Clamping [2%, 98%]",
                    "• Formulasi Kalibrasi Kedalaman Hiperbolik:",
                    "  Z(d) = 1.0 / (2.6349 · d_norm + 0.2222)",
                    "  Rentang Inspeksi: [0.35 m s/d 4.50 m]",
                    "• Penguncian Skala Akustik Realtime:",
                    "  - Sampling Tengah 10% Disparitas ROI",
                    "  - Scale Factor λ* terhadap Ping1D Range",
                    "• Inner Boundary Masking (5% Margin Bebas Flare)",
                    "• Exponential Moving Average (EMA) Temporal:",
                    "  C_t = 0.65 · C_{t-1} + 0.35 · C_frame",
                    "• Exact Time-Synchronized PointCloud Generator"],
                   C_TEAL_BG, C_TEAL_BDR, C_TEAL_HDR)

    draw_smart_arrow(ax, [(590, 1091), (640, 1091)]) # /camera/image_raw -> CLAHE
    draw_smart_arrow(ax, [(590, 1091), (615, 1091), (615, 910), (640, 910)]) # /camera/image_raw -> Depth AI
    draw_smart_arrow(ax, [(590, 591), (615, 591), (615, 620), (640, 620)]) # Sonar -> Depth AI

    # Topic Pills Stage 2
    draw_topic_pill(ax, 975, 1065, 185, 42, "/camera/image_enhanced", "sensor_msgs/Image", "30 Hz")
    draw_topic_pill(ax, 975, 875, 185, 42, "/camera/synced/image", "sensor_msgs/Image", "20 Hz")
    draw_topic_pill(ax, 975, 805, 185, 42, "/camera/synced/depth", "Image 32FC1 (m)", "20 Hz")
    draw_topic_pill(ax, 975, 735, 185, 42, "/camera/synced/camera_info", "CameraInfo", "20 Hz")
    draw_topic_pill(ax, 975, 560, 185, 42, "/camera/depth/points", "PointCloud2", "20 Hz")

    draw_smart_arrow(ax, [(960, 1086), (975, 1086)])
    draw_smart_arrow(ax, [(960, 896), (975, 896)])
    draw_smart_arrow(ax, [(960, 826), (975, 826)])
    draw_smart_arrow(ax, [(960, 756), (975, 756)])
    draw_smart_arrow(ax, [(960, 581), (975, 581)])

    # -------------------------------------------------------------------------
    # STAGE 3 NODES & TOPICS
    # -------------------------------------------------------------------------
    draw_tech_node(ax, 1210, 890, 330, 275, "/orb_slam3_odom", "ORB-SLAM3 Monocular", "C++ Native",
                   ["• Ekstraksi Cepat Fitur FAST & ORB 256-bit",
                    "• Tightly-Coupled Bundle Adjustment (BA)",
                    "• Manifold SO(3) Lie Algebra Tracking",
                    "• Estimasi State Pose SE(3): T_w,c (30 Hz)",
                    "• Matriks Penyelarasan Koordinat Ortogonal:",
                    "  R_align: RDF Optis -> ROS REP 103 ENU",
                    "  R_align = [[0, 0, 1], [-1, 0, 0], [0, -1, 0]]",
                    "• Wireframe Camera Frustum Publisher:",
                    "  - Merah: Pose Kamera Realtime",
                    "  - Biru: Riwayat KeyFrames",
                    "  - Hijau: Covisibility Graph Edge"],
                   C_GREEN_BG, C_GREEN_BDR, C_GREEN_HDR)

    draw_tech_node(ax, 1210, 525, 330, 310, "/ekf_localization", "robot_localization (Node)", "EKF 30 Hz",
                   ["• Extended Kalman Filter 15-State Fusion:",
                    "  [x, y, z, roll, pitch, yaw, vx, vy, vz, wx, wy, wz, ax, ay, az]",
                    "• Sensor Measurement Inputs:",
                    "  1. IMU (Roll, Pitch, Angular Vel)",
                    "  2. Bar30 Abs Z (Mahalanobis Gating 2σ)",
                    "  3. Visual Odometry (X, Y, Z, Yaw)",
                    "• Asynchronous Multi-Rate Propagation",
                    "• Covariance Smoothing & Jump Rejection",
                    "• Broadcaster Transformasi TF Kontinu:",
                    "  odom -> base_link (Zero Jitter)"],
                   C_PURP_BG, C_PURP_BDR, C_PURP_HDR)

    draw_smart_arrow(ax, [(1160, 1086), (1210, 1086)]) # Enhanced image -> ORB-SLAM3
    # IMU to EKF
    draw_smart_arrow(ax, [(590, 886), (615, 886), (615, 510), (1180, 510), (1180, 730), (1210, 730)])
    # Bar30 to EKF
    draw_smart_arrow(ax, [(590, 696), (608, 696), (608, 495), (1190, 495), (1190, 660), (1210, 660)])

    # Topic Pills Stage 3
    draw_topic_pill(ax, 1560, 1065, 170, 42, "/rtabmap/odom", "nav_msgs/Odometry", "30 Hz")
    draw_topic_pill(ax, 1560, 955, 170, 42, "/orb_slam3/sparse_points", "PointCloud2 (RGB)", "10 Hz")
    draw_topic_pill(ax, 1560, 660, 170, 42, "/odometry/filtered", "nav_msgs/Odometry", "30 Hz")

    draw_smart_arrow(ax, [(1540, 1086), (1560, 1086)])
    draw_smart_arrow(ax, [(1540, 976), (1560, 976)])
    draw_smart_arrow(ax, [(1540, 681), (1560, 681)])

    # ORB-SLAM3 Odom to EKF
    draw_smart_arrow(ax, [(1540, 1086), (1552, 1086), (1552, 850), (1198, 850), (1198, 780), (1210, 780)])

    # -------------------------------------------------------------------------
    # STAGE 4 NODES & TOPICS
    # -------------------------------------------------------------------------
    draw_tech_node(ax, 1775, 875, 335, 290, "/rtabmap_slam", "rtabmap_slam (C++ Node)", "Loop Closure",
                   ["• Dense RGB-D SLAM & Multi-Session Memory",
                    "• 3-Stage Underwater PointCloud Filter:",
                    "  1. PassThrough Z-Clipping [0.35m - 4.50m]",
                    "  2. Statistical Outlier Removal (SOR, k=30, σ=1.0)",
                    "  3. OctoMap Voxel Grid (Cell: 0.05 m)",
                    "• Loop Closure Detection via DBoW2 / ORB Vocab",
                    "• Graph Optimization: g2o Global Bundle Adjustment",
                    "• Broadcaster Transformasi TF Global:",
                    "  map -> odom (Drift Correction)",
                    "• Model 3D Metrik Export: .PLY & .OBJ Mesh"],
                   C_PURP_BG, C_PURP_BDR, C_PURP_HDR)

    draw_tech_node(ax, 1775, 680, 335, 175, "/egoexo_ground_surface", "subsea_3d_mapping (Node)", "EgoExo++ Paper",
                   ["• Estimasi Permukaan Dasar Laut 2.5D",
                    "• Datum Bidang Bawah ROV Dinamis:",
                    "  Z_ground = min(Z_trajectory) - 0.12 m",
                    "• Visualisasi Planar Hex Soft Teal (#5B8C9B, α=0.85)",
                    "• Lintasan Jalur Kuning (#FFE600, +1.5 cm offset)",
                    "• Datum Keselamatan Anti-Collision Pilot ROV"],
                   C_ROSE_BG, C_ROSE_BDR, C_ROSE_HDR)

    draw_tech_node(ax, 1775, 525, 335, 135, "/rov_trajectory_tracker", "subsea_3d_mapping (Node)", "Path Tracker",
                   ["• Pelacak Lintasan 3D Realtime (/robot_path)",
                    "• Anti-Teleport Spike Filter (Lompatan > 0.4 m ditolak)",
                    "• Representasi Model Bodi Kubus BlueROV2",
                    "• Komputasi Jarak Tempuh Kumulatif (Odometer Metrik)"],
                   C_ROSE_BG, C_ROSE_BDR, C_ROSE_HDR)

    # Connections to Stage 4
    draw_smart_arrow(ax, [(1730, 1086), (1775, 1086)]) # Odom -> RTAB-Map

    # BUS ROUTING MELALUI CELAH BERSIH (Y: 845 s/d 875) ANTARA ORB-SLAM3 (Y>=890) & EKF (Y<=835)
    draw_smart_arrow(ax, [(1160, 896), (1172, 896), (1172, 875), (1745, 875), (1745, 1030), (1775, 1030)]) # image
    draw_smart_arrow(ax, [(1160, 826), (1178, 826), (1178, 860), (1752, 860), (1752, 990), (1775, 990)]) # depth
    draw_smart_arrow(ax, [(1160, 756), (1184, 756), (1184, 845), (1758, 845), (1758, 950), (1775, 950)]) # camera_info

    # EKF Filtered to Trajectory tracker
    draw_smart_arrow(ax, [(1730, 681), (1752, 681), (1752, 592), (1775, 592)])

    # Output topics from Stage 4
    draw_topic_pill(ax, 2130, 1065, 195, 42, "/rtabmap/octomap_grid", "octomap_msgs/Octomap", "1 Hz")
    draw_topic_pill(ax, 2130, 985, 195, 42, "/rtabmap/cloud_map", "sensor_msgs/PointCloud2", "1 Hz")
    draw_topic_pill(ax, 2130, 750, 195, 42, "/egoexo/ground_plane", "Marker (Soft Teal)", "10 Hz")
    draw_topic_pill(ax, 2130, 570, 195, 42, "/robot_path", "nav_msgs/Path", "10 Hz")

    draw_smart_arrow(ax, [(2110, 1086), (2130, 1086)])
    draw_smart_arrow(ax, [(2110, 1006), (2130, 1006)])
    draw_smart_arrow(ax, [(2110, 771), (2130, 771)])
    draw_smart_arrow(ax, [(2110, 592), (2130, 592)])
    draw_smart_arrow(ax, [(2130, 592), (2120, 592), (2120, 720), (2110, 720)], style="<-")


    # -------------------------------------------------------------------------
    # PANEL (b): HIERARCHICAL TF2 TRANSFORM TREE & VEHICLE INTEGRATION (Bottom 35%)
    # -------------------------------------------------------------------------
    panel_b = FancyBboxPatch((40, 25), 2320, 435, boxstyle="round,pad=0,rounding_size=12",
                             facecolor='#FFFFFF', edgecolor='#64748B', linewidth=1.6, zorder=1)
    ax.add_patch(panel_b)

    ax.text(65, 435, "(b) Rantai Hierarki Transformasi Koordinat Spasial TF2 Tree & Penempatan Sensor Fisik BlueROV2",
            ha='left', va='center', fontsize=14, fontweight='bold', color='#0F172A',
            fontfamily='DejaVu Sans', zorder=2)

    # Sub-box: BlueROV2 Physical Schematic (Left side, x=60 to 455)
    draw_shadowed_card(ax, 60, 45, 395, 375, '#F8FAFC', '#94A3B8', radius=8, border_w=1.2)
    ax.text(257, 395, "SKEMATIK FISIK SENSOR ROV", ha='center', va='center',
            fontsize=10.5, fontweight='bold', color='#1E293B', fontfamily='DejaVu Sans', zorder=4)
    ax.text(257, 378, "Dimensi Bodi BlueROV2: 457 x 338 x 254 mm (Massa: 11 kg)", ha='center', va='center',
            fontsize=7.6, fontstyle='italic', color='#64748B', fontfamily='DejaVu Sans', zorder=4)

    # Draw ROV Silhouette
    draw_subsea_rov_silhouette(ax, 240, 230, scale=1.18)

    # Helper function for TF Frame Cards in Panel B with clean separate Axis Box
    def draw_tf_card(x, y, w, h, frame_name, frame_role, bcast_node, specs, bg_c, bdr_c, is_optical=False):
        draw_shadowed_card(ax, x, y, w, h, bg_c, bdr_c, radius=8, border_w=1.6)
        
        # Frame Title
        fn_size = 8.8 if len(frame_name) > 16 else 10.5
        ax.text(x + 10, y + h - 18, frame_name, ha='left', va='center',
                fontsize=fn_size, fontweight='bold', color='#0F172A', fontfamily='DejaVu Sans', zorder=5)
        
        # Role Pill (width adaptive & compact)
        rw = len(frame_role) * 5.6 + 10
        rp = FancyBboxPatch((x + w - rw - 8, y + h - 26), rw, 17, boxstyle="round,pad=0,rounding_size=4",
                            facecolor='#FFFFFF', edgecolor=bdr_c, linewidth=1, zorder=5)
        ax.add_patch(rp)
        ax.text(x + w - rw/2 - 8, y + h - 17, frame_role, ha='center', va='center',
                fontsize=7.0, fontweight='bold', color=bdr_c, fontfamily='DejaVu Sans', zorder=6)
        
        # Broadcaster
        ax.text(x + 12, y + h - 38, f"Broadcaster: {bcast_node}", ha='left', va='center',
                fontsize=7.6, color='#475569', fontfamily='DejaVu Sans', zorder=5)
        
        # Divider line
        ax.plot([x + 10, x + w - 10], [y + h - 48, y + h - 48], color=bdr_c, lw=0.75, alpha=0.35, zorder=5)
        
        # Specs (text left-aligned, width room for axis gizmo)
        cy = y + h - 63
        for s in specs:
            ax.text(x + 12, cy, s, ha='left', va='center',
                    fontsize=7.1, color='#1E293B', fontfamily='DejaVu Sans', zorder=5)
            cy -= 13.0
            
        # Draw 3D axis gizmo in dedicated bottom-right area
        draw_axis_gizmo(ax, x + w - 24, y + 32, scale=14, is_optical=is_optical)

    # -------------------------------------------------------------------------
    # TF TREE 5-COLUMN PERFECT GRID (WITH 90 PX CLEAN CLEARANCE BETWEEN COLUMNS)
    # Col 1: x=485, w=245 (ends 730) -> Gap 90px
    # Col 2: x=820, w=245 (ends 1065) -> Gap 90px
    # Col 3: x=1155, w=255 (ends 1410) -> Gap 90px
    # Col 4: x=1500, w=255 (ends 1755) -> Gap 90px
    # Col 5: x=1845, w=495 (ends 2340)
    # -------------------------------------------------------------------------
    
    # Col 1 Top: map
    draw_tf_card(485, 235, 245, 165, "map", "Global Origin", "/rtabmap_slam",
                 ["• Datum Peta Inersia Global 3D",
                  "• Standar ROS REP 103 ENU:",
                  "  X-Maju, Y-Kiri, Z-Atas",
                  "• Asal (0,0,0) Awal Misi ROV",
                  "• Koordinat Absolut Digital Twin"],
                 '#EFF6FF', '#3B82F6')

    # Col 1 Bottom: LEGENDA SIMBOL
    leg_box = FancyBboxPatch((485, 45), 245, 175, boxstyle="round,pad=0,rounding_size=8",
                             facecolor='#F8FAFC', edgecolor='#94A3B8', linewidth=1.2, zorder=3)
    ax.add_patch(leg_box)
    ax.text(607, 202, "LEGENDA & KONVENSI DIAGRAM", ha='center', va='center',
            fontsize=8.3, fontweight='bold', color='#0F172A', fontfamily='DejaVu Sans', zorder=4)
    ax.plot([495, 720], [192, 192], color='#CBD5E1', lw=0.75, zorder=4)

    # Legend items
    draw_smart_arrow(ax, [(495, 175), (530, 175)], color='#334155', lw=1.5)
    ax.text(540, 175, "Aliran Topik ROS (Data Stream)", ha='left', va='center', fontsize=7.0, color='#1E293B', zorder=4)

    draw_smart_arrow(ax, [(495, 150), (530, 150)], color='#7C3AED', lw=1.8)
    ax.text(540, 150, "Transformasi Koordinat TF2 Tree", ha='left', va='center', fontsize=7.0, color='#1E293B', zorder=4)

    # Triad line
    ax.plot([495, 508], [125, 125], color='#DC2626', lw=2)
    ax.plot([511, 524], [125, 125], color='#16A34A', lw=2)
    ax.plot([527, 540], [125, 125], color='#2563EB', lw=2)
    ax.text(548, 125, "Sumbu 3D (X: Merah, Y: Hijau, Z: Biru)", ha='left', va='center', fontsize=6.8, color='#1E293B', zorder=4)

    ax.text(495, 98, "λ* Penguncian Skala Akustik Metrik", ha='left', va='center', fontsize=7.0, fontweight='bold', color='#0D9488', zorder=4)
    ax.text(495, 78, "R_align Penyelarasan RDF ke ENU", ha='left', va='center', fontsize=7.0, fontweight='bold', color='#15803D', zorder=4)
    ax.text(495, 58, "Format Dokumen Resmi: Polman Bandung", ha='left', va='center', fontsize=6.8, fontstyle='italic', color='#64748B', zorder=4)

    # Col 2 Top: odom
    draw_tf_card(820, 235, 245, 165, "odom", "Odometry Frame", "/ekf_localization",
                 ["• Kerangka Referensi Kontinu",
                  "• Menerima Koreksi Loop Closure",
                  "• Menghilangkan Drift Inersia",
                  "• Estimasi Odometri (30 Hz)",
                  "• Bebas Lonjakan Spasial"],
                 '#FAF5FF', '#8B5CF6')

    # Col 2 Bottom: Summary Card (Status Fusi Multi-Sensor)
    draw_shadowed_card(ax, 820, 45, 245, 175, '#F8FAFC', '#A855F7', radius=8, border_w=1.2)
    ax.text(942, 202, "ESTIMASI STATE MULTI-SENSOR", ha='center', va='center',
            fontsize=8.3, fontweight='bold', color='#6B21A8', fontfamily='DejaVu Sans', zorder=4)
    ax.plot([830, 1055], [192, 192], color='#E9D5FF', lw=0.75, zorder=4)
    ax.text(830, 175, "• Frekuensi Update: 30 Hz Sinkron", ha='left', va='center', fontsize=7.0, color='#1E293B', zorder=4)
    ax.text(830, 155, "• State Vektor: 15 Derajat Kebebasan", ha='left', va='center', fontsize=7.0, color='#1E293B', zorder=4)
    ax.text(830, 135, "• Mahalanobis Threshold: 2σ Gating", ha='left', va='center', fontsize=7.0, color='#1E293B', zorder=4)
    ax.text(830, 115, "• Z Error: ±0.002 m (Sensor Bar30)", ha='left', va='center', fontsize=7.0, color='#1E293B', zorder=4)
    ax.text(830, 95, "• Attitude Error: < 0.85° (IMU Pixhawk)", ha='left', va='center', fontsize=7.0, color='#1E293B', zorder=4)
    ax.text(830, 75, "• Drift Koreksi: Zero Cumulative", ha='left', va='center', fontsize=7.0, fontweight='bold', color='#7E22CE', zorder=4)

    # Col 3 Top: base_link
    draw_tf_card(1155, 235, 255, 165, "base_link", "Body Center", "/ekf_localization",
                 ["• Titik Pusat Massa Fisik (CoG)",
                  "• Sumbu Utama Seluruh Sensor",
                  "• Translasi t = [X, Y, Z_bar30]",
                  "• Rotasi R = [Roll, Pitch, Yaw_vo]",
                  "• Acuan Gerak Navigasi ROV"],
                 '#FEF2F2', '#EF4444')

    # Col 3 Bottom: base_imu_link (Co-located with base_link)
    draw_tf_card(1155, 45, 255, 175, "base_imu_link", "Inertial Frame", "static_tf_publisher",
                 ["• Sensor Internal Pixhawk Autopilot:",
                  "  t = [0.0, 0.0, 0.0] m (Co-located CoG)",
                  "  R = [0.0°, 0.0°, 0.0°] (Koinsiden)",
                  "• Kecepatan Sudut 3-Sumbu (Gyro)",
                  "• Akselerasi Linier 3-Sumbu (Ax,Ay,Az)",
                  "• Kompensasi Gravitasi g = 9.806 m/s²"],
                 '#FAF5FF', '#9333EA')

    # Kinematic Chain Connections (map -> odom -> base_link) with text ABOVE arrows in 90 px gaps
    draw_smart_arrow(ax, [(730, 317), (820, 317)], color='#2563EB', lw=2.0)
    ax.text(775, 335, "T_map_odom\n(Loop Closure)", ha='center', va='bottom',
            fontsize=7.2, fontweight='bold', color='#2563EB', fontfamily='DejaVu Sans')

    draw_smart_arrow(ax, [(1065, 317), (1155, 317)], color='#7C3AED', lw=2.0)
    ax.text(1110, 335, "T_odom_base\n(Fused EKF 30Hz)", ha='center', va='bottom',
            fontsize=7.2, fontweight='bold', color='#7C3AED', fontfamily='DejaVu Sans')

    # Vertical branch from base_link to base_imu_link
    draw_smart_arrow(ax, [(1282, 235), (1282, 220)], color='#9333EA', lw=1.8)
    ax.text(1290, 227, "t=[0,0,0], R=I", ha='left', va='center', fontsize=6.8, fontweight='bold', color='#9333EA', fontfamily='DejaVu Sans')

    # Col 4 Top: camera_link
    draw_tf_card(1500, 235, 255, 165, "camera_link", "Front Sensor", "static_tf_publisher",
                 ["• Posisi Kamera Depan BlueROV2:",
                  "  t = [+0.18, 0.00, +0.05] m",
                  "  (18cm Depan, 0cm Samping, 5cm Atas)",
                  "  R = [0.0°, 0.0°, 0.0°] (Sejajar Body)",
                  "• Sumbu Robotika (X Maju, Z Atas)"],
                 '#F0FDF4', '#16A34A')

    # Col 4 Bottom: ping1d_sonar_link
    draw_tf_card(1500, 45, 255, 175, "ping1d_sonar_link", "Sonar Altimeter", "static_tf_publisher",
                 ["• Transduser Akustik 115 kHz Sonar:",
                  "  t = [+0.15, 0.00, -0.05] m",
                  "  (15cm Depan, 0cm Samping, 5cm Bawah)",
                  "  R = [0.0°, +90.0°, 0.0°] (Hadap Bawah)",
                  "• Kerucut Emisi Akustik 30° ke Dasar",
                  "• Penguncian Skala Mutlak λ* AI Kedalaman"],
                 '#F0FDFA', '#0D9488')

    # Col 5 Top: camera_optical_link (Wide card for R_align)
    draw_tf_card(1845, 235, 495, 165, "camera_optical_link", "Optical RDF", "static_tf_publisher",
                 ["• Kerangka Standar Kamera Pinhole OpenCV (RDF):",
                  "  t = [0.0, 0.0, 0.0] m terhadap camera_link",
                  "  Rotasi Ortogonal R_align [-90.0°, 0.0°, -90.0°]:",
                  "  Z Maju (Sumbu Kedalaman Optis), X Kanan, Y Bawah",
                  "• Matriks Ortogonal: R_align = [[0, 0, 1], [-1, 0, 0], [0, -1, 0]]",
                  "• Basis Proyeksi Dense Neural Depth & PointCloud Metrik"],
                 '#F0FDF4', '#15803D', is_optical=True)

    # Col 5 Bottom: bar30_depth_link
    draw_tf_card(1845, 45, 495, 175, "bar30_depth_link", "Pressure Sensor", "static_tf_publisher",
                 ["• Port Sensor Tekanan Hidrostatis Piezo-I2C (Bar30):",
                  "  t = [0.00, 0.00, -0.08] m (8 cm di Bawah Pusat Massa)",
                  "  R = [0.0°, 0.0°, 0.0°]",
                  "• Resolusi Metrik: 0.2 mm Kolom Air (Kedalaman Absolut Metrik)",
                  "• Datum Tekanan Dasar Laut Z_abs untuk Pengunci Skala Translasi Vertikal EKF"],
                 '#EFF6FF', '#2563EB')

    # Rigid connections from base_link to sensor leaves
    # base_link -> camera_link (in 90 px gap: 1410 to 1500)
    draw_smart_arrow(ax, [(1410, 317), (1500, 317)], color='#16A34A', lw=1.8)
    ax.text(1455, 335, "t=[+0.18, 0, +0.05]", ha='center', va='bottom', fontsize=6.2, fontweight='bold', color='#16A34A', fontfamily='DejaVu Sans')

    # camera_link -> camera_optical_link (in 90 px gap: 1755 to 1845)
    draw_smart_arrow(ax, [(1755, 317), (1845, 317)], color='#15803D', lw=1.8)
    ax.text(1800, 335, "R_align\n(RDF)", ha='center', va='bottom', fontsize=7.0, fontweight='bold', color='#15803D', fontfamily='DejaVu Sans')

    # base_link -> ping1d_sonar_link (clean orthogonal route right in gap center x=1455)
    draw_smart_arrow(ax, [(1410, 280), (1455, 280), (1455, 132), (1500, 132)], color='#0D9488', lw=1.8)
    ax.text(1445, 205, "t=[+0.15, 0, -0.05]", ha='right', va='center', rotation=90, fontsize=6.2, fontweight='bold', color='#0D9488', fontfamily='DejaVu Sans')

    # base_link -> bar30_depth_link (clean route underneath at y=30)
    draw_smart_arrow(ax, [(1410, 260), (1475, 260), (1475, 30), (1820, 30), (1820, 132), (1845, 132)], color='#2563EB', lw=1.8)
    ax.text(1647, 36, "t=[0, 0, -0.08] (Bar30 Hydrostatic)", ha='center', va='bottom', fontsize=6.8, fontweight='bold', color='#2563EB', fontfamily='DejaVu Sans')

    # Save output with 300 DPI
    out_path = r"c:\remote_ROV\gambar_ta\gambar_arsitektur_ros_nodegraph_tf.png"
    plt.savefig(out_path, dpi=300, facecolor='#FFFFFF', edgecolor='none')
    plt.close()
    print(f"[OK] Master publication diagram generated at: {out_path}")

if __name__ == '__main__':
    generate_diagram()
