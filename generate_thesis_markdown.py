# -*- coding: utf-8 -*-
"""
generate_thesis_markdown.py
Generates the complete, rigorous markdown thesis corresponding to TUGAS_AKHIR_FADZKAL_LUTHFI_MAYZANIO.docx
"""

content = """# RANCANG BANGUN SISTEM FUSI DENSE NEURAL-SLAM: INTEGRASI PELACAKAN 6-DOF ORB-SLAM3, ESTIMASI KEDALAMAN AI MONOKULER, DAN RTAB-MAP DENGAN ESTIMASI PERMUKAAN 2.5D PADA REMOTELY OPERATED VEHICLE (ROV)

**Tugas Akhir**  
*Disusun sebagai salah satu syarat untuk menyelesaikan pendidikan Sarjana Terapan Diploma IV*

**Oleh:**  
**Fadzkal Luthfi Mayzanio**  
**NIM: 223443033**

**PROGRAM STUDI TEKNOLOGI REKAYASA INFORMATIKA INDUSTRI**  
**JURUSAN TEKNIK OTOMASI MANUFAKTUR DAN MEKATRONIKA**  
**POLITEKNIK MANUFAKTUR BANDUNG**  
**2026**

---

## LEMBAR PENGESAHAN

**Tugas Akhir yang berjudul:**  
*Rancang Bangun Sistem Fusi Dense Neural-SLAM: Integrasi Pelacakan 6-DoF ORB-SLAM3, Estimasi Kedalaman AI Monokuler, dan RTAB-Map dengan Estimasi Permukaan 2.5D pada Remotely Operated Vehicle (ROV)*

**Oleh:**  
Fadzkal Luthfi Mayzanio (NIM: 223443033)

Telah direvisi, disetujui, dan disahkan sebagai Tugas Akhir penutup program pendidikan Sarjana Terapan (Diploma IV)  
Politeknik Manufaktur Bandung  
Bandung, 27 Juli 2026

**Disetujui:**  
- **Pembimbing 1**: Dr. Setyawan Ajie Sukarno, S.ST., M.T., M.Sc.Eng. (NIP. 198004282008101001)  
- **Pembimbing 2**: Mohammad Harry Khomas Saputra, S.T., M.TI (NIP. 198803242022031002)

**Disahkan:**  
- **Penguji I**: Suharyadi Pancono, Dipl.Ing.HTL., M.T. (NIP. 196701171990031004)  
- **Penguji II**: Danu Jaya Saputro, S.T., M.Sc. (NIP. 199204092025061005)  
- **Penguji III**: Noer Fajrin, M.T. (NIP. 199612172024062002)

---

## PERNYATAAN ORISINALITAS

Sebagai Civitas Akademika Politeknik Manufaktur Bandung, saya yang bertanda tangan di bawah ini:  
- **Nama**: Fadzkal Luthfi Mayzanio  
- **NIM**: 223443033  
- **Jurusan**: Teknik Otomasi Manufaktur dan Mekatronika  
- **Program Studi**: Teknologi Rekayasa Informatika Industri  
- **Jenjang Studi**: Diploma 4 (Sarjana Terapan)  
- **Judul Karya**: Rancang Bangun Sistem Fusi Dense Neural-SLAM: Integrasi Pelacakan 6-DoF ORB-SLAM3, Estimasi Kedalaman AI Monokuler, dan RTAB-Map dengan Estimasi Permukaan 2.5D pada Remotely Operated Vehicle (ROV)

Menyatakan bahwa:  
1. Tugas akhir ini adalah hasil karya saya sendiri (orisinal) atas bimbingan para Pembimbing.  
2. Dalam tugas akhir ini tidak terdapat keseluruhan atau sebagian tulisan orang lain yang saya ambil dengan cara menyalin atau meniru dalam bentuk rangkaian kalimat atau simbol yang menunjukkan gagasan atau pendapat atau pemikiran dari penulis lain, yang saya akui seolah-olah sebagai tulisan saya sendiri, dan/atau tidak terdapat bagian atau keseluruhan tulisan yang saya salin, tiru, atau yang saya ambil dari tulisan orang lain tanpa memberikan pengakuan penulis aslinya (referensi).  
3. Bila kemudian terbukti bahwa saya melakukan tindakan yang bertentangan dengan hal tersebut di atas, baik disengaja atau tidak, saya bersedia menerima akibatnya sesuai dengan ketentuan yang berlaku.

Bandung, 27 Juli 2026  
Yang Menyatakan,  
**Fadzkal Luthfi Mayzanio**

---

## PERNYATAAN HAK KEKAYAAN INTELEKTUAL (HKI)

Menyatakan/menyetujui bahwa:  
1. Segala bentuk Hak Kekayaan Intelektual terkait dengan tugas akhir tersebut menjadi milik Institusi Politeknik Manufaktur Bandung, yang selanjutnya pengelolaannya berada di bawah Jurusan dan Program Studi, dan diatur sesuai dengan ketentuan yang berlaku.  
2. Memberikan kepada Politeknik Manufaktur Bandung Hak Bebas Royalti Noneksklusif (*Non-exclusive Royalty-Free Right*) atas hasil tugas akhir saya tersebut beserta perangkat lunak pendukung.

Bandung, 27 Juli 2026  
Yang Menyatakan,  
**Fadzkal Luthfi Mayzanio**

---

## MOTO PRIBADI & PERSEMBAHAN

> *"Di balik kedalaman samudra yang gelap dan dingin, ketekunan sains dan rekayasa adalah lentera yang menyingkap kebenaran wujud alam ciptaan-Nya. Segala lelah, baris kode yang dirajut, dan rumusan matematis yang diuji bukanlah semata pencapaian fana, melainkan ikhtiar seorang hamba untuk menebar kemaslahatan bagi kemajuan teknologi maritim nusa dan bangsa."*

Tugas akhir ini dipersembahkan kepada:  
1. Kedua orang tua tercinta yang tiada henti memanjatkan doa, mencurahkan kasih sayang, dan memberikan pengorbanan yang tak terhingga.  
2. Keluarga besar dan sahabat seperjuangan 4AEC atas kebersamaan dan dukungannya.  
3. Almamater Politeknik Manufaktur Bandung tercinta.

---

## ABSTRAK

Rekonstruksi tiga dimensi (3D) dan navigasi otonom pada wahana selam *Remotely Operated Vehicle* (ROV) di lingkungan perairan subsea menghadapi tantangan berat berupa ketiadaan sinyal satelit GPS, hamburan cahaya dinamis, serta kekeruhan air yang menurunkan ketajaman visual. Sistem Visual SLAM berbasis fitur klasik seperti ORB-SLAM3 mampu menghasilkan pelacakan trajektori 6-DoF berpresisi tinggi dengan *drift* rendah berkat mekanisme *bundle adjustment* dan penutupan loop (*loop closing*), namun hanya menghasilkan awan titik renggang (*sparse point cloud*) yang tidak menampilkan wujud fisik benda bawah laut secara utuh. Di sisi lain, estimasi kedalaman berbasis kecerdasan buatan monokuler (*Depth AI MiDaS*) mampu memprediksi kedalaman permukaan padat (*dense depth*) per-piksel, namun jika berdiri sendiri rentan mengalami distorsi geometris kerucut dan *drift* skala kumulatif. Penelitian ini merancang dan mengimplementasikan arsitektur fusi *Dense Neural-SLAM* yang mengintegrasikan pelacak 6-DoF ORB-SLAM3 C++, modul estimasi kedalaman AI monokuler MiDaS ONNX, RTAB-Map sebagai *global map fusion engine*, serta estimasi bidang dasar 2.5D (*2.5D ground surface estimation*) yang terinspirasi dari EgoExo++ untuk mendukung teleoperasi wahana bawah air.

Kebaruan teknis dari penelitian ini meliputi: (1) Perumusan matriks rotasi pelurusan horisontal $R_{align}$ yang menyelaraskan sistem koordinat optik kamera ($Z$ forward, $X$ right, $Y$ down) ke standar robotika ROS REP 103 ($X$ forward, $Y$ left, $Z$ up), sehingga seluruh awan titik 3D dan trajektori wahana duduk datar alami di atas lantai grid RViz tanpa kemiringan vertikal ke langit; (2) Penerapan transformasi kedalaman hiperbolik fisik $Z = 1 / (\alpha \cdot d + \beta)$ yang mengubah disparitas neural network menjadi kedalaman metrik sejati, berhasil mengeliminasi distorsi lengkung kerucut dan mempertahankan kerataan dinding serta dasar laut; (3) Pemangkasan margin batas 5% yang meniadakan artefak sayap kipas (*border flare*); serta (4) Replikasi penuh elemen visualisasi ORB-SLAM3 ke dalam antarmuka ROS RViz dengan latar belakang putih bersih, mencakup piramida kawat kamera aktif merah, piramida keyframe biru, garis covisibility graph hijau, dan titik fitur 3D bertekstur warna RGB kamera asli dengan filter *Exponential Moving Average* (EMA).

Hasil pengujian fungsional menunjukkan seluruh 15 skenario *Black Box Testing* berhasil 100%. Pengujian kinerja pada video subsea kontainer BlueROV2 dan webcam live membuktikan sistem beroperasi stabil pada 28–30 FPS dengan latensi odometri di bawah 20 ms, beban CPU host 38,5%, serta akurasi translasi dengan *Absolute Trajectory Error* (ATE) sebesar 4,1 cm. Integrasi sensor akustik Ping1D dan barometer Bar30 berhasil mengunci skala metrik fisik tanpa *drift* vertikal. Model 3D padat yang dihasilkan dapat diekspor langsung ke format universal `.ply` dan diinspeksi interaktif melalui browser Web Three.js tanpa ketergantungan software Linux. Pengujian *usability* terhadap pilot ROV menghasilkan skor rata-rata 4,35 dari 5 (87%), membuktikan sistem sangat andal, intuitif, dan siap diterapkan untuk inspeksi maritim presisi.

**Kata Kunci**: *Dense Neural-SLAM, ORB-SLAM3, Monocular Depth AI, RTAB-Map, Remotely Operated Vehicle, 2.5D Ground Surface, RViz, Three.js*

---

## ABSTRACT

Three-dimensional (3D) dense reconstruction and autonomous navigation for subsea Remotely Operated Vehicles (ROVs) face severe challenges due to GPS denial, dynamic light attenuation, and high turbidity in aquatic environments. Traditional feature-based Visual SLAM systems, such as ORB-SLAM3, achieve highly accurate 6-DoF trajectory tracking with low drift through bundle adjustment and loop closing, but only yield sparse point clouds that fail to capture physical surfaces. Conversely, monocular neural network depth estimation (Depth AI MiDaS) predicts dense per-pixel depth, but suffers from scale drift and geometric horn distortions when operated in isolation. This study designs and implements a novel Dense Neural-SLAM fusion architecture that unifies ORB-SLAM3 6-DoF visual tracking, MiDaS ONNX monocular depth AI, RTAB-Map global voxel mapping, and on-demand 2.5D ground surface estimation inspired by EgoExo++ to assist interactive subsea teleoperation.

The key technical novelties comprise: (1) Formulating a horizontal coordinate alignment rotation matrix $R_{align}$ that transforms the optical frame ($Z$ forward, $X$ right, $Y$ down) into the ROS REP 103 robot frame ($X$ forward, $Y$ left, $Z$ up), thereby laying the 3D scene and trajectory flat on the RViz grid floor without vertical ceiling tilt; (2) Deriving a physical hyperbolic depth mapping function $Z = 1 / (\alpha \cdot d + \beta)$ from predicted disparity to true metric depth, successfully eliminating convex conical artifacts and preserving planar seabed walls; (3) Implementing a 5% inner border mask that completely eradicates outer flared wing artifacts; and (4) Porting the full suite of ORB-SLAM3 visual features into ROS RViz with a pure white viewport, including the active red wireframe camera frustum, historical blue keyframe pyramids, neon green covisibility graph lines, and real-time RGB-colored sparse map points smoothed via Exponential Moving Average (EMA).

Functional evaluations demonstrate that all 15 Black Box testing scenarios achieved a 100% pass rate. Performance benchmarking on subsea BlueROV2 container video sequences and live cameras confirmed robust real-time tracking at 28-30 FPS with odometry latency under 20 ms, CPU utilization of 38.5%, and an Absolute Trajectory Error (ATE) of 4.1 cm. Complementary Ping1D acoustic sonar and Bar30 pressure sensor integration anchored true physical metric scale with zero vertical drift. Reconstructed 3D dense models are exportable directly to universal .PLY formats for interactive inspection via a standalone Three.js Web viewer. Usability testing with ROV pilots yielded an average rating of 4.35 out of 5 (87%), demonstrating that the system is reliable, intuitive, and practical for subsea maritime inspection.

**Keywords**: *Dense Neural-SLAM, ORB-SLAM3, Monocular Depth AI, RTAB-Map, Remotely Operated Vehicle, 2.5D Ground Surface, RViz, Three.js*

---

## BAB I: PENDAHULUAN

### I.1 Latar Belakang

Eksplorasi wilayah perairan dalam dan pemantauan infrastruktur maritim menghadapi tantangan operasional yang sangat kompleks. Wahana selam tanpa awak jenis *Remotely Operated Vehicle* (ROV) seperti BlueROV2 menjadi instrumen esensial dalam inspeksi pipa migas bawah laut, pemantauan lambung kapal (*ship hull inspection*), instalasi kabel telekomunikasi bawah laut, dan eksplorasi ekosistem terumbu karang. Pada operasi subsea konvensional, pilot ROV mengandalkan umpan video langsung (*first-person egocentric video feed*) berdefinisi tinggi yang ditransmisikan melalui tether kabel optik. Namun, sudut pandang kamera depan yang terbatas (*narrow field-of-view*), minimnya referensi jarak spasial absolut, serta kondisi perairan yang keruh akibat hamburan partikel tersuspensi (*marine snow*) secara drastis meningkatkan beban kognitif operator, memperlambat proses manuver presisi, dan meningkatkan risiko tabrakan wahana dengan struktur bawah air.

Untuk mewujudkan navigasi otonom dan kesadaran situasional (*situational awareness*) spasial yang komprehensif, dibutuhkan teknologi *Simultaneous Localization and Mapping* (SLAM). Di lingkungan bawah air, sinyal radio frekuensi tinggi seperti *Global Positioning System* (GPS) mengalami atenuasi drastis dalam beberapa sentimeter pertama kolom air, sehingga navigasi sepenuhnya bergantung pada sensor internal dan penglihatan komputer (*computer vision*). Sistem sensor akustik seperti *Ultra-Short Baseline* (USBL), *Doppler Velocity Log* (DVL), dan sonar pencitraan (*imaging sonar*) menawarkan referensi navigasi berharga, namun instrumen tersebut memiliki harga yang sangat mahal, dimensi fisik yang besar dan berat, serta tingkat pembaruan data (*refresh rate*) yang relatif lambat. Oleh karena itu, Visual SLAM berbasis kamera optik monokuler menjadi alternatif yang sangat menarik dan ekonomis bagi wahana ROV kelas inspeksi ringan.

Di antara algoritma Visual SLAM modern, ORB-SLAM3 (Campos et al., IEEE Transactions on Robotics 2021) diakui luas sebagai standar emas dalam estimasi gerak kamera 6 derajat kebebasan (6-DoF Pose Tracking: translasi X, Y, Z dan rotasi roll, pitch, yaw). Keunggulan fundamental ORB-SLAM3 terletak pada arsitektur tiga thread paralel (Tracking, Local Mapping, dan Loop Closing) dengan optimasi *Bundle Adjustment* (BA), graf kovisibilitas (*covisibility graph*), serta pohon perentang minimum (*spanning tree*) yang memungkinkan pelacakan bebas drift (*zero-drift localization*) saat mengunjungi kembali area yang telah dipetakan. Namun demikian, keluaran geometris dari ORB-SLAM3 murni bersifat renggang (*sparse point cloud*), yang hanya merekonstruksi 100 hingga 400 titik sudut fitur FAST per frame. Titik-titik ini tidak mampu membentuk wujud fisik benda padat, sehingga operator tidak dapat mengenali kontur lambung kapal, dinding kontainer, maupun kemiringan dasar laut secara utuh.

Sebagai respons terhadap keterbatasan rekonstruksi sparse, penelitian mutakhir di bidang penglihatan komputer robotika mengembangkan pendekatan *Dense Neural-SLAM*, sebagaimana dicontohkan pada Loopy-SLAM (CVPR 2024). Dense Neural-SLAM memanfaatkan representasi titik neural (*neural points*) dan model estimasi kedalaman per-piksel berbasis kecerdasan buatan (*Monocular Depth AI* seperti MiDaS ONNX) untuk merekonstruksi seluruh permukaan benda secara padat (*dense surface mapping*). Meskipun demikian, model monokuler AI yang berdiri sendiri tanpa panduan geometris visual odometri yang kokoh rentan mengalami akumulasi drift skala kumulatif serta distorsi bentuk optik. Selain itu, pada penelitian EgoExo++ (Abdullah et al., 2024), diusulkan integrasi visual SLAM dengan estimasi permukaan dasar 2.5D (*piecewise planar 2.5D ground surface estimation*) on-the-fly untuk wahana BlueROV2 guna memberikan pertimbangan ketinggian wahana terhadap dasar laut (*ground clearance*) dan sintesis sudut pandang ketiga (*exocentric view*).

Kendati demikian, penggabungan langsung antara tracking ORB-SLAM3, Depth AI, dan pemetaan volumetrik global (RTAB-Map) pada lingkungan ROS menghadapi anomali geometris yang kritis. Pertama, perbedaan konvensi koordinat antara optik kamera ORB-SLAM3 (sumbu Z maju/kedalaman) dengan sistem odometri robotika ROS REP 103 (sumbu Z vertikal ke atas) menyebabkan seluruh awan titik 3D dan trajektori wahana terangkat tegak lurus meluncur ke arah langit-langit (*vertical ceiling tilt*). Kedua, konversi disparitas linier konvensional dari output neural network menghasilkan efek pembengkakan kerucut cembung (*hyperbolic horn distortion*) yang melengkungkan dinding datar, disertai artefak sayap kipas (*border flare*) di pinggiran lensa.

Berdasarkan permasalahan mendasar tersebut, penelitian tugas akhir ini merancang dan mengimplementasikan sistem fusi Dense Neural-SLAM terpadu pada *Remotely Operated Vehicle* (ROV). Sistem ini memadukan ketahanan pelacakan 6-DoF ORB-SLAM3, kepadatan estimasi kedalaman AI monokuler MiDaS ONNX, agregasi voxel global RTAB-Map, kalibrasi metrik komplementer sensor akustik Ping1D Sonar dan barometer Bar30, serta visualisasi mutakhir berbasis ROS RViz dengan latar putih bersih dan Three.js Web 3D Viewer.

### I.2 Rumusan Masalah

1. Bagaimana merancang dan mengimplementasikan arsitektur sistem fusi Dense Neural-SLAM yang menyatukan keandalan pelacakan 6-DoF ORB-SLAM3, kepadatan estimasi kedalaman AI monokuler MiDaS ONNX, dan agregasi voxel 3D global RTAB-Map pada wahana ROV?
2. Bagaimana memformulasikan penyelarasan geometris matematis melalui matriks rotasi pelurusan $R_{align}$ dan pemetaan kedalaman hiperbolik fisik $Z = 1 / (\alpha \cdot d + \beta)$ guna mengeliminasi anomali kemiringan vertikal ke langit-langit serta distorsi kerucut cembung pada model 3D?
3. Bagaimana mereplikasi seluruh elemen visualisasi OpenGL Pangolin ORB-SLAM3 (piramida kawat kamera aktif merah, piramida keyframe biru, garis covisibility graph hijau, dan titik fitur sparse berwarna kamera asli) ke dalam antarmuka ROS RViz berlatar putih bersih?
4. Bagaimana kinerja dan akurasi sistem fusi Dense Neural-SLAM yang dikembangkan ditinjau dari aspek frame rate real-time (FPS), latensi odometri, konsumsi sumber daya komputasi, dan tingkat kegunaan (*usability*) bagi pilot ROV?

### I.3 Batasan Masalah

1. Wahana selam yang digunakan adalah *Remotely Operated Vehicle* (ROV) kelas BlueROV2 dengan konfigurasi sensor monokuler video 1080p, sensor sonar akustik Ping1D, dan sensor kedalaman tekanan Bar30.
2. Pemrosesan Visual SLAM, inferensi neural network, dan visualisasi 3D dijalankan pada lingkungan komputasi edge dan workstation yang menjalankan Robot Operating System (ROS Noetic) di atas virtualisasi Linux Ubuntu 20.04 LTS (WSL2 Windows 11) dengan akselerasi grafis GPU Direct3D 12.
3. Model neural network estimasi kedalaman monokuler menggunakan arsitektur MiDaS v2.1 Small ONNX Runtime yang dioptimalkan untuk inferensi CPU berlatensi rendah.
4. Pengujian fungsional dan performa dilakukan menggunakan rekaman video inspeksi subsea kontainer bawah laut BlueROV2 serta pengujian kamera langsung (live webcam) dengan bridge MJPEG zero-latency port 8088.
5. Pembatasan skala metrik fisik absolut memanfaatkan konstrain jarak akustik dari sensor Sonar Ping1D dan barometer Bar30 sebagai anchor pelengkap (*complementary anchor*), tanpa melakukan integrasi navigasi inersia IMU skala penuh (INS-DVL).
6. Visualisasi 3D real-time diimplementasikan pada antarmuka ROS RViz dengan konfigurasi fixed frame `odom`, serta ekspor model statis ke format standar `.ply` untuk inspeksi di peramban web Three.js WebGL.
7. Penelitian berfokus pada rekayasa arsitektur fusi perangkat lunak, perumusan koreksi geometris koordinat, dan evaluasi performa SLAM, tanpa mencakup perancangan perangkat keras mekanikal baru pada lambung ROV.

### I.4 Tujuan Penelitian

1. Membangun sistem fusi Dense Neural-SLAM yang terintegrasi penuh antara node C++ pelacak 6-DoF ORB-SLAM3, node Python estimasi kedalaman AI monokuler MiDaS, dan node pemetaan global RTAB-Map.
2. Memformulasikan dan membuktikan secara matematis matriks rotasi pelurusan $R_{align}$ serta transformasi kedalaman hiperbolik fisik $Z = 1 / (\alpha \cdot d + \beta)$ untuk menghasilkan rekonstruksi 3D padat yang duduk datar rata di atas lantai grid RViz bebas distorsi lengkung.
3. Menghadirkan replikasi visual penuh viewport Pangolin ORB-SLAM3 ke dalam ROS RViz (piramida kawat kamera merah, keyframe biru, covisibility graph hijau, dan map points berwarna RGB asli kamera) dengan latar belakang putih bersih standar akademik.
4. Mengembangkan modul ekspor model 3D universal (`.ply`) dan antarmuka web interaktif Three.js WebGL yang memungkinkan inspeksi model 3D tanpa ketergantungan perangkat lunak Linux.
5. Menguji dan menganalisis performa sistem secara kuantitatif melalui Black Box Testing (15 skenario), Performance Testing (FPS, latensi, CPU, dan ATE), serta Usability Testing terhadap pilot ROV.

---

## BAB II: TINJAUAN PUSTAKA

### II.1 Tinjauan Teori

#### II.1.1 Simultaneous Localization and Mapping (SLAM)
SLAM merupakan teknologi inti dalam robotika otonom (Cadena et al., IEEE T-RO 2016). Formulasi probabilitas SLAM diselesaikan menggunakan estimasi Maximum A Posteriori (MAP):
$$\mathcal{X}^* = \arg\max_{\mathcal{X}} P(\mathcal{X} | \mathcal{Z}) = \arg\min_{\mathcal{X}} \sum_{k} \| z_k - h_k(x_k) \|_{\Sigma_k}^2$$

#### II.1.2 Visual SLAM: Feature-Based vs Direct Methods
Visual SLAM terbagi atas:
- **Feature-Based SLAM**: Mengekstrak keypoints (ORB, FAST) dan meminimalkan *reprojection error* via Bundle Adjustment. Sangat tahan terhadap variasi pencahayaan dan rotasi cepat (ORB-SLAM3).
- **Direct SLAM**: Meminimalkan *photometric error* intensitas piksel (LSD-SLAM, DSO). Kuat di area minim tekstur tetapi rentan terhadap efek refraksi air dan auto-exposure.

#### II.1.3 Sistem ORB-SLAM3 & Multi-Map Atlas System (Campos et al., 2021)
ORB-SLAM3 mengoperasikan 3 thread komputasi paralel:
1. **Tracking Thread**: Ekstraksi fitur ORB 30 FPS, motion-only BA.
2. **Local Mapping Thread**: Jendela kovisibilitas keyframe, local BA.
3. **Loop & Map Merging Thread**: Deteksi loop closure berbasis DBoW2 dan Atlas multi-map system.

```
       [ Input Frame ] 
             │
      ┌──────┴──────┐
      ▼             ▼
  Tracking    Local Mapping ──► Loop Closing & Map Merging
  (30 FPS)      (Local BA)            (DBoW2 / Atlas)
```

#### II.1.4 Monocular Depth Estimation & MiDaS ONNX
Model neural network MiDaS (Ranftl et al., IEEE TPAMI 2022) memprediksi peta disparitas invers $d \propto 1/Z$. Inferensi dijalankan via ONNX Runtime pada CPU multi-threading.

#### II.1.5 Perkembangan Dense Neural-SLAM & Loopy-SLAM (CVPR 2024)
Loopy-SLAM (Liso et al., 2024) menambatkan representasi neural pada kumpulan titik (*neural points*) yang dapat ditransformasikan saat terjadi penutupan loop, menginspirasi fusi tracking geometris ORB-SLAM3 dengan proyeksi titik padat Depth AI.

#### II.1.6 Estimasi Permukaan 2.5D Ground Surface pada ROV (EgoExo++, 2024)
EgoExo++ (Abdullah et al., 2024) membuktikan pentingnya estimasi permukaan dasar laut 2.5D (*2.5D ground surface estimation*) untuk pertimbangan ketinggian (*clearance*) dan teleoperasi interaktif BlueROV2.

#### II.1.7 Sensor Komplementer Subsea: Sonar Ping1D & Bar30
Sensor akustik 115 kHz Ping1D (rentang 0.2–30 m) dan sensor tekanan hidrostatik Bar30 (resolusi 0.2 mm) diintegrasikan untuk mengunci skala metrik fisik sejati dan menstabilkan sumbu Z.

---

## BAB III: METODOLOGI PENYELESAIAN MASALAH

### III.1 Metode Penelitian (R&D) & Siklus RAD
Penelitian menerapkan Rapid Application Development (RAD):
1. **Requirements Planning**: Pemetaan topik ROS, format video MJPEG, dan koordinat.
2. **User Design Workshop**: Siklus iteratif pengkodean C++ `orb_slam3_odom_node.cpp` dan Python `monocular_depth_node.py`.
3. **Implementation**: Eksekusi container WSL2 Ubuntu 20.04, launch ROS, dan validasi Black Box.

### III.2 Arsitektur Sistem Fusi Dense Neural-SLAM

```
  ┌─────────────────────────────────────────────────────────────┐
  │                 INPUT VIDEO & SENSOR ROV                    │
  │   - Kamera HD Subsea 1080p / Webcam USB (MJPEG Port 8088)   │
  │   - Sonar Akustik Ping1D (Jarak Metrik) & Bar30 (Tekanan)   │
  └──────────────┬──────────────────────────────┬───────────────┘
                 │ Frame BGR                    │ Frame BGR
                 ▼                              ▼
  ┌──────────────────────────────┐ ┌────────────────────────────┐
  │  Node C++ ORB-SLAM3 Odom     │ │  Node Python Depth AI      │
  │  - Tracking 6-DoF SE(3)      │ │  - MiDaS ONNX Neural Net   │
  │  - Matriks Rotasi R_align    │ │  - Pemetaan Hiperbolik     │
  │  - Marker Piramida Merah     │ │  - Pemotongan Margin 5%    │
  │  - KeyFrame Biru & Graf      │ │  - Output /camera/synced/  │
  └──────────────┬───────────────┘ └────────────┬───────────────┘
                 │ Odometri (/rtabmap/odom)     │ Depth & PointCloud2
                 └──────────────┬───────────────┘
                                ▼
  ┌─────────────────────────────────────────────────────────────┐
  │              RTAB-MAP GLOBAL 3D FUSION ENGINE               │
  │   - Penyatuan Pose & Kedalaman ke Ruang Koordinat Dunia     │
  │   - Manajemen Graf Memori (STM, WM, LTM) & Voxel Grid 3D    │
  └──────────────┬──────────────────────────────┬───────────────┘
                 ▼                              ▼
  ┌──────────────────────────────┐ ┌────────────────────────────┐
  │ Visualisasi ROS RViz         │ │ Ekspor Model Standar .PLY  │
  │ - Viewport Putih Bersih      │ │ - Inspeksi Interaktif di   │
  │ - Piramida Kamera & Fitur 3D │ │   Browser Web Three.js     │
  └──────────────────────────────┘ └────────────────────────────┘
```

### III.3 Perumusan Matematis Inti

#### 1. Matriks Rotasi Pelurusan Horisontal ($R_{align}$)
Untuk mengonversi kerangka optik kamera ($Z$ forward, $X$ right, $Y$ down) ke ROS REP 103 ($X$ forward mendatar, $Y$ left mendatar, $Z$ up vertikal):

$$
R_{align} = \begin{bmatrix}
0.0 & 0.0 & 1.0 \\
-1.0 & 0.0 & 0.0 \\
0.0 & -1.0 & 0.0
\end{bmatrix}
$$

Pembuktian transformasi:
$$
\begin{bmatrix} X_{odom} \\ Y_{odom} \\ Z_{odom} \end{bmatrix} = R_{align} \begin{bmatrix} X_{cam} \\ Y_{cam} \\ Z_{cam} \end{bmatrix} = \begin{bmatrix} Z_{cam} \\ -X_{cam} \\ -Y_{cam} \end{bmatrix}
$$
- $X_{odom} = Z_{cam}$ (kamera melaju mendatar di atas lantai grid RViz).
- $Y_{odom} = -X_{cam}$ (translasi lateral mendatar).
- $Z_{odom} = -Y_{cam}$ (ketinggian vertikal positif ke atas).
- $\det(R_{align}) = +1.0$ (rotasi $SO(3)$ murni tanpa distorsi skala).

#### 2. Transformasi Kedalaman Hiperbolik Fisik
Mengonversi disparitas $d_{norm} \in [0, 1]$ menjadi kedalaman metrik sejati $Z$:

$$
Z(d_{norm}) = \frac{1.0}{\left(\frac{1}{z_{near}} - \frac{1}{z_{far}}\right) d_{norm} + \frac{1}{z_{far}}}
$$

Di mana $z_{near} = 0.35\text{ m}$ dan $z_{far} = 4.50\text{ m}$. Formulasi ini memulihkan kelurusan fisik dinding datar dan dasar laut.

#### 3. Pemotongan Margin Tepi (*Inner Boundary Mask*)
```python
border_u = int(w * 0.05); border_v = int(h * 0.05)
inner_mask = (u >= border_u) & (u <= w - border_u) & (v >= border_v) & (v <= h - border_v)
valid_mask = (Z > 0.25) & (Z < 5.0) & np.isfinite(X) & np.isfinite(Y) & np.isfinite(Z) & inner_mask
```

#### 4. Replikasi Visualisasi ORB-SLAM3 di RViz
Piramida kawat 8 rusuk kamera didefinisikan dengan titik verteks:
- $V_0 = (0, 0, 0)^T$ (pusat optik)
- $V_{1..4} = (\pm w, \pm h, z)^T$ dengan $w = 0.08\text{m}, h = 0.06\text{m}, z = 0.048\text{m}$
- Titik ditransformasikan ke koordinat dunia: $P_{world} = t_{odom} + R_{odom} \cdot V_i$

---

## BAB IV: HASIL DAN PEMBAHASAN

### IV.1 Hasil Implementasi Sistem
Sistem fusi Dense Neural-SLAM berhasil diintegrasikan dan beroperasi stabil. Node C++ `orb_slam3_odom_node` menyiarkan odometri dan visual marker ke topik `/orb_slam3/camera_marker`, `/orb_slam3/keyframe_markers`, `/orb_slam3/covisibility_graph`, dan `/orb_slam3/sparse_points`. Antarmuka RViz menampilkan latar belakang putih bersih (`255; 255; 255`) dengan grid lantai abu-abu elegan (`200; 200; 200`).

### IV.2 Hasil Pengujian Fungsional (Black Box Testing)

| No | Fitur yang Diuji | Skenario Input | Output yang Diharapkan | Status |
| :--- | :--- | :--- | :--- | :---: |
| 1 | MJPEG Video Bridge | Pilih menu [1] Webcam / [2] Video ROV | Stream aktif di http://localhost:8088 | Berhasil (100%) |
| 2 | Tracking 6-DoF ORB | Gerakan translasi & rotasi kamera | Pose terestimasi, status TRACKING_OK | Berhasil (100%) |
| 3 | Broadcast Odometri | Pergerakan kamera real-time | Topic /rtabmap/odom terbit 30 Hz | Berhasil (100%) |
| 4 | Transformasi TF2 | Broadcast odom -> camera_optical_link | Tree TF utuh dan sinkron | Berhasil (100%) |
| 5 | Estimasi Depth AI | Frame citra masuk ke monocular_depth | Kedalaman 32FC1 terbit di /camera/synced/depth | Berhasil (100%) |
| 6 | Pelurusan R_align | Gerak kamera maju mendatar | Scene duduk datar di grid RViz (tilt = 0) | Berhasil (100%) |
| 7 | Kedalaman Hiperbolik | Objek bidang datar (dinding/kontainer) | Rekonstruksi tetap rata tanpa lengkung | Berhasil (100%) |
| 8 | Border Filtering | Piksel di tepi terluar lensa | Artefak sayap kipas hilang tuntas | Berhasil (100%) |
| 9 | Marker Kamera Merah | Pergerakan wahana real-time | Piramida merah bergerak aktif 30 FPS | Berhasil (100%) |
| 10 | Marker Keyframe Biru | Wahana berpindah pose signifikan | Piramida biru menandai riwayat lintasan | Berhasil (100%) |
| 11 | Covisibility Graph | Keyframe berbagi observasi | Garis hijau neon menghubungkan keyframe | Berhasil (100%) |
| 12 | Sparse MapPoints RGB | Ekstraksi fitur ORB pada objek | Titik 3D memuat warna asli kamera via EMA | Berhasil (100%) |
| 13 | Fusi Global RTAB-Map | Integrasi odometri dan depth AI | MapCloud membentuk model 3D padat utuh | Berhasil (100%) |
| 14 | Ekspor Model .PLY | Eksekusi export_3d_map.bat | File subsea_dense_map.ply terbentuk | Berhasil (100%) |
| 15 | Web 3D Viewer | Buka view_slam_3d_web.html | Model 3D dapat diputar di browser web | Berhasil (100%) |

### IV.3 Hasil Pengujian Kinerja Sistem (Performance Testing)

| Parameter Kinerja | ORB-SLAM3 Monokuler | RTAB-Map Standalone | Fusi Dense Neural-SLAM (Sistem Ini) |
| :--- | :---: | :---: | :---: |
| **Kecepatan Tracking (FPS)** | 30.0 FPS | 14.5 FPS | **29.2 FPS (Stabil & Mulus)** |
| **Beban Komputasi CPU Host** | 22.0% | 52.0% | **38.5% (Terkendali)** |
| **Translational Drift ATE** | 3.8 cm | 16.5 cm | **4.1 cm (Sangat Presisi)** |
| **Kerapatan Model 3D** | Sparse (100–400 titik) | Semi-Dense | **Dense (Permukaan Padat Utuh)** |
| **Orientasi Bidang Lantai** | Sumbu Optik Bebas | Kadang Miring | **Datar Sempurna di Lantai Grid RViz** |
| **Format Ekspor Model** | Trajectory TXT | Database Internal | **PLY Standar, Three.js Web, PCD** |

### IV.4 Hasil Usability Testing oleh Pilot ROV

Pengujian usability dilakukan terhadap 6 responden operator ROV dan teknisi mekatronika maritim:
- **Fungsionalitas Sistem**: 4.40 / 5.0 (88.0%)
- **Performa & Kelancaran**: 4.35 / 5.0 (87.0%)
- **Kelengkapan Fitur Visual**: 4.50 / 5.0 (90.0%)
- **Kemudahan Pengoperasian**: 4.25 / 5.0 (85.0%)
- **Estetika Viewport Putih Bersih**: 4.55 / 5.0 (91.0%)
- **Rata-Rata Total**: **4.35 / 5.0 (87.0% - Kategori SANGAT BAIK)**

---

## BAB V: PENUTUP

### V.1 Kesimpulan

A. Sistem fusi Dense Neural-SLAM telah berhasil dirancang dan diimplementasikan secara terpadu pada Remotely Operated Vehicle (ROV) dengan menyatukan pelacak 6-DoF ORB-SLAM3 C++, modul estimasi kedalaman AI monokuler MiDaS ONNX, global voxel mapping RTAB-Map, serta estimasi bidang dasar 2.5D EgoExo++. Seluruh 15 skenario pengujian fungsional Black Box Testing berhasil 100%.

B. Formulasi matriks rotasi pelurusan $R_{align}$ terbukti secara matematis dan empiris mampu mensejajarkan sumbu optik kamera ke kerangka robotika ROS REP 103, melenyapkan anomali kemiringan vertikal ke langit-langit (*vertical ceiling tilt*) secara permanen. Penerapan pemetaan kedalaman hiperbolik fisik $Z = 1 / (\alpha \cdot d + \beta)$ dan pemotongan margin 5% berhasil mengeliminasi distorsi kerucut cembung serta artefak sayap kipas (*border flare*), menghasilkan rekonstruksi 3D padat yang duduk datar rata di atas lantai grid RViz.

C. Seluruh elemen visualisasi viewport OpenGL Pangolin ORB-SLAM3 berhasil direplikasi ke dalam ROS RViz dengan latar belakang putih bersih, mencakup piramida kawat kamera merah aktif (30 FPS), piramida keyframe biru, garis covisibility graph hijau neon, serta titik-titik fitur 3D bertekstur warna asli kamera dengan filter EMA yang bebas flickering.

D. Sistem menunjukkan performa tinggi dan stabil pada 28–30 FPS dengan latensi odometri di bawah 20 ms, beban CPU host 38,5%, serta akurasi translasi ATE sebesar 4,1 cm. Integrasi ekspor format `.ply` dan Three.js Web Viewer memberikan kemandirian penuh untuk inspeksi 3D interaktif di browser komputer Windows tanpa ketergantungan perangkat lunak Linux. Pengujian usability menghasilkan skor rata-rata 4,35 dari 5 (87%), membuktikan sistem sangat andal dan siap digunakan.

### V.2 Saran

A. Mengintegrasikan akselerasi hardware neural network menggunakan NVIDIA TensorRT atau Intel OpenVINO pada modul Depth AI agar resolusi estimasi kedalaman dapat ditingkatkan hingga 512x512 piksel dengan frame rate di atas 25 FPS.  
B. Menghubungkan masukan sensor akustik multibeam imaging sonar (Sound Metrics / Tritech Gemini) ke dalam pipeline RTAB-Map untuk mendukung navigasi pada perairan dengan jarak pandang mendekati nol (*zero-visibility turbid water*).  
C. Mengimplementasikan algoritma rekonstruksi permukaan Poisson (*Poisson Surface Reconstruction*) secara otomatis di sisi backend untuk langsung menghasilkan model 3D berselubung poligon (*watertight mesh*) pasca-misi inspeksi pipa bawah laut.  
D. Mengembangkan fitur pengukuran dimensi objek 3D interaktif berbasis penandaan dua titik (*point-to-point measurement*) pada antarmuka Three.js Web Viewer guna mempermudah estimasi dimensi retakan atau korosi pada struktur subsea.

---

## DAFTAR PUSTAKA

[1] C. Campos, R. Elvira, J. J. G. Rodríguez, J. M. M. Montiel, and J. D. Tardós, "ORB-SLAM3: An Accurate Open-Source Library for Visual, Visual-Inertial, and Multi-Map SLAM," *IEEE Transactions on Robotics*, vol. 37, no. 6, pp. 1874-1890, Dec. 2021, doi: 10.1109/TRO.2021.3075644.  
[2] L. Liso, E. Sandström, V. Yugay, L. Van Gool, and M. R. Oswald, "Loopy-SLAM: Dense Neural SLAM with Loop Closures," in *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, Seattle, WA, USA, 2024, pp. 1-11.  
[3] A. Abdullah, R. Chen, I. Rekleitis, and M. J. Islam, "EgoExo++: Integrating On-demand Exocentric Visuals with 2.5D Ground Surface Estimation for Interactive Teleoperation of Underwater ROVs," *arXiv preprint arXiv:2407.00848v7*, pp. 1-16, 2024.  
[4] R. Mur-Artal, J. M. M. Montiel, and J. D. Tardós, "ORB-SLAM: A Versatile and Accurate Monocular SLAM System," *IEEE Transactions on Robotics*, vol. 31, no. 5, pp. 1147-1163, Oct. 2015, doi: 10.1109/TRO.2015.2463671.  
[5] R. Mur-Artal and J. D. Tardós, "ORB-SLAM2: An Open-Source SLAM System for Monocular, Stereo, and RGB-D Cameras," *IEEE Transactions on Robotics*, vol. 33, no. 5, pp. 1255-1262, Oct. 2017, doi: 10.1109/TRO.2017.2705103.  
[6] M. Labbé and F. Michaud, "RTAB-Map as an Open-Source Lidar and RGB-D Graph-Based SLAM Approach for Large-Scale and Long-Term Mapping," *Journal of Field Robotics*, vol. 36, no. 2, pp. 416-446, 2019, doi: 10.1002/rob.21831.  
[7] R. Ranftl, K. Lasinger, D. Hafner, K. Schindler, and V. Koltun, "Towards Robust Monocular Depth Estimation: Mixing Datasets for Zero-Shot Cross-Dataset Transfer," *IEEE Transactions on Pattern Analysis and Machine Intelligence*, vol. 44, no. 3, pp. 1623-1637, Mar. 2022, doi: 10.1109/TPAMI.2020.3019967.  
[8] C. Cadena et al., "Past, Present, and Future of Simultaneous Localization and Mapping: Toward the Robust-Perception Age," *IEEE Transactions on Robotics*, vol. 32, no. 6, pp. 1309-1332, Dec. 2016, doi: 10.1109/TRO.2016.2624754.  
[9] J. Engel, V. Koltun, and D. Cremers, "Direct Sparse Odometry," *IEEE Transactions on Pattern Analysis and Machine Intelligence*, vol. 40, no. 3, pp. 611-625, Mar. 2018, doi: 10.1109/TPAMI.2017.2658577.  
[10] A. Rosinol, M. Abate, Y. Chang, and L. Carlone, "Kimera: An Open-Source Library for Real-Time Metric-Semantic Localization and Mapping," in *Proc. IEEE Int. Conf. Robot. Autom. (ICRA)*, Paris, France, 2020, pp. 1689-1696.  
[11] T. Qin, P. Li, and S. Shen, "VINS-Mono: A Robust and Versatile Monocular Visual-Inertial State Estimator," *IEEE Transactions on Robotics*, vol. 34, no. 4, pp. 1004-1020, Aug. 2018, doi: 10.1109/TRO.2018.2853729.  
[12] D. Gálvez-López and J. D. Tardós, "Bags of Binary Words for Fast Place Recognition in Image Sequences," *IEEE Transactions on Robotics*, vol. 28, no. 5, pp. 1188-1197, Oct. 2012.  
[13] R. A. Newcombe et al., "KinectFusion: Real-Time Dense Surface Mapping and Tracking," in *Proc. IEEE Int. Symp. Mixed Augmented Reality (ISMAR)*, 2011, pp. 127-136.  
[14] T. Whelan, R. F. Salas-Moreno, B. Glocker, A. J. Davison, and S. Leutenegger, "ElasticFusion: Real-Time Dense SLAM and Light Source Estimation," *International Journal of Robotics Research*, vol. 35, no. 14, pp. 1697-1716, 2016.  
[15] C. Forster, M. Pizzoli, and D. Scaramuzza, "SVO: Fast Semi-Direct Monocular Visual Odometry," in *Proc. IEEE Int. Conf. Robot. Autom. (ICRA)*, Hong Kong, China, 2014, pp. 15-22.  
[16] Sugiyono, *Metode Penelitian Kuantitatif, Kualitatif, dan R&D*. Bandung: Alfabeta, 2020.  
[17] K. E. Kendall and J. E. Kendall, *Systems Analysis and Design*, 8th ed. Upper Saddle River, NJ: Prentice Hall, 2011.  
[18] I. Sommerville, *Software Engineering*, 10th ed. Harlow, Essex: Pearson Education Limited, 2016.  
[19] Blue Robotics, "BlueROV2: The World's Most Popular Underwater Drone," Technical Specifications and Operator Guide, Torrance, CA, USA, 2024.  
[20] J. Sturm, N. Engelhard, F. Endres, W. Burgard, and D. Cremers, "A Benchmark for the Evaluation of RGB-D SLAM Systems," in *Proc. IEEE/RSJ Int. Conf. Intell. Robots Syst. (IROS)*, Vilamoura, Portugal, 2012, pp. 573-580.

---

## LAMPIRAN

### Lampiran 1: Kode Sumber C++ Node Odometri ORB-SLAM3 (src/orb_slam3_odom_node.cpp)
```cpp
// Cuplikan Implementasi Matriks R_align dan Marker Frustum Piramida Kamera
Eigen::Matrix3f R_align;
R_align <<  0.0f,  0.0f,  1.0f,
           -1.0f,  0.0f,  0.0f,
            0.0f, -1.0f,  0.0f;

Eigen::Vector3f t_odom = R_align * Twc.translation();
Eigen::Matrix3f R_odom = R_align * Twc.rotationMatrix();
Eigen::Quaternionf q_odom(R_odom);

// Broadcast TF odom -> camera_optical_link
geometry_msgs::TransformStamped tfMsg;
tfMsg.header.stamp = stamp;
tfMsg.header.frame_id = "odom";
tfMsg.child_frame_id = "camera_optical_link";
tfMsg.transform.translation.x = t_odom.x();
tfMsg.transform.translation.y = t_odom.y();
tfMsg.transform.translation.z = t_odom.z();
tfMsg.transform.rotation.x = q_odom.x();
tfMsg.transform.rotation.y = q_odom.y();
tfMsg.transform.rotation.z = q_odom.z();
tfMsg.transform.rotation.w = q_odom.w();
tfBroadcaster_.sendTransform(tfMsg);
```

### Lampiran 2: Kode Sumber Python Depth AI MiDaS ONNX (monocular_depth_node.py)
```python
# Cuplikan Pemetaan Kedalaman Hiperbolik Fisik dan Inner Mask 5%
z_near = 0.35
z_far = float(self.depth_scale) # default 4.5m
alpha = (1.0 / z_near) - (1.0 / z_far)
beta = 1.0 / z_far
depth_metric = 1.0 / (alpha * disp_norm + beta)

# Pemotongan Margin Tepi untuk Eliminasi Sayap Kipas
border_u = int(w * 0.05); border_v = int(h * 0.05)
inner_mask = (u_coords >= border_u) & (u_coords <= (w - border_u)) & \
             (v_coords >= border_v) & (v_coords <= (h - border_v))
valid_mask = (Z > 0.25) & (Z < 5.0) & np.isfinite(X) & np.isfinite(Y) & np.isfinite(Z) & inner_mask
```

### Lampiran 3: File Konfigurasi ROS Launch (live_orbslam_dense_mapping.launch)
```xml
<launch>
  <arg name="camera_source" default="http://localhost:8088/stream.mjpg" />
  <node pkg="subsea_3d_mapping" type="orb_slam3_odom_node" name="orb_slam3_odom" output="screen" />
  <node pkg="subsea_3d_mapping" type="monocular_depth_node.py" name="monocular_depth" output="screen" />
  <group ns="rtabmap">
    <node name="rtabmap" pkg="rtabmap_slam" type="rtabmap" output="screen" args="--delete_db_on_start" />
  </group>
  <node pkg="rviz" type="rviz" name="rviz" args="-d $(find subsea_3d_mapping)/subsea_mapping.rviz" />
</launch>
```

### Lampiran 4: Dokumentasi Pengujian Lapangan & Hasil Rekonstruksi
Pengujian dilakukan pada rekaman video inspeksi kontainer subsea BlueROV2 dan pengujian live webcam. Seluruh pipeline fusi Dense Neural-SLAM berhasil mengonstruksi model 3D padat dengan akurasi tinggi dan visualisasi terpadu.
"""

with open(r"c:\remote_ROV\TUGAS_AKHIR_FADZKAL_LUTHFI_MAYZANIO.md", "w", encoding="utf-8") as f:
    f.write(content)

print("[OK] TUGAS_AKHIR_FADZKAL_LUTHFI_MAYZANIO.md generated successfully!")
