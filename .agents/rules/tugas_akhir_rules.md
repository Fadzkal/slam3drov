# PANDUAN DAN ATURAN PROYEK TUGAS AKHIR
# =============================================================================
# Penulis: Fadzkal Luthfi Mayzanio (NIM: 223443033)
# Institusi: Politeknik Manufaktur Bandung (Polman Bandung), 2026
# =============================================================================

1. **Identitas Resmi**: Fadzkal Luthfi Mayzanio (NIM 223443033), D4 Teknologi Rekayasa Informatika Industri, Jurusan Teknik Otomasi Manufaktur dan Mekatronika, Polman Bandung, 2026.
2. **Fokus Proyek**: Fusi Dense Neural-SLAM untuk 3D Mapping & Digital Twin Bawah Air ROV (ORB-SLAM3 + Depth AI MiDaS + RTAB-Map OctoMap 3D + 2.5D Surface EgoExo++ + Loopy-SLAM + Ping1D Sonar & Bar30 Pressure).
3. **Formulasi Matematis Wajib**:
   - Kedalaman Hiperbolik: Z(d_norm) = 1 / (2.6349 * d_norm + 0.2222) pada rentang [0.35m, 4.5m].
   - Rotasi Ortogonal R_align: [[0, 0, 1], [-1, 0, 0], [0, -1, 0]] untuk standar ROS REP 103 ENU.
   - Inner Boundary Filter: Margin 5% untuk eliminasi fan-wing artifacts.
4. **Format Standar Dokumen Polman**: Margin Kiri 4cm, Atas 3cm, Kanan 3cm, Bawah 3cm. Times New Roman 12 pt, 1.5 spasi.
5. **Skrip Generator**: `build_mega_thesis_docx.py` dan `build_mega_thesis_md.py`.
