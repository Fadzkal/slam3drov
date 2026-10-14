import cv2
import numpy as np
import os
import glob
import json

def run_dense_sfm_and_track(image_dir, output_json, max_images=45):
    images_paths = sorted(glob.glob(os.path.join(image_dir, "*.jpg")))[:max_images]
    print(f"Memproses {len(images_paths)} frame kontainer untuk Dense SfM & Robot Trajectory...")
    
    if len(images_paths) < 2:
        print("Kurang frame!")
        return

    sift = cv2.SIFT_create(nfeatures=5000)
    bf = cv2.BFMatcher(cv2.NORM_L2)
    
    K = np.array([
        [1200.0, 0.0, 960.0],
        [0.0, 1200.0, 540.0],
        [0.0, 0.0, 1.0]
    ], dtype=np.float64)

    all_points = []
    all_colors = []
    
    trajectory = []
    cam_rotations = []
    
    # Store keypoints and descriptors for multi-baseline matching
    frames_data = []
    print("Mengekstrak fitur SIFT resolusi tinggi...")
    for idx, path in enumerate(images_paths):
        img = cv2.imread(path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        kp, des = sift.detectAndCompute(gray, None)
        frames_data.append({
            'img': img,
            'gray': gray,
            'kp': kp,
            'des': des
        })
        if (idx + 1) % 10 == 0 or idx == len(images_paths) - 1:
            print(f"Ekstraksi: {idx + 1}/{len(images_paths)} frame selesai...")

    R_current = np.eye(3, dtype=np.float64)
    t_current = np.zeros((3, 1), dtype=np.float64)
    trajectory.append(t_current.flatten().tolist())
    cam_rotations.append(R_current.tolist())
    
    poses = [(R_current.copy(), t_current.copy())]
    
    print("\nMenghitung pergerakan kamera (Visual Odometry & Trajectory)...")
    for i in range(len(images_paths) - 1):
        d1 = frames_data[i]
        d2 = frames_data[i+1]
        
        if d1['des'] is None or d2['des'] is None:
            poses.append((R_current.copy(), t_current.copy()))
            trajectory.append(t_current.flatten().tolist())
            cam_rotations.append(R_current.tolist())
            continue
            
        matches = bf.knnMatch(d1['des'], d2['des'], k=2)
        good = [m for m, n in matches if len((m, n)) == 2 and m.distance < 0.75 * n.distance]
        
        if len(good) < 20:
            poses.append((R_current.copy(), t_current.copy()))
            trajectory.append(t_current.flatten().tolist())
            cam_rotations.append(R_current.tolist())
            continue
            
        pts1 = np.float32([d1['kp'][m.queryIdx].pt for m in good])
        pts2 = np.float32([d2['kp'][m.trainIdx].pt for m in good])
        
        E, mask = cv2.findEssentialMat(pts1, pts2, K, method=cv2.RANSAC, prob=0.999, threshold=1.5)
        if E is not None and mask is not None:
            mask = mask.ravel().astype(bool)
            _, R, t, _ = cv2.recoverPose(E, pts1[mask], pts2[mask], K)
            t_next = t_current + R_current @ t
            R_next = R_current @ R
            R_current = R_next
            t_current = t_next
        
        poses.append((R_current.copy(), t_current.copy()))
        trajectory.append(t_current.flatten().tolist())
        cam_rotations.append(R_current.tolist())

    print(f"Total Waypoint Trajectory Robot: {len(trajectory)}")

    # Multi-baseline Triangulation: match (i, i+1) and (i, i+2) for dense coverage
    print("\nMelakukan Triangulasi Multi-View Densifikasi...")
    for step in [1, 2]:
        for i in range(len(images_paths) - step):
            j = i + step
            d1 = frames_data[i]
            d2 = frames_data[j]
            R1, t1 = poses[i]
            R2, t2 = poses[j]
            
            if d1['des'] is None or d2['des'] is None:
                continue
                
            matches = bf.knnMatch(d1['des'], d2['des'], k=2)
            good = [m for m, n in matches if len((m, n)) == 2 and m.distance < 0.75 * n.distance]
            if len(good) < 15:
                continue
                
            pts1 = np.float32([d1['kp'][m.queryIdx].pt for m in good])
            pts2 = np.float32([d2['kp'][m.trainIdx].pt for m in good])
            
            P1 = K @ np.hstack((R1, t1))
            P2 = K @ np.hstack((R2, t2))
            
            pts4d = cv2.triangulatePoints(P1, P2, pts1.T, pts2.T)
            pts3d = (pts4d[:3] / (pts4d[3] + 1e-8)).T
            
            valid = (pts4d[3] > 1e-4) & (pts3d[:, 2] > 0.5) & (pts3d[:, 2] < 22.0)
            valid_pts = pts3d[valid]
            valid_pts1 = pts1[valid].astype(int)
            
            for pt, uv in zip(valid_pts, valid_pts1):
                u = np.clip(uv[0], 0, d1['img'].shape[1] - 1)
                v = np.clip(uv[1], 0, d1['img'].shape[0] - 1)
                bgr = d1['img'][v, u]
                all_points.append(pt.tolist())
                all_colors.append([int(bgr[2]), int(bgr[1]), int(bgr[0])])

    all_points = np.array(all_points)
    all_colors = np.array(all_colors)
    print(f"\nTotal raw reconstructed points: {len(all_points):,}")

    # Statistical Outlier Removal
    med = np.median(all_points, axis=0)
    diff = np.abs(all_points - med)
    mad = np.median(diff, axis=0)
    valid_mask = np.all(diff < 3.2 * (mad + 1e-3), axis=1)
    
    clean_points = all_points[valid_mask]
    clean_colors = all_colors[valid_mask]
    print(f"Titik bersih setelah filter noise: {len(clean_points):,} titik")

    # Joint Normalization of Object and Robot Trajectory into same Three.js scene
    # Transform: OpenCV -> Three.js (X -> X, Y -> -Y, Z -> Z)
    traj_arr = np.array(trajectory)
    
    # Calculate coordinate shift based on object center
    center_x = float(np.median(clean_points[:, 0]))
    center_z = float(np.median(clean_points[:, 2]))
    min_y = float(np.min(-clean_points[:, 1]))
    
    span_obj = max(
        np.ptp(clean_points[:, 0]),
        np.ptp(-clean_points[:, 1]),
        np.ptp(clean_points[:, 2])
    )
    scale = 10.0 / span_obj if span_obj > 0 else 1.0

    # Transform points
    norm_pts = []
    norm_cols = []
    for p, c in zip(clean_points, clean_colors):
        nx = (p[0] - center_x) * scale
        ny = (-p[1] - min_y) * scale
        nz = (p[2] - center_z) * scale
        norm_pts.extend([round(float(nx), 4), round(float(ny), 4), round(float(nz), 4)])
        norm_cols.extend([round(c[0]/255.0, 3), round(c[1]/255.0, 3), round(c[2]/255.0, 3)])

    # Transform trajectory waypoints with identical transformation matrix
    norm_traj = []
    for t in traj_arr:
        tx = (t[0] - center_x) * scale
        ty = (-t[1] - min_y) * scale
        tz = (t[2] - center_z) * scale
        norm_traj.append([round(float(tx), 4), round(float(ty), 4), round(float(tz), 4)])

    result = {
        'num_points': len(clean_points),
        'points': norm_pts,
        'colors': norm_cols,
        'trajectory': norm_traj,
        'target_y': float(np.median(clean_points[:, 1]) * -1 - min_y) * scale
    }

    with open(output_json, 'w') as f:
        json.dump(result, f)
    print(f"Data 3D Mapping & Trajectory tersimpan di: {output_json}")

if __name__ == "__main__":
    imgs = r"c:\remote_ROV\photogrammetry_images"
    out_json = r"c:\remote_ROV\reconstruction_data.json"
    run_dense_sfm_and_track(imgs, out_json, max_images=45)
