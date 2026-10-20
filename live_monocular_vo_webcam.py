"""
Live Monocular Visual Odometry & Camera Tracking (CPU-Only)
-----------------------------------------------------------
Sistem pelacakan posisi kamera real-time menggunakan monocular camera (Webcam / ROV Stream).
Didesain 100% berjalan di CPU dengan algoritma Optical Flow & Epipolar Geometry.
"""

import cv2
import numpy as np
import time
import sys

class MonocularVisualOdometry:
    def __init__(self, fx=800, fy=800, cx=320, cy=240):
        # Matriks intrinsik kamera (perkiraan default resolusi 640x480)
        self.K = np.array([
            [fx,  0, cx],
            [ 0, fy, cy],
            [ 0,  0,  1]
        ], dtype=np.float64)
        
        # State tracking (Pose kamera terhadap origin)
        self.R = np.eye(3, dtype=np.float64)
        self.t = np.zeros((3, 1), dtype=np.float64)
        
        # Feature tracking parameters
        self.feature_params = dict(
            maxCorners=500,
            qualityLevel=0.02,
            minDistance=8,
            blockSize=7
        )
        
        self.lk_params = dict(
            winSize=(21, 21),
            maxLevel=3,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01)
        )
        
        self.prev_gray = None
        self.prev_pts = None
        self.trajectory = []
        self.min_features = 120

    def process_frame(self, frame):
        start_time = time.perf_counter()
        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Inisialisasi frame pertama
        if self.prev_gray is None:
            self.prev_gray = gray
            self.prev_pts = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)
            self.trajectory.append((float(self.t[0, 0]), float(self.t[2, 0])))
            comp_time = (time.perf_counter() - start_time) * 1000
            return frame, comp_time, len(self.prev_pts) if self.prev_pts is not None else 0

        # Jika titik fitur berkurang drastis, deteksi ulang fitur
        if self.prev_pts is None or len(self.prev_pts) < self.min_features:
            new_pts = cv2.goodFeaturesToTrack(self.prev_gray, mask=None, **self.feature_params)
            if new_pts is not None:
                self.prev_pts = new_pts

        num_tracked = 0
        if self.prev_pts is not None and len(self.prev_pts) > 8:
            # 1. Lucas-Kanade Optical Flow (Sangat ringan di CPU)
            curr_pts, status, err = cv2.calcOpticalFlowPyrLK(
                self.prev_gray, gray, self.prev_pts, None, **self.lk_params
            )

            # Saring titik yang berhasil dilacak
            if curr_pts is not None and status is not None:
                valid_prev = self.prev_pts[status == 1]
                valid_curr = curr_pts[status == 1]
                num_tracked = len(valid_curr)

                if num_tracked >= 8:
                    # 2. Hitung Essential Matrix menggunakan RANSAC
                    E, mask = cv2.findEssentialMat(
                        valid_curr, valid_prev, self.K,
                        method=cv2.RANSAC, prob=0.999, threshold=1.0
                    )

                    if E is not None and mask is not None:
                        # 3. Recover Pose (Rotasi R dan Translasi t kamera)
                        _, R_rel, t_rel, _ = cv2.recoverPose(E, valid_curr, valid_prev, self.K, mask=mask)

                        # Update akumulasi pose kamera di ruang 3D
                        # Pada monocular, scale relative kita tetapkan ke langkah normalisasi
                        scale = 1.0
                        # Saring pergerakan wajar agar tidak meledak saat frame blur
                        t_norm = np.linalg.norm(t_rel)
                        if t_norm > 1e-4:
                            self.t = self.t + scale * self.R.dot(t_rel)
                            self.R = self.R.dot(R_rel)

                        self.trajectory.append((float(self.t[0, 0]), float(self.t[2, 0])))

                # Gambar optical flow vector pada frame
                for p0, p1 in zip(valid_prev[-100:], valid_curr[-100:]):
                    x0, y0 = p0.ravel()
                    x1, y1 = p1.ravel()
                    cv2.line(frame, (int(x0), int(y0)), (int(x1), int(y1)), (0, 255, 0), 1)
                    cv2.circle(frame, (int(x1), int(y1)), 2, (0, 200, 255), -1)

                self.prev_pts = valid_curr.reshape(-1, 1, 2)
        
        self.prev_gray = gray
        comp_time = (time.perf_counter() - start_time) * 1000
        return frame, comp_time, num_tracked

    def reset(self):
        self.R = np.eye(3, dtype=np.float64)
        self.t = np.zeros((3, 1), dtype=np.float64)
        self.trajectory.clear()
        self.prev_gray = None
        self.prev_pts = None


def render_trajectory_map(trajectory, cur_x, cur_z, map_size=480):
    """Membuat peta top-down (Bird-Eye View) dari lintasan kamera secara real-time."""
    traj_img = np.zeros((map_size, map_size, 3), dtype=np.uint8)
    
    # Gambar grid koordinat
    cv2.line(traj_img, (map_size // 2, 0), (map_size // 2, map_size), (40, 40, 40), 1)
    cv2.line(traj_img, (0, map_size // 2), (map_size, map_size // 2), (40, 40, 40), 1)
    
    # Skala visualisasi peta
    scale = 3.0  # pixel per meter/unit
    cx = map_size // 2
    cz = map_size // 2

    # Gambar jejak lintasan yang sudah dilewati
    if len(trajectory) > 1:
        points = []
        for (tx, tz) in trajectory:
            px = int(cx + tx * scale)
            pz = int(cz - tz * scale)
            # Batasi agar tidak error jika keluar layar
            px = max(0, min(map_size - 1, px))
            pz = max(0, min(map_size - 1, pz))
            points.append((px, pz))
        
        for i in range(1, len(points)):
            cv2.line(traj_img, points[i-1], points[i], (0, 255, 255), 2)

    # Gambar posisi kamera saat ini
    curr_px = int(cx + cur_x * scale)
    curr_pz = int(cz - cur_z * scale)
    curr_px = max(5, min(map_size - 6, curr_px))
    curr_pz = max(5, min(map_size - 6, curr_pz))
    
    cv2.circle(traj_img, (curr_px, curr_pz), 6, (0, 0, 255), -1)
    cv2.circle(traj_img, (curr_px, curr_pz), 9, (255, 255, 255), 1)
    
    # Label keterangan peta
    cv2.putText(traj_img, "TOP-DOWN TRAJECTORY MAP (X-Z)", (15, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    cv2.putText(traj_img, f"Pos: X={cur_x:+.2f} | Z={cur_z:+.2f}", (15, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    cv2.putText(traj_img, "Tekan 'R': Reset Pose | 'Q': Keluar", (15, map_size - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (120, 120, 120), 1)

    return traj_img


def open_camera(source):
    """Membuka kamera dengan backend yang tepat agar tidak hang di Windows."""
    if isinstance(source, int) or (isinstance(source, str) and source.isdigit()):
        idx = int(source)
        try:
            from pygrabber.dshow_graph import FilterGraph
            devices = FilterGraph().get_input_devices()
            if idx < len(devices) and ("obs" in devices[idx].lower() or "virtual" in devices[idx].lower()):
                print(f"[PERINGATAN] Kamera ID {idx} ({devices[idx]}) adalah OBS Virtual Camera!")
                print(f"[INFO] Mengalihkan ke Webcam Fisik (ID 1)...")
                idx = 1
        except Exception:
            pass
        # Di Windows, gunakan DirectShow (cv2.CAP_DSHOW) agar membuka kamera USB instan
        print(f"[INFO] Membuka kamera ID {idx} dengan DirectShow (CAP_DSHOW)...")
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if not cap.isOpened():
            # Fallback ke default jika DSHOW gagal
            print(f"[WARN] DirectShow gagal, mencoba backend default...")
            cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        return cap
    else:
        # File video atau RTSP / SDP stream
        print(f"[INFO] Membuka stream / file video: {source}")
        cap = cv2.VideoCapture(source)
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        return cap


def main():
    # Sumber kamera: default coba 0, atau sesuai argumen
    video_source = 0
    if len(sys.argv) > 1:
        video_source = sys.argv[1]
        if video_source.isdigit():
            video_source = int(video_source)

    cap = open_camera(video_source)
    if not cap.isOpened():
        print(f"[ERROR] Gagal membuka kamera / video: {video_source}")
        print("[TIPS] Jika menggunakan USB Webcam, coba jalankan dengan indeks 1 atau 2:")
        print("       python live_monocular_vo_webcam.py 1")
        print("       python live_monocular_vo_webcam.py 2")
        return

    # Set resolusi webcam
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Inisialisasi Visual Odometry
    vo = MonocularVisualOdometry(fx=700, fy=700, cx=320, cy=240)
    
    print("\n=======================================================")
    print("  LIVE MONOCULAR CAMERA TRACKING (100% CPU REAL-TIME)  ")
    print("=======================================================")
    print("  Gerakkan webcam Anda secara perlahan ke kiri, kanan, ")
    print("  maju, mundur, dan amati lintasan kamera bergerak!    ")
    print("  Tekan 'R' untuk Reset | Tekan 'Q' untuk Keluar       ")
    print("=======================================================\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[INFO] Stream video selesai / terputus.")
            break

        frame = cv2.resize(frame, (640, 480))
        processed_frame, comp_time, num_tracked = vo.process_frame(frame)
        
        cur_x = float(vo.t[0, 0])
        cur_y = float(vo.t[1, 0])
        cur_z = float(vo.t[2, 0])

        # Tampilkan overlay info di frame kamera
        fps = 1000.0 / max(comp_time, 1e-5)
        cv2.putText(processed_frame, f"Computation time: {comp_time:.1f} msec ({fps:.0f} FPS)", 
                    (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(processed_frame, f"Tracked Features: {num_tracked}", 
                    (15, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 1)
        cv2.putText(processed_frame, f"3D Pose: X={cur_x:+.2f} Y={cur_y:+.2f} Z={cur_z:+.2f}", 
                    (15, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 255), 1)

        # Buat visualisasi Top-down Map
        traj_map = render_trajectory_map(vo.trajectory, cur_x, cur_z, map_size=480)

        # Gabungkan berdampingan (Side-by-Side: Kamera di kiri, Peta di kanan)
        dashboard = np.hstack((processed_frame, traj_map))
        
        cv2.imshow("Real-Time Monocular Camera Tracking (CPU Only)", dashboard)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
        elif key == ord('r'):
            vo.reset()
            print("[INFO] Pose di-reset ke origin (0, 0, 0).")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
