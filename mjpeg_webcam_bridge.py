"""
High-Performance Zero-Latency MJPEG Webcam Bridge: Windows -> WSL2
==================================================================
Kamera: Fisik USB Webcam (Eksklusif Non-OBS)
Fitur:
- ThreadingHTTPServer: multi-client (browser + ORB-SLAM3 bersamaan)
- Buffer size = 1: zero-latency, tidak ada buffer lag
- Single JPEG encoding: frame di-encode 1x di thread capture, sangat ringan
- Auto-filter: otomatis memblokir OBS Virtual Camera dan memilih webcam fisik
"""

import cv2
import threading
import time
import socket
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

def get_device_map():
    """Mengambil peta index -> nama kamera DirectShow, menandai OBS."""
    device_map = {}
    try:
        from pygrabber.dshow_graph import FilterGraph
        graph = FilterGraph()
        devices = graph.get_input_devices()
        for i, name in enumerate(devices):
            device_map[i] = name
    except Exception:
        pass
    return device_map

def select_camera(requested_idx=None):
    device_map = get_device_map()
    print("[INFO] Deteksi perangkat kamera:")
    obs_indices = set()
    valid_indices = []

    for idx, name in device_map.items():
        is_obs = ("obs" in name.lower()) or ("virtual" in name.lower())
        status = "[DIBLOKIR: OBS Virtual Camera]" if is_obs else "[TERSEDIA: Kamera Fisik]"
        print(f"  Index {idx}: {name} -> {status}")
        if is_obs:
            obs_indices.add(idx)
        else:
            valid_indices.append(idx)

    if not valid_indices:
        valid_indices = [1, 0]

    if requested_idx is not None:
        if requested_idx in obs_indices:
            print(f"[PERINGATAN] Index {requested_idx} adalah OBS Virtual Camera! Otomatis dialihkan ke kamera fisik.")
            return valid_indices[0] if valid_indices else 1
        return requested_idx

    # Prioritas kamera non-OBS: Index 1 (USB Camera) atau Index 0 (c922)
    for preferred in [1, 0]:
        if preferred in valid_indices:
            return preferred
    return valid_indices[0]

# Konfigurasi
requested_arg = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else None
CAMERA_INDEX = select_camera(requested_arg)
ACTIVE_CAM_NAME = get_device_map().get(CAMERA_INDEX, f"Camera Index {CAMERA_INDEX}")
DEFAULT_PORT = 8088
JPEG_QUALITY = 75
TARGET_FPS = 30

# State global
frame_condition = threading.Condition()
latest_jpeg = None
frame_counter = 0
running = True


def capture_loop(cam_idx):
    """Thread loop menangkap frame langsung dari webcam fisik dengan latency minimal."""
    global latest_jpeg, frame_counter, running, ACTIVE_CAM_NAME

    device_map = get_device_map()
    ACTIVE_CAM_NAME = device_map.get(cam_idx, f"Camera {cam_idx}")
    print(f"\n[INFO] Membuka webcam fisik: {ACTIVE_CAM_NAME} (Index {cam_idx}) via DirectShow...")
    cap = cv2.VideoCapture(cam_idx, cv2.CAP_DSHOW)

    # Matikan internal buffer DirectShow untuk mencegah video delay/lag
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, TARGET_FPS)

    if not cap.isOpened():
        print(f"[WARN] Kamera Index {cam_idx} gagal dibuka. Mencoba auto-detect webcam fisik lain...")
        found = False
        valid_alternatives = [i for i in [1, 0] if i != cam_idx and "obs" not in device_map.get(i, "").lower()]
        for alt_idx in valid_alternatives:
            cap = cv2.VideoCapture(alt_idx, cv2.CAP_DSHOW)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            if cap.isOpened():
                alt_name = device_map.get(alt_idx, f"Camera {alt_idx}")
                print(f"[INFO] Berhasil beralih ke kamera fisik: {alt_name} (Index {alt_idx})")
                cam_idx = alt_idx
                ACTIVE_CAM_NAME = alt_name
                found = True
                break
        if not found:
            print("[ERROR] Tidak ada kamera fisik yang bisa dibuka!")
            running = False
            return

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[OK] Webcam Fisik AKTIF: {ACTIVE_CAM_NAME} ({w}x{h} @ {TARGET_FPS} FPS, Zero-Lag, Buffer=1)")

    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]

    while running:
        ret, frame = cap.read()
        if not ret or frame is None:
            time.sleep(0.01)
            continue

        # Encode JPEG sekali saja di thread ini untuk semua client
        ret_enc, jpg = cv2.imencode('.jpg', frame, encode_param)
        if ret_enc:
            jpg_bytes = jpg.tobytes()
            with frame_condition:
                latest_jpeg = jpg_bytes
                frame_counter += 1
                frame_condition.notify_all()

    cap.release()


class MJPEGHandler(BaseHTTPRequestHandler):
    """Handler HTTP streaming dengan multipart/x-mixed-replace."""

    def log_message(self, format, *args):
        pass  # Matikan spam log konsol

    def do_GET(self):
        if self.path in ('/stream.mjpg', '/video', '/mjpeg'):
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Connection', 'close')
            self.end_headers()

            last_id = -1
            try:
                while running:
                    with frame_condition:
                        while running and frame_counter == last_id:
                            frame_condition.wait(timeout=0.1)
                        if not running:
                            break
                        jpeg = latest_jpeg
                        last_id = frame_counter

                    if jpeg is not None:
                        header = (b'--frame\r\n'
                                  b'Content-Type: image/jpeg\r\n'
                                  b'Content-Length: ' + str(len(jpeg)).encode() + b'\r\n\r\n')
                        self.wfile.write(header + jpeg + b'\r\n')
            except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
                pass

        elif self.path in ('/', '/index.html'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            html = f"""<!DOCTYPE html>
<html>
<head>
  <title>ORB-SLAM3 Real-Time Webcam Stream</title>
  <style>
    body {{ background: #0f1117; color: #fff; font-family: sans-serif; text-align: center; margin-top: 30px; }}
    .container {{ display: inline-block; background: #1a1d27; padding: 20px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.5); }}
    img {{ border-radius: 8px; border: 1px solid #333; }}
    .badge {{ display: inline-block; background: #10b981; color: #fff; padding: 4px 10px; border-radius: 20px; font-size: 13px; font-weight: bold; margin-bottom: 12px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="badge">● LIVE ZERO-LAG STREAM &bull; {ACTIVE_CAM_NAME} (Index {CAMERA_INDEX})</div>
    <br/>
    <img src="/stream.mjpg" width="640" height="480" />
    <p style="color:#888; font-size:14px; margin-top:15px;">Stream URL untuk ORB-SLAM3: <code>http://localhost:{self.server.server_port}/stream.mjpg</code></p>
  </div>
</body>
</html>"""
            self.wfile.write(html.encode())
        else:
            self.send_error(404)


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def find_free_port():
    candidates = [8088, 8888, 5000, 18080, 8554]
    for p in candidates:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("0.0.0.0", p))
            s.close()
            return p
        except Exception:
            continue
    return DEFAULT_PORT


if __name__ == '__main__':
    port = find_free_port()

    # Simpan port aktif ke file agar WSL2 otomatis tahu port yang benar
    port_file = os.path.join(os.path.dirname(__file__), "bridge_port.txt")
    with open(port_file, "w") as f:
        f.write(str(port))

    print("=" * 60)
    print("  MJPEG ZERO-LATENCY WEBCAM BRIDGE (Windows -> WSL2)      ")
    print("=" * 60)
    print(f"Target Kamera : Index {CAMERA_INDEX} ({ACTIVE_CAM_NAME})")
    print(f"Port Server   : {port}")
    print()

    # Mulai thread capture kamera
    t = threading.Thread(target=capture_loop, args=(CAMERA_INDEX,), daemon=True)
    t.start()
    time.sleep(1.0)

    if not running:
        print("[ERROR] Kamera tidak dapat diakses.")
        sys.exit(1)

    local_ip = get_local_ip()
    print("============================================================")
    print("  STATUS: STREAM REAL-TIME AKTIF!")
    print(f"  • Preview Browser : http://localhost:{port}/")
    print(f"  • Stream Endpoint : http://localhost:{port}/stream.mjpg")
    print(f"  • WSL2 LAN Stream : http://{local_ip}:{port}/stream.mjpg")
    print("============================================================")
    print("Tekan Ctrl+C di terminal ini untuk berhenti.")
    print()

    # Gunakan ThreadingHTTPServer agar multi-client tidak saling blokir / ngeleg
    server = ThreadingHTTPServer(("0.0.0.0", port), MJPEGHandler)
    server.daemon_threads = True
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        running = False
        print("\n[INFO] Bridge dihentikan.")
