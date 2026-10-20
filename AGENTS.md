# PANDUAN DAN ATURAN PROYEK TUGAS AKHIR (WORKSPACE RULES)
# =============================================================================
# Proyek: Fusi Dense Neural-SLAM untuk 3D Mapping & Digital Twin Bawah Air ROV
# Penulis: Fadzkal Luthfi Mayzanio (NIM: 223443033)
# Program: D4 Teknologi Rekayasa Informatika Industri (TRII)
# Jurusan: Teknik Otomasi Manufaktur dan Mekatronika (TOMM)
# Institusi: Politeknik Manufaktur Bandung (Polman Bandung), 2026
# =============================================================================

Dokumen ini berisi panduan, konvensi teknis, standar format penulisan, dan aturan arsitektur yang WAJIB ditaati oleh AI Agent di setiap sesi percakapan untuk proyek ini.

---

## 1. Identitas Penulis dan Institusi
Setiap dokumen akademik, pengesahan, atau laporan teknis harus selalu menggunakan data resmi berikut:
- **Nama Mahasiswa**: Fadzkal Luthfi Mayzanio
- **NIM**: 223443033
- **Program Studi**: D4 Teknologi Rekayasa Informatika Industri
- **Jurusan**: Teknik Otomasi Manufaktur dan Mekatronika
- **Institusi**: Politeknik Manufaktur Bandung (Polman Bandung)
- **Tahun Akademik**: 2026

---

## 2. Judul dan Fokus Riset Utama
- **Judul Resmi Tugas Akhir**:
  > **RANCANG BANGUN SISTEM FUSI DENSE NEURAL-SLAM: INTEGRASI PELACAKAN 6-DOF ORB-SLAM3, ESTIMASI KEDALAMAN AI MONOKULER, DAN RTAB-MAP DENGAN ESTIMASI PERMUKAAN 2.5D PADA REMOTELY OPERATED VEHICLE (ROV) UNTUK REKONSTRUKSI 3D MAPPING BAWAH AIR**

- **Fokus Utama**:
  Riset ini secara eksplisit berorientasi pada **Dense 3D Volumetric Mapping dan Rekonstruksi Digital Twin Bawah Air**. Metode Visual SLAM *sparse* murni (seperti ORB-SLAM3) tidak memadai untuk deteksi rintangan dan inspeksi struktur; oleh karena itu, fusi dengan model estimasi kedalaman AI rapat (*dense neural depth*), penyelarasan koordinat ortogonal $\mathbf{R}_{align}$, dan engine pemetaan volumetrik 3D OctoMap adalah inti inovasi proyek ini.

---

## 3. Pilar Arsitektur Sistem Fusi (4-Layer Modular)
1. **Layer 1: Sensor & Video Streaming Acquisition**:
   - Kamera monokuler ROV (sensor CMOS 1/2.7", FOV 80°, 640x480 piksel, format streaming MJPEG over HTTP latensi < 80 ms).
   - Sensor altimeter akustik jarak dasar laut: Blue Robotics Ping1D Sonar (115 kHz, Time-of-Flight).
   - Sensor tekanan hidrostatis kedalaman absolut: Bar30 High-Resolution Depth Sensor (piezo-resistif I2C).
2. **Layer 2: 6-DoF Tracking Engine (ORB-SLAM3)**:
   - Pelacak pose 6-DoF kamera $\mathbf{T}_{w,c} \in SE(3)$ berbasis ekstraksi fitur FAST, deskriptor ORB 256-bit, optimasi *Bundle Adjustment*, preintegrasi inersia pada manifold $SO(3)$, dan sistem multi-map Atlas.
3. **Layer 3: Dense Neural Depth Inference (MiDaS DPT)**:
   - Inferensi kedalaman kontinu menggunakan model MiDaS DPT berbasis FP16 GPU CUDA.
   - Formulasi pemetaan hiperbolik disparitas ke kedalaman fisik metrik:
     $$Z(d_{norm}) = \frac{1}{2.6349 \cdot d_{norm} + 0.2222}$$
     dengan rentang inspeksi fisik $z_{near} = 0.35\text{ m}$ hingga $z_{far} = 4.50\text{ m}$.
   - Filter pemotongan batas dalam (*Inner Boundary Masking*) 5% margin untuk mengeliminasi distorsi radial kubah kamera dan efek sayap kipas (*fan-wing artifacts*).
   - Perataan temporal warna *Exponential Moving Average* (EMA): $C_t = 0.65 \cdot C_{t-1} + 0.35 \cdot C_{frame}$.
4. **Layer 4: 3D Volumetric Engine, 2.5D Surface, & Digital Twin (RTAB-Map, RViz, Three.js)**:
   - Transformasi koordinat optis (RDF) ke navigasi robotika (ROS REP 103 ENU: $X$ maju, $Y$ kiri, $Z$ atas) melalui matriks rotasi ortogonal $\mathbf{R}_{align}$:
     $$\mathbf{R}_{align} = \begin{bmatrix} 0 & 0 & 1 \\ -1 & 0 & 0 \\ 0 & -1 & 0 \end{bmatrix}$$
   - Pemetaan volumetrik 3D OctoMap dengan resolusi voxel $0.05\text{ m}$ dan filter *Statistical Outlier Removal* (SOR, $k=30, \sigma=1.0$) untuk membersihkan hamburan partikel debu air (*marine snow*).
   - Estimasi bidang dasar 2.5D berbasis RANSAC (diadaptasi dari riset EgoExo++ pada BlueROV2) sebagai datum keselamatan navigasi anti-tabrakan dasar laut.
   - Penguncian skala metrik fisik $\lambda^*$ melalui kuadrat terkecil (*least-squares scale anchoring*) memadukan translasi vertikal SLAM, tekanan Bar30, dan sonar Ping1D.
   - Ekspor model 3D metrik (.PLY & .OBJ) dan visualisasi ganda: native ROS RViz dengan *wireframe* piramida frustum kamera 8-rusuk dinamis, serta viewer interaktif Three.js WebGL.

---

## 4. Literatur Acuan Wajib
Setiap analisis komparatif dan tinjauan teori harus mengacu secara mendalam pada 3 paper utama yang tersimpan di workspace:
1. **ORB-SLAM3 / ORB-SLAM2**:
   - Campos et al. (IEEE T-RO 2021) & Mur-Artal & Tardós (IEEE T-RO 2017) (`10125478.pdf` / `1610.06475v2.pdf`).
2. **EgoExo++**:
   - Abdullah et al. (2024), *"EgoExo++: 2.5D Ground Surface Estimation for Underwater ROV Teleoperation"* (`2407.00848v7.pdf`), uji coba lapangan BlueROV2 di sistem gua Peacock Springs Florida.
3. **Loopy-SLAM**:
   - Liso et al. (CVPR 2024), *"Loopy-SLAM: Dense Neural SLAM with Loop Closures"* (`Liso_Loopy-SLAM_Dense_Neural_SLAM_with_Loop_Closures_CVPR_2024_paper.pdf`), rekonstruksi titik-titik saraf padat bebas *drift* dengan *deformation graph*.

---

## 5. Standar Format Dokumen & Skrip Generator
- **Format Baku Polman Bandung**:
  - Ukuran Kertas: A4 ($21.0 \times 29.7\text{ cm}$).
  - Margin: Kiri $4.0\text{ cm}$, Atas $3.0\text{ cm}$, Kanan $3.0\text{ cm}$, Bawah $3.0\text{ cm}$.
  - Tipografi: Times New Roman, ukuran 12 pt, spasi 1.5 baris, perataan rata kanan-kiri (*Justify*).
  - Penomoran: Halaman awal angka Romawi kecil (i, ii, iii, ...), bab utama angka Arab (I-1, II-1, ...).
- **Aset Gambar**:
  - Disimpan di folder `gambar_ta/`. Wajib berlatar belakang putih murni (`#FFFFFF`) layaknya publikasi jurnal ilmiah atau tangkapan resolusi tinggi dari paper acuan.
  - Setiap gambar wajib disertai nomor gambar, judul resmi, sumber sitasi, dan paragraf **Catatan Analisis Gambar** yang mengulas aspek teknis dan relevansi algoritmanya.
- **Skrip Generator Master**:
  - `build_mega_thesis_docx.py` $\to$ menghasilkan `TUGAS_AKHIR_FADZKAL_LUTHFI_MAYZANIO.docx`.
  - `build_mega_thesis_md.py` $\to$ menghasilkan `TUGAS_AKHIR_FADZKAL_LUTHFI_MAYZANIO.md`.
  - Jika ada pembaruan data pengujian (misal: FPS, tabel ATE RMSE, atau parameter baru), perbarui selalu kedua skrip ini agar dokumen Word dan Markdown tetap sinkron 100%.
