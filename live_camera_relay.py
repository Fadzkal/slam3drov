import subprocess, threading, time
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver

frame_lock = threading.Lock()
current_frame = None

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global current_frame
        self.send_response(200)
        self.send_header('Age', '0')
        self.send_header('Cache-Control', 'no-cache, private')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
        self.end_headers()
        last_sent = None
        try:
            while True:
                with frame_lock:
                    f = current_frame
                if f is not None and f is not last_sent:
                    last_sent = f
                    self.wfile.write(
                        b'--FRAME\r\nContent-Type: image/jpeg\r\nContent-Length: '
                        + str(len(f)).encode()
                        + b'\r\n\r\n'
                        + f
                        + b'\r\n'
                    )
                time.sleep(0.01)
        except Exception:
            pass

    def log_message(self, format, *args):
        pass

def run_ffmpeg():
    global current_frame
    cmd = [
        'c:/remote_ROV/cockpit/binaries/ffmpeg/ffmpeg.exe',
        '-protocol_whitelist', 'file,udp,rtp',
        '-fflags', 'nobuffer',
        '-flags', 'low_delay',
        '-max_delay', '0',
        '-i', 'c:/remote_ROV/stream.sdp',
        '-vf', 'scale=960:540,vflip,hflip',
        '-f', 'image2pipe',
        '-vcodec', 'mjpeg',
        '-q:v', '5',
        '-r', '20',
        '-'
    ]
    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10**7)
    buffer = b''
    while True:
        chunk = pipe.stdout.read(16384)
        if not chunk:
            break
        buffer += chunk
        while True:
            a = buffer.find(b'\xff\xd8')
            if a == -1:
                buffer = b''
                break
            if a > 0:
                buffer = buffer[a:]
                a = 0
            b = buffer.find(b'\xff\xd9', 2)
            if b == -1:
                break
            jpg = buffer[:b+2]
            buffer = buffer[b+2:]
            if len(jpg) > 3000:
                with frame_lock:
                    current_frame = jpg

if __name__ == '__main__':
    t = threading.Thread(target=run_ffmpeg, daemon=True)
    t.start()
    print('Starting BlueROV2 Live Camera Relay (960x540 Smooth) on http://0.0.0.0:8555/video ...')
    server = ThreadedHTTPServer(('0.0.0.0', 8555), CamHandler)
    server.serve_forever()
