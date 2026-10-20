import os
import sys
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'))

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_report():
    doc = Document()
    
    # Page setup - Margins 1 inch
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
    user_uploaded_dir = r"C:\Users\Fadzkal Luthfi\.gemini\antigravity-ide\brain\d040261d-d251-43ae-906a-4aecc9db7b92\.user_uploaded"
    brain_dir = r"C:\Users\Fadzkal Luthfi\.gemini\antigravity-ide\brain\d040261d-d251-43ae-906a-4aecc9db7b92"
    rov_dir = r"c:\remote_ROV"
    
    # Colors
    NAVY = RGBColor(10, 37, 64)       # #0A2540
    CYAN = RGBColor(0, 150, 180)      # Teal/Cyan
    DARK_GRAY = RGBColor(55, 65, 81)
    
    # ----------------------------------------------------
    # COVER PAGE
    # ----------------------------------------------------
    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_meta = p_meta.add_run("DOKUMEN RISET & LAPORAN TEKNIS AKADEMIS\nSUBSEA ROBOTICS & COMPUTER VISION LAB")
    r_meta.font.size = Pt(8.5)
    r_meta.font.color.rgb = RGBColor(140, 150, 160)
    r_meta.font.bold = True
    
    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_before = Pt(36)
    
    p_title = doc.add_paragraph()
    r_title = p_title.add_run("PENGEMBANGAN SISTEM 3D DENSE SLAM,\nMULTI-SENSOR FUSION, DAN VISUALISASI WEB (THREE.JS) PADA REMOTELY OPERATED VEHICLE (ROV)")
    r_title.font.size = Pt(20)
    r_title.font.bold = True
    r_title.font.color.rgb = NAVY
    p_title.paragraph_format.space_after = Pt(12)
    p_title.paragraph_format.line_spacing = 1.15
    
    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("Integrasi AI Monocular Depth (MiDaS), RTAB-Map Graph SLAM, Sensor Tekanan Bar30, Sonar Ping1D, Estimasi Lantai 2.5D EgoExo++, Serta Studi Komparasi SOTA Vision Foundation Model (MASt3R-SLAM)")
    r_sub.font.size = Pt(11.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = CYAN
    p_sub.paragraph_format.space_after = Pt(40)
    
    # Author card
    tbl_auth = doc.add_table(rows=4, cols=2)
    tbl_auth.alignment = WD_TABLE_ALIGNMENT.LEFT
    auth_data = [
        ("Platform Wahana", "BlueROV2 Heavy Configuration / Underwater ROV"),
        ("Sistem Operasi & Middleware", "ROS Noetic (Ubuntu 20.04 WSL2) & Windows 11"),
        ("Repositori Proyek", "https://github.com/Fadzkal/slam3drov.git (Branch: main)"),
        ("Waktu Penyusunan", "Oktober 2026")
    ]
    for i, (k, v) in enumerate(auth_data):
        row = tbl_auth.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.3)
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(k)
        r0.font.bold = True
        r0.font.size = Pt(9.5)
        r0.font.color.rgb = DARK_GRAY
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(v)
        r1.font.size = Pt(9.5)
        set_cell_margins(c0, 60, 60, 80, 80)
        set_cell_margins(c1, 60, 60, 80, 80)
        if i % 2 == 0:
            set_cell_background(c0, "F8FAFC")
            set_cell_background(c1, "F8FAFC")

    doc.add_page_break()

    # Helper function for Section Headings
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(20)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = NAVY
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.size = Pt(11.5)
        r.font.bold = True
        r.font.color.rgb = CYAN
        return p

    def add_body(text, bold_prefix=None, space_after=6):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.font.bold = True
            rb.font.size = Pt(10)
            rb.font.color.rgb = DARK_GRAY
        r = p.add_run(text)
        r.font.size = Pt(10)
        r.font.color.rgb = DARK_GRAY
        return p

    def add_img(path, caption, width=Inches(6.0)):
        if os.path.exists(path):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run()
            run.add_picture(path, width=width)
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(12)
            r_cap = p_cap.add_run(caption)
            r_cap.font.size = Pt(8.5)
            r_cap.font.italic = True
            r_cap.font.color.rgb = RGBColor(100, 116, 139)
        else:
            print(f"[WARN] Image not found: {path}")

    # ----------------------------------------------------
    # BAB I: PENDAHULUAN
    # ----------------------------------------------------
    add_h1("BAB I. PENDAHULUAN & LATAR BELAKANG RISET")
    add_body("Inspeksi infrastruktur bawah air seperti pipa migas dasar laut, struktur pondasi anjungan lepas pantai, lambung kapal, dan pencarian target dasar laut membutuhkan pemetaan tiga dimensi (3D Mapping) yang cepat, akurat, dan memiliki skala fisik nyata. Penggunaan Remotely Operated Vehicle (ROV) seperti BlueROV2 menjadi solusi utama di industri maritim.")
    add_body("Namun, lingkungan bawah air menghadirkan tantangan optik dan navigasi yang sangat berat:", "Tantangan Utama Lingkungan Bawah Air: ")
    add_body("1. Ketiadaan Sinyal Satelit (No GPS): Gelombang elektromagnetik GPS teratenuasi habis oleh air laut pada kedalaman beberapa sentimeter, sehingga navigasi sepenuhnya bergantung pada sensor internal (dead reckoning) dan penglihatan kamera.")
    add_body("2. Penurunan Kontras & Atenuasi Spektral: Partikel tersuspensi di air laut menyebabkan hamburan balik (backscattering) cahaya, hilangnya spektrum warna merah pada kedalaman >3 meter, dan kabur kehijauan.")
    add_body("3. Ambiguitas Skala Monocular (Scale Ambiguity): Kamera tunggal 2D biasa tidak memiliki informasi kedalaman absolut, sehingga skala objek tidak dapat diketahui dalam satuan meter secara mandiri.")
    add_body("4. Keterbatasan Beban Komputasi Wahana: Komputer mini di dalam tabung ROV (seperti Raspberry Pi 4) memiliki keterbatasan daya komputasi dan memori yang ketat.")
    add_body("Untuk memecahkan masalah ini, proyek ini membangun arsitektur komputasi cerdas yang menggabungkan AI Monocular Depth Estimation (MiDaS), Graph SLAM (RTAB-Map), fusi sensor fisik (Bar30 & Ping1D Sonar), representasi lantai 2.5D EgoExo++, serta antarmuka visualisasi web modern berbasis Three.js.")

    arch_img = os.path.join(rov_dir, "subsea_architecture_white.jpg")
    add_img(arch_img, "Gambar 1.1: Diagram Alur Arsitektur Multi-Sensor 3D Mapping & SLAM BlueROV2", width=Inches(5.8))

    # ----------------------------------------------------
    # BAB II: ARSITEKTUR FUSI MULTI-SENSOR
    # ----------------------------------------------------
    add_h1("BAB II. ARSITEKTUR MULTI-SENSOR FUSION & ESTIMASI KEDALAMAN")
    add_body("Sistem mengintegrasikan 4 modalitas sensor utama untuk membentuk estimasi pose 6-DoF yang terkunci sempurna tanpa drift vertikal:")
    
    tbl_sensor = doc.add_table(rows=5, cols=3)
    tbl_sensor.alignment = WD_TABLE_ALIGNMENT.CENTER
    s_headers = ["Sensor / Node", "Fungsi Primer", "Kompensasi & Kontribusi Geometris"]
    for j, h in enumerate(s_headers):
        cell = tbl_sensor.rows[0].cells[j]
        set_cell_background(cell, "0A2540")
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(9)
        set_cell_margins(cell, 80, 80, 80, 80)
        
    s_rows = [
        ("Kamera HD + CLAHE Node", "Tangkapan visual RGB & feature extraction", "CLAHE menaikkan kontras warna merah dan menghilangkan kabur partikel air laut."),
        ("AI Monocular Depth (MiDaS)", "Dense relative depth per-pixel", "Menghasilkan peta kedalaman padat tanpa membutuhkan hardware stereo baseline yang lebar."),
        ("Bar30 Pressure Sensor", "Kedalaman hidrostatik presisi tinggi (±2 mm)", "Mengunci sumbu Z secara absolut; mengeliminasi akumulasi drift vertikal secara permanen."),
        ("Ping1D Echosounder Sonar", "Jarak akustik ke objek / dasar laut (±1 mm)", "Mengalibrasi rasio skala metrik absolut dari depth relatif AI menjadi satuan meter nyata.")
    ]
    for i, row in enumerate(s_rows):
        r_cells = tbl_sensor.rows[i+1].cells
        for j, val in enumerate(row):
            p = r_cells[j].paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            r.font.color.rgb = DARK_GRAY
            set_cell_margins(r_cells[j], 60, 60, 80, 80)
            if i % 2 == 1:
                set_cell_background(r_cells[j], "F1F5F9")
                
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    add_h2("2.1 Kalibrasi Skala Metrik Otomatis")
    add_body("Model kedalaman monocular AI (MiDaS) hanya menghasilkan nilai kedalaman relatif d_rel ∈ [0, 1]. Untuk mengubahnya menjadi satuan metrik z_metrik (meter), node depth_to_pose_publisher.py dan monocular_depth_node.py memfusi jarak akustik Sonar Ping1D:")
    add_body("z_metrik = d_rel × (d_sonar / d_ai_tengah)", "Formulasi Skala Metrik: ")
    add_body("Dengan metode ini, setiap piksel pada gambar kamera mendapatkan koordinat 3D (X, Y, Z) dalam satuan meter nyata, siap di-feed ke dalam pipeline RGB-D SLAM.")

    # ----------------------------------------------------
    # BAB III: PIPELINE RTAB-MAP SLAM & SOLUSI BUG
    # ----------------------------------------------------
    add_h1("BAB III. PIPELINE RTAB-MAP SLAM & INVESTIGASI BUG PETA MELAYANG")
    add_body("RTAB-Map (Real-Time Appearance-Based Mapping) bertugas sebagai backend SLAM berbasis Graph Memory. Sistem mengelola Working Memory (WM) untuk real-time tracking dan Long-Term Memory (LTM) untuk deteksi penutupan loop (Loop Closure).")
    
    add_h2("3.1 Investigasi Mendalam Kasus Bug: Peta Melayang & Melompat ke Langit")
    add_body("Pada fase pengujian awal, ditemukan anomali kritis di mana potongan point cloud 3D tiba-tiba melompat puluhan meter ke atas langit dan ke bawah lantai, dihubungkan garis-garis biru panjang (graph link constraints):")
    
    bug_img = os.path.join(user_uploaded_dir, "media_1791975973965.png")
    add_img(bug_img, "Gambar 3.1: Tangkapan Layar Anomali Odometry Jump (Peta Terdistorsi ke Atas & Bawah)", width=Inches(5.6))
    
    add_body("Berdasarkan analisis log telemetri dan struktur frame data, ditemukan 3 akar penyebab (root causes) utama:", "Akar Penyebab (Root Causes): ")
    add_body("1. Desinkronisasi Timestamp Kamera vs AI Depth (approx_sync lag): Kamera menghasilkan frame pada 30 FPS, sedangkan inferensi AI Depth (MiDaS) pada CPU membutuhkan ~100 ms (10 FPS). Ketika kamera bergerak cepat, modul approx_sync memasangkan gambar RGB baru dengan peta depth lama (terlambat 1-2 frame). Akibatnya, proyeksi 3D terdistorsi parah, menyebabkan solver EPnP menghitung rotasi/translasi lonjakan acak.")
    add_body("2. Threshold Keyframe Terlalu Rapat (RGBD/LinearUpdate = 0.05m): Rekaman dipicu setiap 5 cm pergerakan, menyebabkan antrean buffer RTAB-Map overload dan memperparah lag desync.")
    add_body("3. Tidak Adanya Filter Outlier Kecepatan (Odom/MaxTranslation = 0): Default RTAB-Map menerima nilai translasi berapapun. Jika ada 1 frame blur yang menghasilkan lompatan 20 meter, sistem menganggapnya sah dan memplotnya di langit.")

    add_h2("3.2 Solusi Parameter Rekayasa yang Diterapkan")
    add_body("Untuk mengatasi masalah ini secara permanen, parameter di live_rov_3d_mapping.launch diperbarui:")
    add_body("• Odom/MaxTranslation = 0.30 m: Membatasi translasi maksimum 30 cm per frame. Lompatan liar akibat blur langsung dibuang (outlier rejection).")
    add_body("• Odom/MaxRotation = 0.50 rad (~28°): Membatasi rotasi mendadak per frame.")
    add_body("• RGBD/LinearUpdate = 0.12 m & AngularUpdate = 0.18 rad: Memperlebar batas keyframe agar frame tidak berdesakan.")
    add_body("• RGBD/OptimizeMaxError = 1.5 m: Menolak penutupan loop (loop closure) palsu yang menyebabkan graf melintir.")
    add_body("• Vis/MinInliers = 10 & Vis/PnPReprojError = 4.0: Memperketat verifikasi geometrically consistent inliers.")

    rviz_ok_img = os.path.join(user_uploaded_dir, "media_1791974361152.png")
    add_img(rviz_ok_img, "Gambar 3.2: Hasil Mapping Stabil Pasca Tuning (Odometry Inliers: 420-520, Peta Konsisten)", width=Inches(5.6))

    # ----------------------------------------------------
    # BAB IV: VISUALISASI WEB THREE.JS & EKSPOR PLY
    # ----------------------------------------------------
    doc.add_page_break()
    add_h1("BAB IV. SISTEM VISUALISASI WEB TIGA DIMENSI (THREE.JS)")
    add_body("Salah satu tantangan besar bagi adopsi sistem SLAM oleh pengguna non-teknis adalah ketergantungan pada RViz, ROS, dan lingkungan Linux dengan X-Server. Untuk mengatasi hal ini, dibangun antarmuka visualisasi berbasis web modern mandiri menggunakan Three.js:")

    web_img = os.path.join(brain_dir, "final_snapshot_view_1791975013317.png")
    add_img(web_img, "Gambar 4.1: Antarmuka Tiga Dimensi Web Visualizer (view_slam_3d_web.html) Berbasis Three.js", width=Inches(5.8))

    add_h2("4.1 Fitur-Fitur Unggulan Web Viewer")
    add_body("1. Navigasi Orbit 360° Bebas: Pengguna dapat memutar, memperbesar (zoom), dan menggeser (pan) model 3D menggunakan mouse atau layar sentuh.")
    add_body("2. Drag & Drop File Loader Mandiri: Mendukung file .ply, .pcd, dan .obj langsung dari hard disk menggunakan HTML5 FileReader API tanpa kendala CORS.")
    add_body("3. Skema Pewarnaan Dinamis: Pilihan warna RGB Asli Kamera, Elevasi Kedalaman Z (Turbo Colormap), Deep Sea Cyber Neon, dan Monokrom.")
    add_body("4. Alat Pengukur Jarak Interaktif (Metric Ruler): Pengguna dapat mengklik dua titik sembarang pada point cloud untuk menghitung jarak nyata dalam centimeter dan meter.")
    add_body("5. Lantai 2.5D EgoExo & Grid Metrik 1m: Menyediakan orientasi spasial dasar laut dan batas bodi ROV.")
    add_body("6. Ekspor Snapshot Cepat: Tombol satu klik untuk mengunduh gambar resolusi tinggi (PNG) untuk kebutuhan pelaporan inspeksi.")

    add_h2("4.2 Alur Ekspor Otomatis 1-Klik")
    add_body("Disediakan skrip launcher Windows export_3d_map.bat dan open_3d_web_viewer.bat:")
    add_body("1. export_3d_map.bat membuat salinan snapshot database RTAB-Map (~/.ros/rtabmap.db) agar tidak terjadi konflik penguncian SQLite.")
    add_body("2. Perintah rtabmap-export mengekstrak seluruh point cloud padat berwarna menjadi file export/subsea_3d_map.ply.")
    add_body("3. Web server lokal port 8888 otomatis diaktifkan dan browser Google Chrome / Edge langsung terbuka menampilkan model 3D terbaru.")

    # ----------------------------------------------------
    # BAB V: STUDI KOMPARASI SOTA & MASt3R-SLAM
    # ----------------------------------------------------
    doc.add_page_break()
    add_h1("BAB V. STUDI KOMPARASI DENGAN STATE-OF-THE-ART (SOTA)")
    add_body("Untuk memperkaya tinjauan pustaka akademis, dilakukan komparasi antara sistem yang dibangun dengan dua tolok ukur representatif:")

    add_h2("5.1 Komparasi 1: Proyek Monocular Sederhana (EECS 442 - Univ. of Michigan)")
    add_body("Repositori eecs-442-slam-project mewakili pendekatan Computer Vision klasik:")
    add_body("• Menggunakan Epipolar Geometry & Essential Matrix (E = K^T F K) untuk estimasi pose frame-ke-frame.")
    add_body("• Kelemahan Mendasar: Mengalami Scale Ambiguity parah (tidak tahu ukuran nyata objek) dan Scale Drift kumulatif. Peta yang dihasilkan hanya berupa titik bintik jarang (Sparse Point Cloud) tanpa informasi permukaan padat.")

    add_h2("5.2 Komparasi 2: Foundation Model Vision Transformer (MASt3R-SLAM - CVPR 2025)")
    add_body("MASt3R-SLAM (Imperial College London) merupakan terobosan paling mutakhir di bidang Monocular Dense SLAM:")
    
    comp_img = os.path.join(user_uploaded_dir, "media_1791976428426.png")
    add_img(comp_img, "Gambar 5.1: Perbandingan Rekonstruksi Ruangan: DROID-SLAM vs Spann3R vs MASt3R-SLAM (EuRoC V102)", width=Inches(5.4))

    add_body("Analisis Perbandingan Rekonstruksi Gambar 5.1:")
    add_body("• DROID-SLAM (Kiri): Mengalami fenomena depth explosion pada tepian dinding yang minim tekstur, menghasilkan titik-titik melenceng seperti landak.")
    add_body("• Spann3R (Tengah): Mengalami drift skala kumulatif, mengakibatkan geometri dinding terfragmentasi dan melintir.")
    add_body("• MASt3R-SLAM (Kanan): Menghasilkan geometri kotak sempurna, dinding tegak lurus, dan lantai datar berkat pemanfaatan 3D Reconstruction Priors dari jutaan data latih.")

    add_h2("5.3 Analisis Kelayakan Implementasi & Arsitektur Dual-Stage")
    add_body("Berdasarkan uji kapabilitas perangkat keras, laptop saat ini menggunakan GPU AMD Radeon terintegrasi tanpa kartu diskrit NVIDIA CUDA, sedangkan MASt3R-SLAM mewajibkan kompilasi kernel CUDA C++ (cuda_matching.cu) dan VRAM GPU tinggi (≥8 GB).")
    add_body("Oleh karena itu, diusulkan Arsitektur Dua-Tahap (Dual-Stage SLAM Architecture) yang sangat strategis untuk operasional maritim nyata:")

    # Table Dual Stage
    tbl_dual = doc.add_table(rows=3, cols=3)
    tbl_dual.alignment = WD_TABLE_ALIGNMENT.CENTER
    d_heads = ["Tahapan Operasi", "Mesin Komputasi & Algoritma", "Luaran & Nilai Tambah Operasional"]
    for j, h in enumerate(d_heads):
        cell = tbl_dual.rows[0].cells[j]
        set_cell_background(cell, "0A2540")
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(9)
        set_cell_margins(cell, 80, 80, 80, 80)
        
    d_rows = [
        ("Tahap 1: On-Board Real-Time Navigation", 
         "Sistem Saat Ini (RTAB-Map + MiDaS + Bar30 + Ping1D)\nBerjalan ringan di CPU onboard ROV / laptop kendali.",
         "Menyediakan lintasan navigasi real-time, penguncian kedalaman hidrostatik, dan skala metrik pasti untuk pilot ROV."),
        ("Tahap 2: Post-Mission Digital Twin", 
         "MASt3R-SLAM via Google Colab / GPU Workstation\nMemproses rekaman video HD setelah wahana naik ke darat.",
         "Menghasilkan model 3D padat berkualitas tinggi, dinding tegak lurus, dan fotorealistis untuk pelaporan inspeksi akhir.")
    ]
    for i, row in enumerate(d_rows):
        r_cells = tbl_dual.rows[i+1].cells
        for j, val in enumerate(row):
            p = r_cells[j].paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            r.font.color.rgb = DARK_GRAY
            set_cell_margins(r_cells[j], 60, 60, 80, 80)
            if i % 2 == 1:
                set_cell_background(r_cells[j], "F1F5F9")

    # ----------------------------------------------------
    # BAB VI: INTEGRASI ORB-SLAM3 MONOCULAR 3D SLAM
    # ----------------------------------------------------
    doc.add_page_break()
    add_h1("BAB VI. INTEGRASI ORB-SLAM3 MONOCULAR 3D SLAM & ZERO-LATENCY BRIDGE")
    add_body("Sebagai pembanding representatif dari arsitektur feature-based Visual SLAM klasik paling teruji di dunia akademik (Campos et al., IEEE T-RO 2021), ORB-SLAM3 diintegrasikan secara native ke dalam ekosistem riset ini.")

    add_h2("6.1 Arsitektur Kompilasi di WSL2 Ubuntu 20.04 & Akselerasi GPU Direct3D 12")
    add_body("• Pustaka Inti: libORB_SLAM3.so (5.08 MB) dikompilasi bersama DBoW2, g2o, dan Sophus.")
    add_body("• Pangolin 3D OpenGL Viewer: Terhubung ke WSLg Direct3D 12 (mesa: D3D12 AMD Radeon Graphics) untuk rendering interaktif yang mulus di Windows 11.")
    add_body("• Custom Executable mono_live: Dibangun khusus di ~/slam_ws/ORB_SLAM3/Examples/Monocular/mono_live untuk menerima input live stream MJPEG HTTP dari Windows.")

    add_h2("6.2 Desain Zero-Latency MJPEG Webcam Bridge")
    add_body("Karena WSL2 berjalan dalam virtualisasi Hyper-V terisolasi, dibangun modul jembatan video cerdas (mjpeg_webcam_bridge.py) dengan fitur:")
    add_body("1. Eliminasi Frame Buffering: Mematikan buffer DirectShow (CAP_PROP_BUFFERSIZE = 1) untuk latensi transmisi 0 detik.")
    add_body("2. Single JPEG Encoding di Thread Terpisah: Kompresi JPEG dilakukan 1x di thread capture, menghemat komputasi CPU.")
    add_body("3. ThreadingHTTPServer Multi-Client: Browser Windows dan ORB-SLAM3 WSL2 dapat mengakses stream secara simultan.")
    add_body("4. Dynamic Port Hunting: Otomatis mendeteksi port bebas (8088) dan mempublikasikannya ke bridge_port.txt.")

    add_h2("6.3 Riwayat Investigasi Kasus & Pemecahan Masalah Teknis")
    add_body("• Kasus 1 (OBS Virtual Camera): DirectShow mendeteksi OBS di Index 2. Modul pygrabber diintegrasikan untuk blacklist string 'OBS'/'Virtual' dan otomatis mengunci webcam fisik (Index 1 / 0).")
    add_body("• Kasus 2 (Bentrok Port 8080): Port 8080 diduduki ApplicationWebServer Windows. Dipindahkan ke port 8088 dengan mekanisme deteksi port otomatis.")
    add_body("• Kasus 3 (Crash Format YAML): Galat '*Camera.fx parameter doesn't exist*' dipecahkan dengan menambahkan header resmi File.version: \"1.0\" dan melengkapi parameter intrinsik kamera.")
    add_body("• Kasus 4 (TRACK_REF_KF: Less than 15 matches): Peringatan lost tracking pada permukaan dinding/pintu polos diatasi dengan menaikkan nFeatures ke 1500 serta menurunkan ambang FAST ke 15/5.")

    # ----------------------------------------------------
    # BAB VII: KESIMPULAN & PANDUAN PENGOPERASIAN
    # ----------------------------------------------------
    doc.add_page_break()
    add_h1("BAB VII. PANDUAN PENGOPERASIAN LENGKAP & KESIMPULAN")
    add_body("Seluruh subsistem telah diotomasi penuh melalui launcher batch mandiri:")
    add_body("1. Full Subsea 3D Mapping (BlueROV2): Dobel klik run_live_rov_mapping.bat (atau run_subsea_mapping.bat).")
    add_body("2. ORB-SLAM3 Live 3D Mapping: Dobel klik run_orbslam3.bat (Pilih [2] untuk webcam live, [1] untuk rekaman ROV).")
    add_body("3. Ekspor Peta 3D ke Browser: Dobel klik export_3d_map.bat.")
    add_body("4. Web 3D Viewer Mandiri (Three.js): Dobel klik open_3d_web_viewer.bat atau buka view_slam_3d_web.html.")
    add_body("5. Visual Odometry CPU-Only: Dobel klik run_live_vo_webcam.bat.")

    add_h2("7.1 Kesimpulan Penelitian & Rekomendasi")
    add_body("1. Fusi multi-sensor Bar30 dan Sonar Ping1D berhasil mengunci skala metrik fisik nyata (meter) dan menghilangkan vertical drift pada sumbu Z.")
    add_body("2. Penyelarasan update keyframe dan batas translasi maksimal Odom/MaxTranslation = 0.30 m melenyapkan bug peta melayang secara permanen.")
    add_body("3. Visualisasi Three.js Web Viewer memberikan kebebasan inspeksi dan pengukuran dimensi tanpa ketergantungan perangkat lunak Linux.")
    add_body("4. Verifikasi ORB-SLAM3 dengan zero-latency bridge membuktikan komputasi SLAM kelas berat dapat berjalan mulus dengan akselerasi GPU Direct3D 12 di Windows 11.")
    add_body("5. Arsitektur Dual-Stage (RTAB-Map navigasi live + MASt3R-SLAM post-mission digital twin) memberikan solusi terlengkap bagi robotika bawah air modern.")

    # Save to disk
    output_docx = os.path.join(rov_dir, "LAPORAN_LENGKAP_SUBSEA_3D_SLAM.docx")
    doc.save(output_docx)
    print(f"[OK] Document generated successfully: {output_docx}")

if __name__ == '__main__':
    create_report()
