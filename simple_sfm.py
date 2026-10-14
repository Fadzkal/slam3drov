import cv2
import numpy as np
import os
import glob

def run_sfm(image_dir, output_ply, max_images=50):
    images_paths = sorted(glob.glob(os.path.join(image_dir, "*.jpg")))[:max_images]
    print(f"Memproses {len(images_paths)} frame kontainer untuk 3D Photogrammetry...")
    
    if len(images_paths) < 2:
        print("Kurang frame!")
        return

    # SIFT Feature Detector (High accuracy underwater feature extractor)
    sift = cv2.SIFT_create(nfeatures=3000)
    bf = cv2.BFMatcher(cv2.NORM_L2)
    
    # Intrinsic matrix for 1080p camera
    K = np.array([
        [1200.0, 0.0, 960.0],
        [0.0, 1200.0, 540.0],
        [0.0, 0.0, 1.0]
    ], dtype=np.float64)

    all_points = []
    all_colors = []
    
    R_current = np.eye(3, dtype=np.float64)
    t_current = np.zeros((3, 1), dtype=np.float64)
    
    prev_img = cv2.imread(images_paths[0])
    prev_gray = cv2.cvtColor(prev_img, cv2.COLOR_BGR2GRAY)
    prev_kp, prev_des = sift.detectAndCompute(prev_gray, None)
    
    for idx in range(1, len(images_paths)):
        curr_img = cv2.imread(images_paths[idx])
        curr_gray = cv2.cvtColor(curr_img, cv2.COLOR_BGR2GRAY)
        curr_kp, curr_des = sift.detectAndCompute(curr_gray, None)
        
        if prev_des is None or curr_des is None or len(prev_des) < 15 or len(curr_des) < 15:
            continue
            
        try:
            matches = bf.knnMatch(prev_des, curr_des, k=2)
        except Exception:
            continue
            
        good = [m for m, n in matches if len((m, n)) == 2 and m.distance < 0.75 * n.distance]
        
        if len(good) < 25:
            continue
            
        pts1 = np.float32([prev_kp[m.queryIdx].pt for m in good])
        pts2 = np.float32([curr_kp[m.trainIdx].pt for m in good])
        
        # Estimate Essential Matrix with RANSAC
        E, mask = cv2.findEssentialMat(pts1, pts2, K, method=cv2.RANSAC, prob=0.999, threshold=1.5)
        if E is None or mask is None:
            continue
            
        mask = mask.ravel().astype(bool)
        pts1_in = pts1[mask]
        pts2_in = pts2[mask]
        
        if len(pts1_in) < 15:
            continue
            
        # Recover relative camera motion [R | t]
        _, R, t, mask_pose = cv2.recoverPose(E, pts1_in, pts2_in, K)
        
        # Camera projection matrices
        P1 = K @ np.hstack((R_current, t_current))
        t_next = t_current + R_current @ t
        R_next = R_current @ R
        P2 = K @ np.hstack((R_next, t_next))
        
        # Multi-view triangulation
        pts4d = cv2.triangulatePoints(P1, P2, pts1_in.T, pts2_in.T)
        pts3d = (pts4d[:3] / (pts4d[3] + 1e-8)).T
        
        # Check depth validity
        valid = (pts4d[3] > 1e-4) & (pts3d[:, 2] > 0.3) & (pts3d[:, 2] < 25.0)
        valid_pts = pts3d[valid]
        valid_pts1 = pts1_in[valid].astype(int)
        
        for pt, uv in zip(valid_pts, valid_pts1):
            u = np.clip(uv[0], 0, prev_img.shape[1] - 1)
            v = np.clip(uv[1], 0, prev_img.shape[0] - 1)
            bgr = prev_img[v, u]
            all_points.append(pt)
            all_colors.append([bgr[2], bgr[1], bgr[0]])
            
        print(f"Frame {idx}/{len(images_paths)}: +{len(valid_pts)} titik 3D nyata (Akumulasi: {len(all_points):,})")
        
        R_current = R_next
        t_current = t_next
        prev_img, prev_gray, prev_kp, prev_des = curr_img, curr_gray, curr_kp, curr_des

    if len(all_points) == 0:
        print("Tidak ada titik 3D yang berhasil dibuat.")
        return

    all_points = np.array(all_points)
    all_colors = np.array(all_colors)
    
    # Save to standard PLY format
    with open(output_ply, 'w') as f:
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write(f"element vertex {len(all_points)}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        f.write("property uchar red\n")
        f.write("property uchar green\n")
        f.write("property uchar blue\n")
        f.write("end_header\n")
        for p, c in zip(all_points, all_colors):
            f.write(f"{p[0]:.4f} {p[1]:.4f} {p[2]:.4f} {int(c[0])} {int(c[1])} {int(c[2])}\n")
            
    print(f"\n=======================================================")
    print(f"SUKSES! Model 3D Photogrammetry tersimpan di:\n--> {output_ply}")
    print(f"Total titik 3D padat dan akurat: {len(all_points):,} titik")
    print(f"=======================================================")

if __name__ == "__main__":
    imgs = r"c:\remote_ROV\photogrammetry_images"
    out_ply = r"c:\remote_ROV\underwater_container_3d.ply"
    run_sfm(imgs, out_ply, max_images=50)
