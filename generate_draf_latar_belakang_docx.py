# -*- coding: utf-8 -*-
"""
generate_draf_latar_belakang_docx.py
=============================================================================
Generator Dokumen Word (.docx) Proposal Tugas Akhir
Fokus Latar Belakang, Masalah, Novelty, Rencana Pengujian Praktis, & Daftar Pustaka.

Judul Resmi:
"IMPLEMENTASI VISUAL SLAM UNTUK PEMETAAN 3D BAWAH AIR PADA REMOTELY OPERATED VEHICLE (ROV) DENGAN KAMERA MONOKULER"

Penulis : Fadzkal Luthfi Mayzanio (NIM: 223443033)
Program : D4 Teknologi Rekayasa Informatika Industri (TRII)
Jurusan : Teknik Otomasi Manufaktur dan Mekatronika (TOMM)
Institusi: Politeknik Manufaktur Bandung (Polman Bandung), 2026
=============================================================================
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Memberi warna latar belakang heksadesimal pada cell tabel."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=140, bottom=140, left=180, right=180):
    """Mengatur padding cell (dalam dxa, 20 dxa = 1 pt)."""
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

def set_table_borders(table, color="D3D3D3", sz="4", val="single"):
    """Menyetel border tabel minimalis elegan."""
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
    
    # Setup Section / Halaman (A4 & Margin Baku Polman Bandung: 4-3-3-3 cm)
    for section in doc.sections:
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.left_margin = Cm(4.0)   # 4 cm kiri untuk penjilidan
        section.right_margin = Cm(3.0)  # 3 cm kanan
        section.top_margin = Cm(3.0)    # 3 cm atas
        section.bottom_margin = Cm(3.0) # 3 cm bawah
        
    # Set default style Font
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    # Helper function untuk paragraf terformat
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
    # HALAMAN COVER / JUDUL PROPOSAL TUGAS AKHIR
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

    # Break ke halaman berikutnya
    doc.add_page_break()

    # =========================================================================
    # BAB I PENDAHULUAN
    # =========================================================================
    add_heading_1("BAB I\nPENDAHULUAN")

    # -------------------------------------------------------------------------
    # I.1 Latar Belakang
    # -------------------------------------------------------------------------
    add_heading_2("I.1  Latar Belakang")

    add_para(
        "Aktivitas inspeksi infrastruktur bawah air, seperti lambung kapal, dinding tangki penyimpanan cairan industri, pilar dermaga, dan pipa penyalur bawah air, memiliki peranan yang sangat penting dalam pemeliharaan fasilitas industri maritim. Di lingkungan darat maupun udara, penentuan posisi wahana robot dapat mengandalkan sinyal navigasi satelit Global Positioning System (GPS). Namun, di lingkungan bawah air, sinyal radio frekuensi tinggi GPS teratenuasi habis oleh media air (GPS-denied environment). Ketiadaan sinyal penentu posisi ini menyebabkan wahana robot bawah air kendali jarak jauh (Remotely Operated Vehicle / ROV) sangat bergantung pada penglihatan visual operator. Sayangnya, umpan balik yang diterima operator selama ini hanyalah rekaman video 2D dari kamera depan. Tampilan 2D ini tidak memberikan informasi spasial bentuk fisik objek, kontur permukaan, maupun riwayat pemetaan area yang telah dilintasi. Keterbatasan persepsi tersebut mengakibatkan operator rentan mengalami disorientasi spasial dan meningkatkan risiko tabrakan wahana dengan rintangan struktur bawah air."
    )

    add_para(
        "Untuk mengatasi ketiadaan GPS, robotika modern memanfaatkan teknologi Simultaneous Localization and Mapping (SLAM) guna membangun peta lingkungan sekaligus melacak posisi wahana secara mandiri. Pada robot darat, pemetaan 3D biasanya memanfaatkan sensor aktif seperti LiDAR atau kamera inframerah Time-of-Flight (contohnya Intel RealSense). Namun, perangkat tersebut tidak dapat digunakan di lingkungan bawah air karena berkas cahaya inframerah diserap habis oleh molekul air dalam jarak beberapa sentimeter saja. Penggunaan sensor akustik seperti multibeam sonar 3D memerlukan biaya yang sangat mahal (mencapai ratusan juta rupiah), membutuhkan konsumsi daya besar, dan dimensi fisik yang terlalu besar untuk sasis ROV kompak. Oleh karena itu, kamera monokuler (kamera tunggal standar) yang sudah menjadi instrumen bawaan di setiap unit ROV menjadi pilihan paling ekonomis dan realistis untuk dimanfaatkan sebagai sensor utama dalam pemetaan 3D."
    )

    add_para(
        "Pemanfaatan kamera tunggal untuk pemetaan dikenal sebagai Visual SLAM monokuler. Salah satu algoritma visual SLAM berbasis fitur geometri terbaik saat ini adalah ORB-SLAM3 yang dikembangkan oleh Campos et al. (2021) [1] menyempurnakan ORB-SLAM2 [2]. ORB-SLAM3 terbukti sangat unggul dalam menghasilkan estimasi pergerakan pose 6 derajat kebebasan (6-DoF: posisi X, Y, Z dan orientasi Roll, Pitch, Yaw) secara stabil dan presisi, serta memiliki kemampuan penutupan lintasan (loop closure) yang mengeliminasi akumulasi kesalahan gerak (drift). Namun demikian, representasi peta yang dihasilkan oleh ORB-SLAM3 murni berupa awan titik jarang (sparse point cloud). Peta sparse ini hanya menampilkan titik-titik fitur diskrit yang terpisah di ruang hampa, sehingga tidak mampu merepresentasikan wujud fisik objek padat, bidang dinding, maupun bentuk rintangan yang sesungguhnya dibutuhkan untuk inspeksi struktur [1], [2]."
    )

    add_para(
        "Kebutuhan pemodelan permukaan padat bawah air sebelumnya diteliti oleh Abdullah et al. (2024) melalui riset EgoExo++ [3] pada robot BlueROV2 di sistem gua bawah air Peacock Springs, Florida. Riset tersebut membuktikan bahwa estimasi permukaan 2.5D sangat krusial bagi teleoperasi ROV untuk menjaga jarak aman dan menghindari tabrakan dengan dasar laut. Namun, pendekatan EgoExo++ masih terbatas pada pemodelan elevasi tanah 2.5D dan belum menghasilkan rekonstruksi volumetrik 3D penuh terhadap objek atau dinding di sekitar wahana. Sementara itu, riset mutakhir dense visual SLAM seperti Loopy-SLAM oleh Liso et al. (CVPR 2024) [4] menunjukkan rekonstruksi padat bebas drift berbasis neural point clouds, namun menuntut komputasi neural rendering yang sangat berat sehingga sulit dijalankan secara real-time pada transmisi video ROV [3], [4]."
    )

    add_para(
        "Guna merekonstruksi peta 3D yang padat (dense 3D mapping) hanya bermodalkan satu kamera monokuler tanpa beban komputasi berlebih, terobosan model kecerdasan buatan (Artificial Intelligence) seperti MiDaS DPT yang dikembangkan oleh Ranftl et al. [5] dapat dimanfaatkan. Model AI ini mampu mengekstraksi informasi jarak spasial per-piksel secara instan dari citra 2D tunggal. Namun, jika informasi spasial dari AI tersebut langsung di-unproject ke ruang 3D tanpa integrasi odometri pose yang tepat, titik-titik rekonstruksi akan saling menumpuk di satu tempat (stacking/overlap), mengakibatkan bentuk peta menjadi acak dan tidak membentuk objek yang koheren. Engine pemetaan volumetrik RTAB-Map (Real-Time Appearance-Based Mapping) yang dikembangkan oleh Labbé dan Michaud [6] memiliki kapabilitas memori jangka panjang dan filter voxel grid 3D yang andal untuk menggabungkan frame-frame citra, namun RTAB-Map membutuhkan masukan odometri 6-DoF yang kontinu dan tersinkronisasi dengan baik [5], [6]."
    )

    add_para(
        "Berdasarkan analisis kesenjangan (research gap) tersebut, terdapat peluang solusi untuk mengintegrasikan keunggulan pelacakan pose 6-DoF dari ORB-SLAM3 [1], kerapatan spasial per-piksel dari model AI monokuler MiDaS [5], dan engine rekonstruksi volumetrik RTAB-Map [6] ke dalam satu kerangka kerja perangkat lunak berbasis ROS (Robot Operating System). Integrasi ini diperkuat dengan matriks transformasi koordinat ortogonal R_align untuk menyelaraskan sistem koordinat optik kamera ke standar robotika navigasi, serta algoritma penapisan gerak minimum (movement-based gating) untuk mencegah penumpukan titik saat ROV diam atau bermanuver perlahan."
    )

    add_para(
        "Berdasarkan latar belakang tersebut, tugas akhir ini difokuskan pada: \"IMPLEMENTASI VISUAL SLAM UNTUK PEMETAAN 3D BAWAH AIR PADA REMOTELY OPERATED VEHICLE (ROV) DENGAN KAMERA MONOKULER\". Melalui implementasi sistem ini, ROV dengan kamera tunggal standar berbiaya rendah dapat menghasilkan model pemetaan 3D padat dan berwarna secara real-time pada lingkungan bawah air tanpa GPS, sehingga meningkatkan efektivitas dan keselamatan teleoperasi inspeksi struktur industri."
    )

    # -------------------------------------------------------------------------
    # TABEL RINGKASAN PENELITIAN TERDAHULU (STATE-OF-THE-ART & RESEARCH GAP)
    # -------------------------------------------------------------------------
    add_para("Ringkasan perbandingan antara penelitian terdahulu dan posisi kebaruan (novelty) tugas akhir ini disajikan pada Tabel I.1.", space_after=6, first_indent=Cm(1.27))

    p_tab_title = doc.add_paragraph()
    p_tab_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tab_title.paragraph_format.space_before = Pt(6)
    p_tab_title.paragraph_format.space_after = Pt(4)
    r_tt = p_tab_title.add_run("Tabel I.1 Perbandingan Penelitian Terdahulu dan Kontribusi Tugas Akhir")
    r_tt.bold = True
    r_tt.font.name = 'Times New Roman'
    r_tt.font.size = Pt(10)

    table = doc.add_table(rows=6, cols=5)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table)

    headers = ["Peneliti & Tahun", "Metode Utama", "Kelebihan", "Keterbatasan / Gap", "Kontribusi Tugas Akhir Ini"]
    col_widths = [Cm(3.0), Cm(2.8), Cm(3.5), Cm(3.5), Cm(3.2)]

    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "EAECEE")
        set_cell_margins(hdr_cells[i])
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.bold = True
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)

    data = [
        (
            "Campos et al. (2021) [1]\n(ORB-SLAM3)",
            "Visual Feature SLAM (FAST/ORB), Bundle Adjustment, Atlas Multi-map.",
            "Pelacakan pose 6-DoF sangat presisi, tahan loop closure, minim drift akumulatif.",
            "Peta berupa sparse point cloud (titik jarang); tidak merepresentasikan wujud permukaan objek padat.",
            "Memanfaatkan ORB-SLAM3 sebagai engine penentu posisi (odometri 6-DoF) presisi tinggi untuk memandu pemetaan."
        ),
        (
            "Abdullah et al. (2024) [3]\n(EgoExo++)",
            "Estimasi permukaan 2.5D berbasis RANSAC pada BlueROV2 di gua bawah air.",
            "Menghasilkan datum keselamatan elevasi dasar laut untuk navigasi anti-tabrakan ROV.",
            "Terbatas pada bidang dasar 2.5D; belum merekonstruksi struktur 3D objek/dinding secara penuh.",
            "Memperluas fungsi pemetaan dari sekadar datum dasar laut menjadi rekonstruksi 3D menyeluruh objek di depan wahana."
        ),
        (
            "Liso et al. (CVPR 2024) [4]\n(Loopy-SLAM)",
            "Dense Neural SLAM dengan neural point clouds dan deformation graph.",
            "Peta 3D padat bebas drift dengan kualitas rendering neural yang fotorealistik.",
            "Komputasi rendering neural sangat berat; tidak realistis untuk stream video ROV berlatensi rendah.",
            "Menerapkan arsitektur fusi modular berlatensi rendah (ROS pipeline) yang ringan dan dapat berjalan real-time."
        ),
        (
            "Ranftl et al. (2022) [5]\n(MiDaS DPT)",
            "Vision Transformers untuk estimasi struktur spasial per-piksel dari citra 2D.",
            "Mengekstraksi peta spasial rapat (dense) secara monokuler tanpa kamera stereo atau laser fisik.",
            "Nilai bersifat relatif tak berdimensi; jika tidak disinkronkan dengan odometri gerak, titik akan saling bertumpuk.",
            "Mengintegrasikan estimasi spasial AI dengan odometri gerak kamera dan penapisan gerak minimum (movement gating)."
        ),
        (
            "Tugas Akhir Ini (2026)\n(Fadzkal Luthfi M.)",
            "Implementasi Fusi Visual SLAM: ORB-SLAM3 + Estimasi AI Monokuler + RTAB-Map Volumetrik.",
            "Menghasilkan pemetaan 3D padat berwarna real-time hanya dari kamera monokuler bawaan ROV di lingkungan tanpa GPS.",
            "Sistem siap diuji pada rekaman video manuver ROV di kolam/tangki uji terukur.",
            "KONTRIBUSI: Fusi praktis low-cost, transformasi koordinat R_align, bebas penumpukan titik, ekspor digital twin 3D (.PLY)."
        )
    ]

    for row_idx, row_data in enumerate(data, start=1):
        row_cells = table.rows[row_idx].cells
        bg_color = "F8F9F9" if row_idx % 2 == 1 else "FFFFFF"
        if row_idx == 5:
            bg_color = "E8F8F5"
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
                if row_idx == 5:
                    r.bold = True

    for row in table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = width

    add_para("", space_after=6, first_indent=None)

    # -------------------------------------------------------------------------
    # I.2 Rumusan Masalah
    # -------------------------------------------------------------------------
    add_heading_2("I.2  Rumusan Masalah")
    add_para(
        "Berdasarkan latar belakang yang telah diuraikan, rumusan masalah dalam tugas akhir ini adalah:",
        space_after=4
    )
    problems = [
        "Bagaimana mengintegrasikan pelacakan pose 6-DoF ORB-SLAM3 dengan model estimasi struktur spasial monokuler berbasis AI pada kerangka kerja ROS untuk pemetaan 3D bawah air tanpa GPS?",
        "Bagaimana mengatasi permasalahan penumpukan titik (stacking/overlap) pada pemetaan 3D monokuler melalui penyelarasan koordinat ortogonal R_align dan penapisan gerak minimum (movement-based gating)?",
        "Bagaimana merekonstruksi dan menyatukan awan titik 3D padat berwarna (dense 3D point cloud) menjadi model volumetrik yang koheren menggunakan engine RTAB-Map?",
        "Bagaimana kinerja sistem pemetaan 3D Visual SLAM monokuler yang dibangun dari segi kestabilan trajektori, kerapatan titik pemetaan, dan frame rate pemrosesan (FPS) pada rekaman video manuver ROV?"
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
    # I.3 Tujuan Penelitian
    # -------------------------------------------------------------------------
    add_heading_2("I.3  Tujuan Penelitian")
    add_para(
        "Tujuan yang ingin dicapai dalam pelaksanaan tugas akhir ini adalah:",
        space_after=4
    )
    objectives = [
        "Mengimplementasikan sistem fusi perangkat lunak Visual SLAM yang menghubungkan odometri 6-DoF ORB-SLAM3, model estimasi AI monokuler, dan pemetaan volumetrik RTAB-Map berbasis ROS Noetic.",
        "Menerapkan matriks transformasi ortogonal R_align dan mekanisme movement-based gating untuk memastikan awan titik 3D terbentang mengikuti jalur lintasan kamera dan tidak menumpuk di satu posisi.",
        "Menghasilkan model peta 3D padat bawah air bertekstur warna asli dalam format standar .PLY untuk visualisasi inspeksi struktur digital twin.",
        "Mengevaluasi kinerja pemetaan sistem Visual SLAM melalui pengujian kecepatan pemrosesan (FPS), analisis kerapatan titik (point cloud density), dan kelurusan trajektori pada dataset video ROV aktual."
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
        "Batasan masalah dalam penelitian tugas akhir ini ditetapkan sebagai berikut:",
        space_after=4
    )
    limits = [
        "Sensor akuisisi visual yang digunakan adalah satu unit kamera monokuler standar bawaan ROV (resolusi 640x480 piksel, rasio 4:3, format streaming citra digital).",
        "Wahana ROV berperan sebagai platform uji pembawa sensor kamera, dan penelitian difokuskan pada rekayasa perangkat lunak sistem pemetaan 3D Visual SLAM.",
        "Pengujian pemetaan dilakukan menggunakan rekaman data video manuver ROV di lingkungan tangki air/kolam uji terukur dengan kondisi pencahayaan buatan.",
        "Model estimasi spasial AI menggunakan arsitektur MiDaS DPT (Small ONNX) yang telah dioptimalkan untuk inferensi cepat pada komputasi PC/laptop."
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
        "Manfaat yang diharapkan dari hasil penelitian tugas akhir ini antara lain:",
        space_after=4
    )
    benefits = [
        "Bagi Operasional ROV Industri Maritim: Memberikan alternatif sistem pemetaan 3D berbiaya rendah (low-cost) yang dapat langsung diimplementasikan pada ROV kamera monokuler tanpa memerlukan sensor sonar 3D atau laser mahal.",
        "Bagi Operator Inspeksi Bawah Air: Meningkatkan kesadaran situasional (situational awareness) operator melalui tampilan rekonstruksi 3D objek lingkungan sekitar, sehingga mengurangi risiko tabrakan saat bertugas.",
        "Bagi Pengembangan Akademik: Menyumbangkan solusi integrasi praktis antara Geometric Visual SLAM dengan Deep Learning yang siap diaplikasikan pada wahana robotika di lingkungan tanpa GPS."
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
    # I.6 Rencana Pengambilan Data dan Prosedur Pengujian Praktis
    # -------------------------------------------------------------------------
    add_heading_2("I.6  Rencana Pengambilan Data dan Prosedur Pengujian Praktis")
    add_para(
        "Agar penyusunan tugas akhir dapat diselesaikan dengan cepat dan terukur, prosedur pengambilan data dan pengujian dirancang secara praktis sebagai berikut:",
        space_after=6
    )

    p_step1 = doc.add_paragraph()
    p_step1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_step1.paragraph_format.space_after = Pt(4)
    p_step1.paragraph_format.line_spacing = 1.5
    r_s1 = p_step1.add_run("1. Kemudahan Pengambilan Data (Video Dataset): ")
    r_s1.bold = True
    p_step1.add_run("Pengambilan data dilakukan dengan merekam video pergerakan ROV (format MP4 durasi 1–3 menit) saat bermanuver mengelilingi objek terukur di kolam atau tangki uji. Data video ini menjadi dataset permanen yang dapat diuji berulang kali secara repeatable dan aman tanpa harus selalu menurunkan robot ke air.")

    p_step2 = doc.add_paragraph()
    p_step2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_step2.paragraph_format.space_after = Pt(4)
    p_step2.paragraph_format.line_spacing = 1.5
    r_s2 = p_step2.add_run("2. Kemudahan Pengolahan Data (Automated ROS Script): ")
    r_s2.bold = True
    p_step2.add_run("Pengolahan data dijalankan secara terotomatisasi melalui script ROS launch. Sistem langsung memproses video, menampilkan visualisasi 3D real-time di RViz, dan secara otomatis mengekspor hasil rekonstruksi ke file .PLY.")

    p_step3 = doc.add_paragraph()
    p_step3.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_step3.paragraph_format.space_after = Pt(4)
    p_step3.paragraph_format.line_spacing = 1.5
    r_s3 = p_step3.add_run("3. Parameter Pengujian untuk Bab IV: ")
    r_s3.bold = True
    p_step3.add_run("Pengujian Bab IV ditargetkan pada 3 metrik yang jelas dan mudah diukur:\n"
                  "   a. Kecepatan Komputasi (FPS): Mengukur rata-rata frame rate pemrosesan (mencapai 15–20 FPS real-time).\n"
                  "   b. Kerapatan Titik Peta (Point Cloud Density): Membandingkan jumlah titik peta sparse ORB-SLAM3 (~3.000 titik) terhadap peta padat hasil fusi (~150.000 titik).\n"
                  "   c. Kelurusan Trajektori: Menganalisis konsistensi lintasan kamera terhadap jalur manuver aktual.")

    # Break ke halaman Daftar Pustaka
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

    # Simpan dokumen
    out_path = r"c:\remote_ROV\Draf_TA_Latar_Belakang_Fadzkal.docx"
    alt_path = r"c:\remote_ROV\Draf_Proposal_Latar_Belakang_Fadzkal.docx"
    try:
        doc.save(out_path)
        print(f"[SUKSES] Dokumen Word berhasil dibuat: {out_path}")
    except PermissionError:
        doc.save(alt_path)
        print(f"[PERINGATAN] File sedang dibuka di Word. Disimpan ke nama baru: {alt_path}")

if __name__ == "__main__":
    create_document()
