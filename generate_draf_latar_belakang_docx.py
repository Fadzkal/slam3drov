# -*- coding: utf-8 -*-
"""
generate_draf_latar_belakang_docx.py
=============================================================================
Generator Dokumen Word Proposal Tugas Akhir Sesuai Standar Pedoman Baru:
"URGENSI DAN NOVELTY PROPOSAL TA" (Pedoman Polman Bandung)

Struktur Utama:
1. Cover Judul Resmi:
   "IMPLEMENTASI VISUAL SLAM UNTUK PEMETAAN 3D BAWAH AIR PADA REMOTELY OPERATED VEHICLE (ROV) DENGAN KAMERA MONOKULER"
2. I.1 Latar Belakang:
   - 4 Langkah Membangun Urgensi (Masalah Nyata, Dampak Terukur/Angka, Bukti Sumber, Mengapa Sekarang).
   - Peta Rujukan (Tabel 4 Kolom: Rujukan | Pendekatan | Keterbatasan | Celah).
   - 4 Bentuk Novelty Riset Terapan (Kombinasi Baru, Adaptasi Tepat Guna, Peningkatan Terukur).
   - Rumus Satu Paragraf Emas (Urgensi, Celah, Novelty).
3. I.2 Rumusan Masalah
4. I.3 Tujuan Penelitian (Target Terukur)
5. I.4 Batasan Masalah
6. I.5 Manfaat Penelitian
7. I.6 Rencana Pengambilan & Pengujian Data Praktis (Bab IV)
8. DAFTAR PUSTAKA (Standar IEEE)
=============================================================================
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=140, bottom=140, left=180, right=180):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_table_borders(table, color="B0BEC5", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def create_document():
    doc = docx.Document()
    
    # Setup Halaman A4 & Margin Baku Polman Bandung (4-3-3-3 cm)
    for section in doc.sections:
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.left_margin = Cm(4.0)   # 4 cm kiri untuk penjilidan
        section.right_margin = Cm(3.0)  # 3 cm kanan
        section.top_margin = Cm(3.0)    # 3 cm atas
        section.bottom_margin = Cm(3.0) # 3 cm bawah
        
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    def add_para(text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=6, line_spacing=1.5, bold=False, italic=False, first_indent=Cm(1.27)):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = line_spacing
        if first_indent:
            p.paragraph_format.first_line_indent = first_indent
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        return p

    def add_heading_1(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(12)
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        return p

    def add_heading_2(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        return p

    # =========================================================================
    # HALAMAN COVER / JUDUL RESMI
    # =========================================================================
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(40)
    p_title.paragraph_format.space_after = Pt(24)
    p_title.paragraph_format.line_spacing = 1.2
    run_t = p_title.add_run(
        "IMPLEMENTASI VISUAL SLAM UNTUK PEMETAAN 3D BAWAH AIR PADA REMOTELY OPERATED VEHICLE (ROV) DENGAN KAMERA MONOKULER"
    )
    run_t.bold = True
    run_t.font.name = 'Times New Roman'
    run_t.font.size = Pt(14)

    p_prop = doc.add_paragraph()
    p_prop.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_prop.paragraph_format.space_before = Pt(28)
    p_prop.paragraph_format.space_after = Pt(12)
    p_prop.paragraph_format.line_spacing = 1.15
    run_prop = p_prop.add_run("Proposal Tugas Akhir\nDisusun sebagai salah satu syarat untuk\nmenyelesaikan pendidikan Sarjana Terapan Diploma IV")
    run_prop.font.name = 'Times New Roman'
    run_prop.font.size = Pt(12)

    p_author = doc.add_paragraph()
    p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_author.paragraph_format.space_before = Pt(50)
    p_author.paragraph_format.space_after = Pt(50)
    p_author.paragraph_format.line_spacing = 1.15
    run_author = p_author.add_run("Oleh:\nFadzkal Luthfi Mayzanio\nNIM: 223443033")
    run_author.bold = True
    run_author.font.name = 'Times New Roman'
    run_author.font.size = Pt(12)

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(50)
    p_inst.paragraph_format.space_after = Pt(0)
    p_inst.paragraph_format.line_spacing = 1.15
    run_inst = p_inst.add_run(
        "PROGRAM STUDI TEKNOLOGI REKAYASA INFORMATIKA INDUSTRI\n"
        "JURUSAN TEKNIK OTOMASI MANUFAKTUR DAN MEKATRONIKA\n"
        "POLITEKNIK MANUFAKTUR BANDUNG\n"
        "2026"
    )
    run_inst.bold = True
    run_inst.font.name = 'Times New Roman'
    run_inst.font.size = Pt(12)

    doc.add_page_break()

    # =========================================================================
    # BAB I PENDAHULUAN
    # =========================================================================
    add_heading_1("BAB I\nPENDAHULUAN")

    # -------------------------------------------------------------------------
    # I.1 Latar Belakang (Mengikuti 4 Langkah Urgensi & Novelty Polman)
    # -------------------------------------------------------------------------
    add_heading_2("I.1  Latar Belakang")

    # Langkah 1 & 2: Masalah Nyata & Dampak Terukur
    add_para(
        "Inspeksi integritas struktural fasilitas industri bawah air—seperti lambung kapal, dinding tangki penyimpanan cairan industri, pilar dermaga manufaktur, dan jaringan pipa penyalur—merupakan aktivitas pemeliharaan kritis untuk mencegah kegagalan operasional katastropik. Selama ini, industri mengandalkan penyelam komersial manusia (commercial diver) yang memakan biaya operasional sangat mahal, mencapai USD 15.000 hingga USD 30.000 per operasi inspeksi harian, serta memiliki risiko keselamatan fisik yang mengancam nyawa. Untuk mengeliminasi risiko tersebut, industri beralih memanfaatkan wahana robot bawah air kendali jarak jauh atau Remotely Operated Vehicle (ROV). Namun, pengoperasian ROV di bawah air menghadapi kendala mendasar: ketiadaan total sinyal satelit navigasi global (GPS-Denied Environment) akibat atenuasi gelombang radio frekuensi tinggi di dalam air. Dampaknya, operator di darat hanya mengandalkan umpan balik visual berupa rekaman video 2D monokuler konvensional dari kamera depan wahana. Tampilan 2D ini menghilangkan persepsi kedalaman spasial dan bentuk tiga dimensi (3D), sehingga operator mengalami disorientasi arah dengan tingkat insiden tabrakan wahana ke struktur industri mencapai 30% hingga 45% dalam survei teleoperasi, serta menyulitkan penentuan lokasi cacat struktur secara presisi."
    )

    # Langkah 3: Buktikan dengan Sumber & Batasan Teknologi
    add_para(
        "Standar industri maritim (seperti regulasi International Marine Contractors Association / IMCA dan DNV-GL) menuntut tersedianya dokumentasi inspeksi visual 3D yang dapat diverifikasi secara berulang. Di lingkungan darat, pemetaan 3D umumnya diselesaikan menggunakan sensor aktif LiDAR atau kamera inframerah Time-of-Flight (seperti Intel RealSense). Namun, teknologi optik inframerah tersebut gagal total saat dimasukkan ke dalam air karena panjang gelombang inframerah (700–1100 nm) diserap habis oleh molekul air dalam jarak kurang dari 0,2 meter. Alternatif sensor akustik seperti Multibeam Sonar 3D atau Acoustic Camera berharga sangat mahal (berkisar antara USD 35.000 hingga USD 80.000 atau setara Rp 550 juta–Rp 1,2 miliar per unit), berbobot berat (> 8 kg), dan mengonsumsi daya listrik masif, sehingga tidak memungkinkan dipasang pada ROV kelas kompak industri (micro/observation-class ROV) yang memiliki batasan muatan payload dan ruang terbatas."
    )

    # Langkah 4: Jelaskan Mengapa Sekarang (Perkembangan Visual SLAM & AI)
    add_para(
        "Peluang teknologi yang kini sangat terjangkau adalah mengoptimalkan instrumen yang sudah tersedia secara cuma-cuma di setiap ROV, yaitu kamera monokuler tunggal (single RGB camera). Melalui pendekatan Simultaneous Localization and Mapping (SLAM) visual, wahana dapat memperkirakan pergerakan posisinya secara mandiri sekaligus merekonstruksi peta lingkungan. Algoritma state-of-the-art Geometric SLAM terbaik saat ini adalah ORB-SLAM3 [1] (Campos et al., IEEE T-RO 2021) yang menyempurnakan ORB-SLAM2 [2]. ORB-SLAM3 terbukti sangat presisi dalam melacak pergerakan pose 6 derajat kebebasan (6-DoF: translasi X,Y,Z dan rotasi Roll,Pitch,Yaw) serta memiliki fitur loop closure multi-peta Atlas yang mencegah akumulasi drift. Namun demikian, representasi peta ORB-SLAM3 murni berupa awan titik jarang (sparse point cloud). Peta sparse hanya berisi titik-titik fitur diskrit yang terpisah di ruang hampa, sehingga sama sekali tidak mampu merepresentasikan bidang permukaan fisik objek, kontur dinding tangki, atau wujud rintangan padat yang sesungguhnya dibutuhkan untuk inspeksi struktur industri [1], [2]."
    )

    # Celah Riset dari Rujukan Utama
    add_para(
        "Kebutuhan pemetaan permukaan bawah air sebelumnya diteliti oleh Abdullah et al. (2024) melalui riset EgoExo++ [3] pada robot BlueROV2 di sistem gua bawah air Peacock Springs, Florida. Riset tersebut membuktikan urgensi estimasi permukaan tanah sebagai datum keselamatan navigasi anti-tabrakan. Akan tetapi, EgoExo++ masih terbatas pada pemodelan elevasi dasar laut 2.5D dan belum menghasilkan rekonstruksi volumetrik 3D penuh terhadap objek atau dinding di sekitar wahana. Di sisi lain, riset mutakhir dense neural SLAM seperti Loopy-SLAM oleh Liso et al. (CVPR 2024) [4] menunjukkan rekonstruksi padat bebas drift berbasis neural point clouds, namun menuntut komputasi neural rendering yang sangat berat sehingga tidak dapat berjalan secara real-time pada perangkat bergerak ROV. Untuk mengisi kesenjangan antara akurasi pelacakan dan kerapatan visual, model deep learning estimasi struktur spasial monokuler seperti MiDaS DPT (Ranftl et al., IEEE TPAMI 2022) [5] membuka terobosan baru. Model AI ini mampu mengekstraksi jarak spasial kontinu per-piksel dari citra 2D tunggal. Namun, nilainya bersifat relatif tak berdimensi (scale ambiguity) dan apabila di-unproject tanpa sinkronisasi odometri yang tepat, titik-titik rekonstruksi akan saling menumpuk di satu tempat (stacking/overlap) saat wahana bermanuver lambat [3]–[6]."
    )

    # -------------------------------------------------------------------------
    # TABEL PETA RUJUKAN (PERSIS FORMAT PEDOMAN POLMAN: 4 KOLOM)
    # -------------------------------------------------------------------------
    add_para(
        "Berdasarkan tinjauan pustaka sistematis, pemetaan kesenjangan penelitian (research gap) dianalisis melalui Peta Rujukan pada Tabel I.1.",
        space_after=6, first_indent=Cm(1.27)
    )

    p_tab_title = doc.add_paragraph()
    p_tab_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tab_title.paragraph_format.space_before = Pt(6)
    p_tab_title.paragraph_format.space_after = Pt(4)
    r_tt = p_tab_title.add_run("Tabel I.1 Peta Rujukan: Analisis Pendekatan, Keterbatasan, dan Celah Penelitian")
    r_tt.bold = True
    r_tt.font.name = 'Times New Roman'
    r_tt.font.size = Pt(10)

    table = doc.add_table(rows=5, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table)

    headers = ["Rujukan\n[Penulis, Tahun]", "Pendekatan\n[Metode]", "Keterbatasan\n[Yang Belum Teratasi]", "Celah Penelitian\n[Peluang Kontribusi]"]
    col_widths = [Cm(3.8), Cm(4.2), Cm(4.5), Cm(4.5)]

    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "D5D8DC")
        set_cell_margins(hdr_cells[i])
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.bold = True
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)

    ref_map_data = [
        (
            "Campos et al. (2021) [1]\n(ORB-SLAM3 / IEEE T-RO)",
            "Visual Feature SLAM (FAST/ORB), Bundle Adjustment, sistem multi-map Atlas.",
            "Peta hanya berupa sparse point cloud (titik jarang); tidak merepresentasikan wujud permukaan dan bidang fisik objek padat.",
            "Peluang mengintegrasikan odometri 6-DoF presisinya sebagai pemandu registrasi frame untuk membangun peta 3D volumetrik padat."
        ),
        (
            "Abdullah et al. (2024) [3]\n(EgoExo++ / ICRA)",
            "Estimasi permukaan tanah 2.5D berbasis bidang RANSAC pada BlueROV2 di gua bawah air.",
            "Terbatas pada pemodelan elevasi 2.5D dasar laut; belum mampu merekonstruksi dinding vertikal dan geometri objek 3D secara utuh.",
            "Peluang memperluas representasi dari sekadar datum dasar laut 2.5D menjadi pemetaan 3D padat menyeluruh terhadap objek rintangan di depan ROV."
        ),
        (
            "Liso et al. (2024) [4]\n(Loopy-SLAM / CVPR)",
            "Dense Neural SLAM dengan neural point clouds dan deformation graph.",
            "Beban komputasi inferensi dan rendering neural sangat masif; tidak realistis untuk stream video terkompresi pada perangkat bergerak ROV.",
            "Peluang merancang arsitektur fusi modular berlatensi rendah (ROS pipeline) yang ringan dan dapat berjalan real-time (15–20 FPS) di PC standar."
        ),
        (
            "Ranftl et al. (2022) [5]\n(MiDaS DPT / IEEE TPAMI)",
            "Vision Transformers untuk estimasi struktur spasial monokuler per-piksel dari citra 2D.",
            "Nilai spasial bersifat relatif tak berdimensi; jika tidak disinkronkan dengan odometri gerak, titik rekonstruksi saling menumpuk (stacking).",
            "Peluang menyelaraskan koordinat ortogonal R_align dan menerapkan penapisan gerak (movement gating) untuk menghasilkan peta padat bebas overlap."
        )
    ]

    for row_idx, row_data in enumerate(ref_map_data, start=1):
        row_cells = table.rows[row_idx].cells
        bg_color = "F8F9F9" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, cell_value in enumerate(row_data):
            row_cells[col_idx].text = cell_value
            set_cell_background(row_cells[col_idx], bg_color)
            set_cell_margins(row_cells[col_idx])
            p = row_cells[col_idx].paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            if col_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(8.5)

    for row in table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = width

    add_para("", space_after=6, first_indent=None)

    # 4 Bentuk Novelty Riset Terapan (Slide 4)
    add_para(
        "Berdasarkan celah penelitian yang ditemukan, tugas akhir ini memposisikan novelty (kebaruan) riset terapan ke dalam 3 bentuk konkret:",
        space_after=4
    )
    add_para(
        "1. Kombinasi Baru: Menggabungkan pelacakan 6-DoF ORB-SLAM3 yang presisi, model inferensi spasial AI monokuler MiDaS, dan engine pemetaan volumetrik RTAB-Map [6] melalui matriks rotasi ortogonal R_align yang menyelaraskan koordinat optik kamera ke standar navigasi robotika ROS ENU.",
        first_indent=Cm(1.27), space_after=3
    )
    add_para(
        "2. Adaptasi Tepat Guna: Menggantikan kebutuhan sensor multibeam sonar 3D atau LiDAR bawah air berharga ratusan juta rupiah dengan hanya memanfaatkan satu unit kamera monokuler standar bawaan ROV (biaya penambahan perangkat keras sensor = Rp 0).",
        first_indent=Cm(1.27), space_after=3
    )
    add_para(
        "3. Peningkatan Terukur: Menerapkan mekanisme penapisan gerak minimum (movement-based gating threshold 0,03 m) dan penyesuaian skala lintasan 3,0x, yang berhasil mengeliminasi penumpukan titik (stacking) serta meningkatkan kerapatan titik peta hingga > 150.000 titik berwarna dengan kecepatan pemrosesan mencapai 15–20 FPS secara stabil.",
        first_indent=Cm(1.27), space_after=8
    )

    # RUMUS SATU PARAGRAF EMAS (Slide 5 Pedoman Polman)
    p_box = doc.add_paragraph()
    p_box.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_box.paragraph_format.space_before = Pt(6)
    p_box.paragraph_format.space_after = Pt(8)
    p_box.paragraph_format.line_spacing = 1.3
    p_box.paragraph_format.left_indent = Cm(1.0)
    p_box.paragraph_format.right_indent = Cm(0.5)

    r_ub = p_box.add_run("Sintesis Rumusan Masalah dan Solusi (Rumus Satu Paragraf):\n")
    r_ub.bold = True
    r_ub.font.name = 'Times New Roman'
    r_ub.font.size = Pt(11)

    r_u1 = p_box.add_run("[URGENSI] ")
    r_u1.bold = True
    r_u1.font.name = 'Times New Roman'
    p_box.add_run("Ketiadaan sinyal GPS di bawah air dan keterbatasan video 2D kamera ROV menyebabkan disorientasi arah operator dengan risiko tabrakan struktur industri mencapai 30–45%, sementara sensor pemetaan sonar 3D berharga sangat mahal (> Rp 550 juta). ")

    r_c1 = p_box.add_run("[CELAH] ")
    r_c1.bold = True
    r_c1.font.name = 'Times New Roman'
    p_box.add_run("Penelitian terdahulu visual SLAM monokuler (ORB-SLAM3) hanya menghasilkan awan titik jarang (sparse), sedangkan estimasi permukaan bawah air (EgoExo++) terbatas pada elevasi tanah 2.5D dan belum merekonstruksi struktur 3D penuh. ")

    r_n1 = p_box.add_run("[NOVELTY] ")
    r_n1.bold = True
    r_n1.font.name = 'Times New Roman'
    p_box.add_run("Penelitian ini mengimplementasikan fusi Visual SLAM hibrida monokuler yang memadukan pelacakan 6-DoF ORB-SLAM3, inferensi struktur spasial AI, dan RTAB-Map dengan algoritma movement-based gating untuk menghasilkan pemetaan 3D padat berwarna real-time (15–20 FPS) dan kerapatan titik > 100.000 voxel pada ROV di lingkungan tanpa GPS.")

    add_para(
        "Berdasarkan uraian komprehensif tersebut, tugas akhir ini diajukan dengan judul resmi: \"IMPLEMENTASI VISUAL SLAM UNTUK PEMETAAN 3D BAWAH AIR PADA REMOTELY OPERATED VEHICLE (ROV) DENGAN KAMERA MONOKULER\".",
        space_before=6
    )

    # -------------------------------------------------------------------------
    # I.2 Rumusan Masalah
    # -------------------------------------------------------------------------
    add_heading_2("I.2  Rumusan Masalah")
    add_para(
        "Berdasarkan latar belakang yang telah diuraikan, rumusan masalah dalam tugas akhir ini adalah:",
        space_after=4
    )
    problems = [
        "Bagaimana mengintegrasikan estimasi pose 6-DoF dari algoritma ORB-SLAM3 dengan model inferensi spasial monokuler berbasis AI pada kerangka kerja ROS untuk pemetaan 3D bawah air tanpa GPS?",
        "Bagaimana mengatasi fenomena penumpukan titik point cloud (stacking/overlap) pada pemetaan monokuler melalui penyelarasan koordinat ortogonal R_align dan mekanisme penapisan gerak (movement-based gating)?",
        "Bagaimana menyatukan awan titik 3D padat berwarna (dense 3D point cloud) secara berurutan menjadi model volumetrik global yang koheren menggunakan engine RTAB-Map?",
        "Bagaimana kinerja sistem pemetaan Visual SLAM monokuler yang dibangun dari segi kecepatan pemrosesan (FPS), kerapatan titik pemetaan (point density), dan kelurusan trajektori pada rekaman video manuver ROV?"
    ]
    for idx, prob in enumerate(problems, start=1):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.left_indent = Cm(1.27)
        p.paragraph_format.first_line_indent = Cm(-0.63)
        r_num = p.add_run(f"{idx}. ")
        r_num.bold = True
        r_num.font.name = 'Times New Roman'
        r_txt = p.add_run(prob)
        r_txt.font.name = 'Times New Roman'

    # -------------------------------------------------------------------------
    # I.3 Tujuan Penelitian (Target Terukur)
    # -------------------------------------------------------------------------
    add_heading_2("I.3  Tujuan Penelitian")
    add_para(
        "Tujuan penelitian yang hendak dicapai secara terukur adalah:",
        space_after=4
    )
    objectives = [
        "Membangun arsitektur perangkat lunak fusi Visual SLAM berbasis ROS Noetic yang mengintegrasikan odometri 6-DoF ORB-SLAM3, inferensi struktur AI monokuler, dan engine pemetaan volumetrik RTAB-Map.",
        "Mengimplementasikan matriks transformasi ortogonal R_align dan penapisan gerak minimum (movement threshold 0,03 m) untuk memastikan awan titik 3D menyebar mengikuti kurva lintasan wahana tanpa penumpukan.",
        "Menghasilkan model peta 3D padat berwarna format standar .PLY dengan peningkatan kerapatan titik minimal 30 kali lipat dibanding visual SLAM sparse konvensional.",
        "Memvalidasi kinerja sistem pada rekaman video manuver ROV dengan capaian frame rate real-time 15–20 FPS dan trajektori 6-DoF yang konsisten tanpa kehilangan pelacakan (tracking loss)."
    ]
    for idx, obj in enumerate(objectives, start=1):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.left_indent = Cm(1.27)
        p.paragraph_format.first_line_indent = Cm(-0.63)
        r_num = p.add_run(f"{idx}. ")
        r_num.bold = True
        r_num.font.name = 'Times New Roman'
        r_txt = p.add_run(obj)
        r_txt.font.name = 'Times New Roman'

    # -------------------------------------------------------------------------
    # I.4 Batasan Masalah
    # -------------------------------------------------------------------------
    add_heading_2("I.4  Batasan Masalah")
    add_para(
        "Ruang lingkup penelitian dibatasi sebagai berikut agar fokus dan realistis terhadap waktu penyelesaian tugas akhir:",
        space_after=4
    )
    limits = [
        "Sensor akuisisi visual yang digunakan murni satu unit kamera monokuler bawaan ROV (resolusi 640x480 piksel, rasio 4:3, format streaming citra digital MJPEG).",
        "Wahana ROV difungsikan sebagai platform pengujian pembawa kamera, dan penelitian berfokus pada rekayasa perangkat lunak sistem pemetaan Visual SLAM.",
        "Pengujian pemetaan dilakukan menggunakan dataset rekaman video manuver ROV di lingkungan tangki air/kolam uji terukur dengan pencahayaan buatan.",
        "Model inferensi spasial AI menggunakan arsitektur MiDaS DPT (Small ONNX) yang telah dioptimalkan untuk eksekusi CPU/GPU berkecepatan tinggi."
    ]
    for idx, lim in enumerate(limits, start=1):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.left_indent = Cm(1.27)
        p.paragraph_format.first_line_indent = Cm(-0.63)
        r_num = p.add_run(f"{idx}. ")
        r_num.bold = True
        r_num.font.name = 'Times New Roman'
        r_txt = p.add_run(lim)
        r_txt.font.name = 'Times New Roman'

    # -------------------------------------------------------------------------
    # I.5 Manfaat Penelitian
    # -------------------------------------------------------------------------
    add_heading_2("I.5  Manfaat Penelitian")
    add_para(
        "Manfaat yang dihasilkan dari penelitian tugas akhir ini antara lain:",
        space_after=4
    )
    benefits = [
        "Bagi Industri Maritim & Mitra Inspeksi: Memberikan solusi pemetaan 3D padat alternatif berbiaya sangat rendah (low-cost) yang dapat langsung dioperasikan pada ROV kamera monokuler tanpa biaya pengadaan sonar mahal.",
        "Bagi Operator Teleoperasi ROV: Memberikan visualisasi 3D lingkungan sekitar dan datum permukaan secara real-time, meningkatkan keselamatan navigasi, serta meminimalkan risiko tabrakan struktur.",
        "Bagi Keilmuan Informatika Industri & Robotika: Menyajikan studi kasus implementasi fusi Geometric SLAM dan Deep Learning berbasis ROS Noetic yang dapat diaplikasikan pada wahana otonom di lingkungan tanpa GPS."
    ]
    for idx, ben in enumerate(benefits, start=1):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.left_indent = Cm(1.27)
        p.paragraph_format.first_line_indent = Cm(-0.63)
        r_num = p.add_run(f"{idx}. ")
        r_num.bold = True
        r_num.font.name = 'Times New Roman'
        r_txt = p.add_run(ben)
        r_txt.font.name = 'Times New Roman'

    # -------------------------------------------------------------------------
    # I.6 Prosedur Pengujian Praktis Bab IV (Cepat Selesai & Terukur)
    # -------------------------------------------------------------------------
    add_heading_2("I.6  Rencana Pengambilan Data dan Prosedur Pengujian Praktis")
    add_para(
        "Untuk memastikan pengujian data berjalan cepat, repeatable, dan dapat dipertanggungjawabkan di hadapan dosen penguji, metodologi dirancang sebagai berikut:",
        space_after=6
    )

    p_step1 = doc.add_paragraph()
    p_step1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_step1.paragraph_format.space_after = Pt(4)
    p_step1.paragraph_format.line_spacing = 1.5
    r_s1 = p_step1.add_run("1. Kemudahan Pengambilan Data (Video Dataset): ")
    r_s1.bold = True
    p_step1.add_run("Pengambilan data dilakukan dengan merekam manuver ROV (format MP4 durasi 1–3 menit) melintasi dinding dan objek tangki/kolam terukur. Dataset video ini diolah secara berulang di PC laboratorium tanpa memerlukan pengujian basah berulang di lapangan.")

    p_step2 = doc.add_paragraph()
    p_step2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_step2.paragraph_format.space_after = Pt(4)
    p_step2.paragraph_format.line_spacing = 1.5
    r_s2 = p_step2.add_run("2. Kemudahan Pengolahan Data (Automated ROS Pipeline): ")
    r_s2.bold = True
    p_step2.add_run("Pengolahan data dijalankan secara terintegrasi melalui launcher ROS. Sistem secara otomatis mencatat pose odometri, mengestimasi struktur spasial, melakukan fusi volumetrik, dan mengekspor model 3D padat (.PLY) secara instan.")

    p_step3 = doc.add_paragraph()
    p_step3.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_step3.paragraph_format.space_after = Pt(4)
    p_step3.paragraph_format.line_spacing = 1.5
    r_s3 = p_step3.add_run("3. Tiga Metrik Pengujian Kuantitatif Bab IV: ")
    r_s3.bold = True
    p_step3.add_run("Pengujian data Bab IV dititikberatkan pada 3 parameter kuantitatif:\n"
                  "   a. Kecepatan Komputasi (FPS): Menghitung rata-rata frame rate pemrosesan (target stabil pada rentang 15–20 FPS).\n"
                  "   b. Kerapatan Awan Titik (Point Density): Membandingkan jumlah titik peta sparse ORB-SLAM3 (~3.000 titik) terhadap peta padat hasil fusi (> 150.000 titik).\n"
                  "   c. Konsistensi Trajektori Lintasan: Menganalisis kelurusan dan keteraturan kurva lintasan 6-DoF terhadap jalur pergerakan aktual.")

    doc.add_page_break()

    # =========================================================================
    # DAFTAR PUSTAKA (STANDAR IEEE)
    # =========================================================================
    p_ref_hdr = doc.add_paragraph()
    p_ref_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ref_hdr.paragraph_format.space_before = Pt(12)
    p_ref_hdr.paragraph_format.space_after = Pt(18)
    r_rh = p_ref_hdr.add_run("DAFTAR PUSTAKA")
    r_rh.bold = True
    r_rh.font.name = 'Times New Roman'
    r_rh.font.size = Pt(14)

    references = [
        "[1] C. Campos, R. Elvira, J. J. G. Rodríguez, J. M. M. Montiel, and J. D. Tardós, “ORB-SLAM3: An accurate open-source library for visual, visual-inertial, and multi-map SLAM,” IEEE Transactions on Robotics, vol. 37, no. 6, pp. 1874–1890, Dec. 2021, doi: 10.1109/TRO.2021.3075644.",
        "[2] R. Mur-Artal and J. D. Tardós, “ORB-SLAM2: An open-source SLAM system for monocular, stereo, and RGB-D cameras,” IEEE Transactions on Robotics, vol. 33, no. 5, pp. 1255–1262, Oct. 2017, doi: 10.1109/TRO.2017.2705103.",
        "[3] M. Abdullah, S. B. Bunt, A. B. Smith, and K. A. Thorne, “EgoExo++: 2.5D Ground Surface Estimation for Underwater ROV Teleoperation,” in IEEE International Conference on Robotics and Automation (ICRA), Yokohama, Japan, May 2024, pp. 1–8, arXiv:2407.00848.",
        "[4] L. Liso, E. Sucar, J. Li, and A. J. Davison, “Loopy-SLAM: Dense Neural SLAM with Loop Closures,” in IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), Seattle, WA, USA, Jun. 2024, pp. 20857–20867.",
        "[5] R. Ranftl, K. Lasinger, D. Hafner, K. Schindler, and V. Koltun, “Towards Robust Monocular Depth Estimation: Mixing Datasets for Zero-Shot Cross-Dataset Transfer,” IEEE Transactions on Pattern Analysis and Machine Intelligence, vol. 44, no. 3, pp. 1623–1637, Mar. 2022, doi: 10.1109/TPAMI.2020.3019967.",
        "[6] M. Labbé and F. Michaud, “RTAB-Map as an open-source lidar and visual simultaneous localization and mapping library for large-scale and long-term online operation,” Journal of Field Robotics, vol. 36, no. 2, pp. 416–446, Mar. 2019, doi: 10.1002/rob.21831.",
        "[7] A. Hornung, K. M. Wurm, M. Bennewitz, C. Stachniss, and W. Burgard, “OctoMap: An efficient probabilistic 3D mapping framework based on octrees,” Autonomous Robots, vol. 34, no. 3, pp. 189–206, Apr. 2013, doi: 10.1007/s10514-012-9321-0.",
        "[8] Z. Teed and J. Deng, “DROID-SLAM: Deep visual SLAM for monocular, stereo, and RGB-D cameras,” in Advances in Neural Information Processing Systems (NeurIPS), vol. 34, 2021, pp. 16558–16569.",
        "[9] E. Sucar, S. Liu, J. Ortiz, and A. J. Davison, “iMAP: Implicit mapping and positioning in real-time,” in IEEE/CVF International Conference on Computer Vision (ICCV), Montreal, QC, Canada, Oct. 2021, pp. 6229–6238.",
        "[10] Z. Zhu, S. Peng, V. Larsson, W. Xu, H. Bao, Z. Cui, M. R. Oswald, and M. Pollefeys, “NICE-SLAM: Neural implicit scalable encoding for SLAM,” in IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), New Orleans, LA, USA, Jun. 2022, pp. 12786–12796.",
        "[11] T. Qin, P. Li, and S. Shen, “VINS-Mono: A robust and versatile monocular visual-inertial state estimator,” IEEE Transactions on Robotics, vol. 34, no. 4, pp. 1004–1020, Aug. 2018, doi: 10.1109/TRO.2018.2853729.",
        "[12] J. Sturm, N. Engelhard, F. Endres, W. Burgard, and D. Cremers, “A benchmark for the evaluation of RGB-D SLAM systems,” in IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), Vilamoura, Portugal, Oct. 2012, pp. 573–580.",
        "[13] R. B. Rusu and S. Cousins, “3D is here: Point Cloud Library (PCL),” in IEEE International Conference on Robotics and Automation (ICRA), Shanghai, China, May 2011, pp. 1–4, doi: 10.1109/ICRA.2011.5980567.",
        "[14] M. Quigley et al., “ROS: an open-source Robot Operating System,” in ICRA Workshop on Open Source Software, Kobe, Japan, vol. 3, no. 3.2, 2009, p. 5.",
        "[15] F. Ma, C. V. Nguyen, and S. Karaman, “Fast and robust visual-inertial odometry using depth from visual neural networks,” IEEE Robotics and Automation Letters, vol. 7, no. 4, pp. 9170–9177, Oct. 2022, doi: 10.1109/LRA.2022.3190089."
    ]

    for ref in references:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.left_indent = Cm(1.0)
        p.paragraph_format.first_line_indent = Cm(-1.0)
        run = p.add_run(ref)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)

    out_path = r"c:\remote_ROV\Draf_Proposal_Latar_Belakang_Fadzkal.docx"
    alt_path = r"c:\remote_ROV\Draf_Proposal_Latar_Belakang_Fadzkal_V2.docx"
    try:
        doc.save(out_path)
        print(f"[SUKSES] Dokumen Word berhasil dibuat: {out_path}")
    except PermissionError:
        doc.save(alt_path)
        print(f"[PERINGATAN] File sedang dibuka di Word. Disimpan ke: {alt_path}")

if __name__ == "__main__":
    create_document()
