import cv2
import os

def extract_container_high_contrast(video_path, output_dir, start_sec=235.0, end_sec=260.0, fps_sample=2.0):
    os.makedirs(output_dir, exist_ok=True)
    # Clear old frames
    for f in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, f))
        
    cap = cv2.VideoCapture(video_path)
    video_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    step_frames = int(video_fps / fps_sample)
    
    current_frame = int(start_sec * video_fps)
    end_frame = int(end_sec * video_fps)
    
    saved = 0
    while current_frame < end_frame:
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        ret, frame = cap.read()
        if not ret:
            break
            
        filename = os.path.join(output_dir, f"frame_{saved:04d}.jpg")
        cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        saved += 1
        current_frame += step_frames
        
    cap.release()
    print(f"Sukses mengekstrak {saved} foto kontainer ber-fitur tinggi (Detik {start_sec}-{end_sec}) ke: {output_dir}")

if __name__ == "__main__":
    vid = r"c:\remote_ROV\videos\YTDown.com_YouTube_Media_g4bUv6Fx3Pk_Site-113-A-Steel-Container-from-a-BlueROV2_001_1080p.mp4"
    out = r"c:\remote_ROV\photogrammetry_images"
    extract_container_high_contrast(vid, out, start_sec=235.0, end_sec=258.0, fps_sample=2.0)
