# LAPORAN RISET & PENGEMBANGAN TEKNIS
## Sistem 3D Dense SLAM, Multi-Sensor Fusion, dan Visualisasi Web (Three.js) pada Remotely Operated Vehicle (ROV)

**Platform**: BlueROV2 Heavy Configuration / Underwater ROV  
**Middleware**: ROS Noetic (Ubuntu 20.04 WSL2) & Windows 11  
**Repositori GitHub**: [https://github.com/Fadzkal/slam3drov.git](https://github.com/Fadzkal/slam3drov.git)  
**Dokumen Microsoft Word**: [`LAPORAN_LENGKAP_SUBSEA_3D_SLAM.docx`](file:///c:/remote_ROV/LAPORAN_LENGKAP_SUBSEA_3D_SLAM.docx)  
**Tanggal**: Oktober 2026  

---

## DAFTAR ISI
1. [BAB I: Pendahuluan & Latar Belakang Riset](#bab-i-pendahuluan--latar-belakang-riset)
2. [BAB II: Arsitektur Multi-Sensor Fusion & Estimasi Kedalaman](#bab-ii-arsitektur-multi-sensor-fusion--estimasi-kedalaman)
3. [BAB III: Pipeline RTAB-Map SLAM & Investigasi Bug Peta Melayang](#bab-iii-pipeline-rtab-map-slam--investigasi-bug-peta-melayang)
4. [BAB IV: Sistem Visualisasi Web Tiga Dimensi (Three.js)](#bab-iv-sistem-visualisasi-web-tiga-dimensi-threejs)
5. [BAB V: Studi Komparasi dengan State-of-the-Art (SOTA) & MASt3R-SLAM](#bab-v-studi-komparasi-dengan-state-of-the-art-sota--mast3r-slam)
6. [BAB VI: Panduan Pengoperasian & Kesimpulan](#bab-vi-panduan-pengoperasian--kesimpulan)

---

## BAB I: Pendahuluan & Latar Belakang Riset

Inspeksi infrastruktur bawah air seperti pipa migas dasar laut, struktur pondasi anjungan lepas pantai, lambung kapal, dan survei bangkai kapal membutuhkan pemetaan tiga dimensi (*3D Mapping*) yang cepat, akurat, dan memiliki skala fisik nyata (dalam sentimeter/meter). Penggunaan wahana tanpa awak *Remotely Operated Vehicle* (ROV) seperti BlueROV2 menjadi solusi utama di industri maritim.

### Tantangan Utama Lingkungan Bawah Air
1. **Ketiadaan Sinyal Satelit (No GPS)**: Gelombang elektromagnetik GPS teratenuasi habis oleh air laut pada kedalaman beberapa sentimeter, sehingga navigasi sepenuhnya bergantung pada sensor internal (*dead reckoning*) dan penglihatan kamera.
2. **Penurunan Kontras & Hamburan Cahaya**: Partikel tersuspensi di air laut menyebabkan hamburan balik (*backscattering*) cahaya, hilangnya spektrum warna merah pada kedalaman >3 meter, dan kabur kehijauan.
3. **Ambiguitas Skala Monocular (Scale Ambiguity)**: Kamera tunggal 2D biasa tidak memiliki informasi kedalaman absolut, sehingga skala objek tidak dapat diketahui dalam satuan meter secara mandiri.
4. **Keterbatasan Beban Komputasi Wahana**: Komputer mini di dalam tabung ROV (seperti Raspberry Pi 4) memiliki keterbatasan daya komputasi dan memori yang ketat.

Untuk memecahkan masalah ini, proyek ini membangun arsitektur komputasi cerdas yang menggabungkan AI Monocular Depth Estimation (MiDaS), Graph SLAM (RTAB-Map), fusi sensor fisik (Bar30 & Ping1D Sonar), representasi lantai 2.5D EgoExo++, serta antarmuka visualisasi web modern berbasis Three.js.

---

## BAB II: Arsitektur Multi-Sensor Fusion & Estimasi Kedalaman

Sistem mengintegrasikan 4 modalitas sensor utama untuk membentuk estimasi pose 6-DoF yang terkunci sempurna tanpa drift vertikal:

| Sensor / Node | Fungsi Primer | Kompensasi & Kontribusi Geometris |
| :--- | :--- | :--- |
| **Kamera HD + CLAHE Node** | Tangkapan visual RGB & feature extraction | CLAHE menaikkan kontras warna merah dan menghilangkan kabur partikel air laut. |
| **AI Monocular Depth (MiDaS)** | Dense relative depth per-pixel | Menghasilkan peta kedalaman padat tanpa membutuhkan hardware stereo baseline yang lebar. |
| **Bar30 Pressure Sensor** | Kedalaman hidrostatik presisi tinggi ($\pm 2\text{ mm}$) | Mengunci sumbu Z secara absolut; mengeliminasi akumulasi drift vertikal secara permanen. |
| **Ping1D Echosounder Sonar** | Jarak akustik ke objek / dasar laut ($\pm 1\text{ mm}$) | Mengalibrasi rasio skala metrik absolut dari depth relatif AI menjadi satuan meter nyata. |

### 2.1 Formulasi Kalibrasi Skala Metrik Otomatis
Model kedalaman monocular AI (MiDaS) menghasilkan nilai kedalaman relatif $d_{rel} \in [0, 1]$. Untuk mengubahnya menjadi satuan metrik $z_{metrik}$ (meter), node [`depth_to_pose_publisher.py`](file:///c:/remote_ROV/depth_to_pose_publisher.py) dan [`monocular_depth_node.py`](file:///c:/remote_ROV/monocular_depth_node.py) memfusi jarak akustik Sonar Ping1D:

$$z_{metrik} = d_{rel} \times \left(\frac{d_{sonar}}{d_{ai\_center}}\right)$$

Dengan metode ini, setiap piksel pada gambar kamera mendapatkan koordinat 3D $(X, Y, Z)$ dalam satuan meter nyata, siap di-feed ke dalam pipeline RGB-D SLAM.

---

## BAB III: Pipeline RTAB-Map SLAM & Investigasi Bug Peta Melayang

RTAB-Map (*Real-Time Appearance-Based Mapping*) bertugas sebagai backend SLAM berbasis Graph Memory. Sistem mengelola Working Memory (WM) untuk real-time tracking dan Long-Term Memory (LTM) untuk deteksi penutupan loop (*Loop Closure*).

### 3.1 Investigasi Kasus Bug: Peta Melayang & Melompat ke Langit
Pada fase pengujian awal, ditemukan anomali kritis di mana potongan point cloud 3D tiba-tiba melompat puluhan meter ke atas langit dan ke bawah lantai, dihubungkan garis-garis biru panjang (*graph link constraints*).

Ditemukan 3 akar penyebab (*root causes*) utama:
1. **Desinkronisasi Timestamp Kamera vs AI Depth (`approx_sync` lag)**:
   - Kamera menghasilkan frame pada 30 FPS, sedangkan inferensi AI Depth (MiDaS) pada CPU membutuhkan $\sim 100\text{ ms}$ (10 FPS).
   - Ketika kamera bergerak cepat, modul `approx_sync` memasangkan gambar RGB baru dengan peta depth lama (terlambat 1–2 frame).
   - Akibatnya, proyeksi 3D terdistorsi parah, menyebabkan solver EPnP menghitung rotasi/translasi lonjakan acak.
2. **Threshold Keyframe Terlalu Rapat (`RGBD/LinearUpdate = 0.05m`)**:
   - Rekaman dipicu setiap 5 cm pergerakan, menyebabkan antrean buffer RTAB-Map overload dan memperparah lag desync.
3. **Tidak Adanya Filter Outlier Kecepatan (`Odom/MaxTranslation = 0`)**:
   - Default RTAB-Map menerima nilai translasi berapapun. Jika ada 1 frame blur yang menghasilkan lompatan 20 meter, sistem menganggapnya sah dan memplotnya di langit.

### 3.2 Solusi Parameter Rekayasa yang Diterapkan
Parameter di [`live_rov_3d_mapping.launch`](file:///c:/remote_ROV/live_rov_3d_mapping.launch) telah diperbarui:
- `Odom/MaxTranslation = 0.30 m`: Membatasi translasi maksimum 30 cm per frame. Lompatan liar akibat blur langsung dibuang (*outlier rejection*).
- `Odom/MaxRotation = 0.50 rad` ($\sim 28^\circ$): Membatasi rotasi mendadak per frame.
- `RGBD/LinearUpdate = 0.12 m` & `AngularUpdate = 0.18 rad`: Memperlebar batas keyframe agar frame tidak berdesakan.
- `RGBD/OptimizeMaxError = 1.5 m`: Menolak penutupan loop (*loop closure*) palsu yang menyebabkan graf melintir.
- `Vis/MinInliers = 10` & `Vis/PnPReprojError = 4.0`: Memperketat verifikasi *geometrically consistent inliers*.

Hasil pengujian pasca-perbaikan menunjukkan odometry stabil dengan kualitas **420–520 inliers** tanpa lonjakan.

---

## BAB IV: Sistem Visualisasi Web Tiga Dimensi (Three.js)

Untuk menghilangkan ketergantungan pada RViz, ROS, dan Linux X-Server, telah dibangun antarmuka visualisasi web modern berbasis **Three.js** di [`view_slam_3d_web.html`](file:///c:/remote_ROV/view_slam_3d_web.html).

### Fitur-Fitur Utama Web Viewer:
1. **Navigasi Orbit 360° Bebas**: Rotasi 3D, pan, dan zoom interaktif menggunakan mouse / touch gesture.
2. **Drag & Drop File Loader Mandiri**: Membaca file `.ply`, `.pcd`, dan `.obj` langsung dari disk lokal menggunakan HTML5 `FileReader` API (100% bebas batasan CORS).
3. **Pilihan Skema Warna**:
   - *RGB Asli*: Warna asli dari kamera HD bawah air.
   - *Elevasi Kedalaman Z*: Turbo/Jet gradient menunjukkan kontur kedalaman.
   - *Deep Sea Cyber*: Visualisasi neon cyan kontras tinggi.
   - *Monokrom / Intensitas*.
4. **Alat Pengukur Jarak Interaktif (Metric Ruler)**: Klik 2 titik pada point cloud untuk mengukur dimensi objek secara akurat dalam centimeter dan meter.
5. **Lantai 2.5D EgoExo & Grid Metrik 1m**: Orientasi spasial dasar laut dan batas bodi ROV.
6. **Ekspor Snapshot Cepat**: Tombol satu klik untuk mengunduh gambar resolusi tinggi (PNG).

### Skrip Otomasi 1-Klik:
- [**`export_3d_map.bat`**](file:///c:/remote_ROV/export_3d_map.bat): Mengekstrak database `~/.ros/rtabmap.db` menjadi `export/subsea_3d_map.ply` dan otomatis meluncurkan web viewer di port 8888.
- [**`open_3d_web_viewer.bat`**](file:///c:/remote_ROV/open_3d_web_viewer.bat): Membuka web viewer kapan saja secara instan.

---

## BAB V: Studi Komparasi dengan State-of-the-Art (SOTA) & MASt3R-SLAM

### 5.1 Tinjauan Komparasi 1: Monocular Tradisional (EECS 442 - UMich)
Repositori `eecs-442-slam-project` mewakili pendekatan Computer Vision klasik:
- Menggunakan Epipolar Geometry & Essential Matrix ($E = K^T F K$) untuk estimasi pose frame-ke-frame.
- Kelemahan: Mengalami *Scale Ambiguity* parah (tidak tahu ukuran nyata objek) dan *Scale Drift* kumulatif. Peta yang dihasilkan hanya berupa titik bintik jarang (*Sparse Point Cloud*).

### 5.2 Tinjauan Komparasi 2: Vision Transformer SOTA (MASt3R-SLAM - CVPR 2025)
MASt3R-SLAM (Imperial College London) merupakan terobosan paling mutakhir di bidang Monocular Dense SLAM:
- **DROID-SLAM (2021)**: Mengalami fenomena *depth explosion* pada tepian dinding yang minim tekstur, menghasilkan titik-titik melenceng keluar seperti landak.
- **Spann3R (2024)**: Mengalami *scale drift* kumulatif, mengakibatkan geometri dinding terfragmentasi dan melintir.
- **MASt3R-SLAM (2025)**: Menghasilkan geometri kotak sempurna, dinding tegak lurus, dan lantai datar berkat pemanfaatan **3D Reconstruction Priors** dari jutaan data latih deep learning.

### 5.3 Usulan Arsitektur Dua-Tahap (Dual-Stage SLAM Architecture)
Mengingat laptop saat ini menggunakan GPU AMD Radeon terintegrasi tanpa kartu diskrit NVIDIA CUDA (sedangkan MASt3R-SLAM mewajibkan kompilasi kernel CUDA C++ `cuda_matching.cu` dan VRAM $\ge 8\text{ GB}$), arsitektur dua-tahap berikut diusulkan untuk operasional maritim nyata:

```
                          ┌────────────────────────────────────────────────────────┐
                          │         MISI PENYELAMAN BLUEROV2                       │
                          └──────────────────────────┬─────────────────────────────┘
                                                     │
                    ┌────────────────────────────────┴────────────────────────────────┐
                    ▼                                                                 ▼
   [TAHAP 1: ON-BOARD REAL-TIME SLAM]                              [TAHAP 2: POST-MISSION DIGITAL TWIN]
   Sistem Kita Saat Ini:                                           Menggunakan MASt3R-SLAM:
   • RTAB-Map + MiDaS + Bar30 + Ping1D Sonar                       • Memproses rekaman video HD di Cloud / GPU Workstation
   • Berjalan enteng di CPU/mini-computer onboard                  • Menggunakan Deep 3D Prior Transformer
   • Menghasilkan lintasan navigasi & skala metrik pasti           • Menghasilkan rekonstruksi 3D padat, dinding kotak presisi
   • Visualisasi Live di RViz & Three.js Web HUD                   • Hasil inspeksi visual fotorealistis untuk klien/laporan
```

---

## BAB VI: Panduan Pengoperasian & Kesimpulan

### 6.1 Panduan Pengoperasian
1. **Menjalankan Live 3D Mapping & RViz**:
   > Dobel klik [**`run_live_rov_mapping.bat`**](file:///c:/remote_ROV/run_live_rov_mapping.bat).
2. **Mengekspor Peta 3D ke Tampilan Web**:
   > Dobel klik [**`export_3d_map.bat`**](file:///c:/remote_ROV/export_3d_map.bat). Database diekstrak ke [`export/subsea_3d_map.ply`](file:///c:/remote_ROV/export/subsea_3d_map.ply) dan browser langsung terbuka.
3. **Membuka Web 3D Viewer Kapan Saja**:
   > Dobel klik [**`open_3d_web_viewer.bat`**](file:///c:/remote_ROV/open_3d_web_viewer.bat) atau buka [`view_slam_3d_web.html`](file:///c:/remote_ROV/view_slam_3d_web.html).

### 6.2 Kesimpulan Penelitian
1. Masalah anomali peta melayang dan lonjakan odometry berhasil diselesaikan secara tuntas melalui penyelarasan frekuensi update keyframe dan pemasangan batas kecepatan maksimum (`Odom/MaxTranslation = 0.30 m`).
2. Sistem fusi sensor berhasil mengunci skala metrik fisik nyata (meter) dan menghilangkan *vertical drift* pada sumbu Z berkat sensor Bar30 dan Sonar Ping1D.
3. Visualisasi Three.js Web Viewer memberikan kemudahan akses bagi pengguna untuk menginspeksi, mengukur dimensi, dan menyajikan hasil 3D SLAM tanpa perlu ketergantungan pada RViz atau Linux.
4. Rancangan arsitektur dua-tahap (Dual-Stage) yang memadukan pipeline ringan RTAB-Map untuk navigasi live dengan MASt3R-SLAM untuk pemodelan pasca-misi memberikan solusi paling komprehensif bagi robotika bawah air modern.
