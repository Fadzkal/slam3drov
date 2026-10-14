import cv2
import os
import argparse

def extract_frames(video_path, output_dir, interval_sec=1.0, max_frames=80):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Tidak bisa membuka video {video_path}")
        return
        
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    print(f"Video: {video_path}")
    print(f"Durasi: {duration:.1f} detik, FPS: {fps:.1f}, Total Frame: {total_frames}")
    
    step = int(fps * interval_sec)
    frame_idx = 0
    saved_count = 0
    
    while cap.isOpened() and saved_count < max_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            break
            
        # Check sharpness (Laplacian variance)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Save frame
        filename = os.path.join(output_dir, f"frame_{saved_count:04d}.jpg")
        cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        saved_count += 1
        frame_idx += step
        
    cap.release()
    print(f"Sukses mengekstrak {saved_count} foto berkualitas tinggi ke: {output_dir}")

if __name__ == "__main__":
    video = r"c:\remote_ROV\videos\YTDown.com_YouTube_Media_g4bUv6Fx3Pk_Site-113-A-Steel-Container-from-a-BlueROV2_001_1080p.mp4"
    out = r"c:\remote_ROV\photogrammetry_images"
    extract_frames(video, out, interval_sec=2.0, max_frames=60)
