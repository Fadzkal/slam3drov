#!/usr/bin/env python3
"""
monocular_depth_node.py
=============================================================================
Node Inferensi AI Dense Monocular Depth (MiDaS DPT ONNX) dengan
Scale Anchoring Geometris ORB-SLAM3 dan Koreksi Anti-Kubah (Planar Cosine).

Fitur Utama:
1. Inferensi MiDaS ONNX FP32 berkecepatan tinggi (~12.5 FPS).
2. Koreksi Anti-Kubah/Anti-Barrel (Spherical-to-Planar Ray Cosine):
   Mengeliminasi kelengkungan kubah/parabola pada dinding dan pintu,
   sehingga permukaan datar tetap rigid dan lurus.
3. Scale Anchoring Geometris ORB-SLAM3:
   Mengunci skala metrik depth secara real-time terhadap MapPoints 3D
   yang ditriangulasi oleh Bundle Adjustment ORB-SLAM3.
4. Temporal Smoothing (EMA):
   Menstabilkan dynamic range dan menghilangkan jitter kedalaman antar frame.
5. Sinkronisasi multi-topik ROS untuk RTAB-Map SLAM dan RViz.
=============================================================================
"""

import os
import struct
import numpy as np
import cv2
import onnxruntime as ort
import rospy
from sensor_msgs.msg import Image, PointCloud2, PointField, CameraInfo, Range
from nav_msgs.msg import Odometry
from std_msgs.msg import Float64
from cv_bridge import CvBridge
import sensor_msgs.point_cloud2 as pc2

def quat_to_rot_matrix(qx, qy, qz, qw):
    """Konversi quaternion ke matriks rotasi 3x3 (numpy)."""
    norm = np.sqrt(qx*qx + qy*qy + qz*qz + qw*qw)
    if norm < 1e-6:
        return np.eye(3, dtype=np.float32)
    qx, qy, qz, qw = qx/norm, qy/norm, qz/norm, qw/norm
    return np.array([
        [1.0 - 2.0*(qy*qy + qz*qz), 2.0*(qx*qy - qz*qw),       2.0*(qx*qz + qy*qw)],
        [2.0*(qx*qy + qz*qw),       1.0 - 2.0*(qx*qx + qz*qz), 2.0*(qy*qz - qx*qw)],
        [2.0*(qx*qz - qy*qw),       2.0*(qy*qz + qx*qw),       1.0 - 2.0*(qx*qx + qy*qy)]
    ], dtype=np.float32)

class MonocularDepthNode:
    def __init__(self):
        rospy.init_node("monocular_depth_node", anonymous=False)
        
        model_path = rospy.get_param(
            "~model_path",
            os.path.expanduser("~/catkin_ws/src/subsea_3d_mapping/models/model-small.onnx")
        )
        rospy.loginfo(f"Loading MiDaS depth model from: {model_path}")
        so = ort.SessionOptions()
        so.intra_op_num_threads = 4
        so.inter_op_num_threads = 2
        so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        self.session = ort.InferenceSession(model_path, sess_options=so, providers=['CPUExecutionProvider'])
        self.input_name = self.session.get_inputs()[0].name
        
        self.bridge = CvBridge()
        self.depth_scale = rospy.get_param("~depth_scale", 3.8)
        self.max_depth_range = rospy.get_param("~max_depth_range", 3.5)
        self.step = rospy.get_param("~point_step", 3)
        self._prev_depth = None
        
        # State Temporal EMA Dynamic Range
        self._ema_p_low = None
        self._ema_p_high = None

        # ORB-SLAM3 Sparse Anchoring State
        self.latest_odom_pose = None
        self.latest_odom_time = rospy.Time(0)
        self.sparse_pts_world = None
        self.slam_scale = 1.0
        
        # Ping1D Sonar Metric Anchor State
        self.latest_ping_distance = None
        self.latest_ping_time = rospy.Time(0)
        
        # Publishers for raw and synced streams
        self.depth_pub = rospy.Publisher("/camera/depth/image", Image, queue_size=2)
        self.points_pub = rospy.Publisher("/camera/depth/points", PointCloud2, queue_size=2)
        
        # Synchronized publishers for RTAB-Map SLAM & Odometry
        self.synced_rgb_pub = rospy.Publisher("/camera/synced/image", Image, queue_size=5)
        self.synced_depth_pub = rospy.Publisher("/camera/synced/depth", Image, queue_size=5)
        self.synced_info_pub = rospy.Publisher("/camera/synced/camera_info", CameraInfo, queue_size=5)
        
        self._last_depth_time = rospy.Time(0)
        self.last_info = None
        self._last_enhanced_time = rospy.Time(0)
        self.image_topic = rospy.get_param("~image_topic", "/camera/image_raw")
        
        # Subscribers
        rospy.Subscriber("/camera/camera_info", CameraInfo, self.info_callback, queue_size=5)
        rospy.Subscriber(self.image_topic, Image, self.image_callback, queue_size=1, buff_size=2**24)
        if self.image_topic != "/camera/image_raw":
            rospy.Subscriber("/camera/image_raw", Image, self.fallback_image_callback, queue_size=1, buff_size=2**24)
            
        rospy.Subscriber("/rtabmap/odom", Odometry, self.odom_callback, queue_size=5)
        rospy.Subscriber("/orb_slam3/sparse_points", PointCloud2, self.sparse_pts_callback, queue_size=2)
        rospy.Subscriber("/sonar/ping1d/distance", Float64, self.ping_dist_callback, queue_size=5)
        rospy.Subscriber("/sonar/ping1d/range", Range, self.ping_range_callback, queue_size=5)
        
        rospy.loginfo(f"Planar Corrected Monocular Depth Node ready! Listening to: {self.image_topic}")

    def odom_callback(self, msg):
        self.latest_odom_pose = msg.pose.pose
        self.latest_odom_time = msg.header.stamp

    def sparse_pts_callback(self, msg):
        try:
            pts = list(pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True))
            if pts:
                self.sparse_pts_world = np.array(pts, dtype=np.float32)
        except Exception:
            pass

    def fallback_image_callback(self, msg):
        if (rospy.Time.now() - self._last_enhanced_time).to_sec() > 1.0:
            self.image_callback(msg)

    def ping_dist_callback(self, msg):
        if 0.20 <= msg.data <= 30.0:
            self.latest_ping_distance = msg.data
            self.latest_ping_time = rospy.Time.now()

    def ping_range_callback(self, msg):
        if 0.20 <= msg.range <= 30.0:
            self.latest_ping_distance = msg.range
            self.latest_ping_time = rospy.Time.now()

    def info_callback(self, msg):
        self.last_info = msg

    def image_callback(self, msg):
        now = rospy.Time.now()
        # Throttle to max 12.5 FPS so CPU has plenty of headroom for RViz & RTAB-Map
        if (now - self._last_depth_time).to_sec() < 0.08:
            return
        self._last_depth_time = now
        self._last_image_time = now
        try:
            cv_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:
            rospy.logerr(f"cv_bridge error: {e}")
            return
            
        h, w = cv_img.shape[:2]
        
        # 1. Inferensi Model MiDaS DPT (Disparitas Relatif)
        img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(img_rgb, (256, 256), interpolation=cv2.INTER_CUBIC)
        norm = resized.astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        norm = (norm - mean) / std
        input_tensor = np.transpose(norm, (2, 0, 1))[np.newaxis, ...].astype(np.float32)
        
        out = self.session.run(None, {self.input_name: input_tensor})[0]
        depth_raw = out[0]
        
        # 2. Robust Percentile Clipping dengan Temporal EMA
        # Menjaga dynamic range tetap stabil sehingga dinding tidak berdenyut/mengembang antar frame
        p_low = float(np.percentile(depth_raw, 3))
        p_high = float(np.percentile(depth_raw, 97))
        if self._ema_p_low is None:
            self._ema_p_low = p_low
            self._ema_p_high = p_high
        else:
            self._ema_p_low = 0.85 * self._ema_p_low + 0.15 * p_low
            self._ema_p_high = 0.85 * self._ema_p_high + 0.15 * p_high
            
        denom = max(self._ema_p_high - self._ema_p_low, 1e-4)
        depth_clamped = np.clip(depth_raw, self._ema_p_low, self._ema_p_high)
        disp_norm = (depth_clamped - self._ema_p_low) / denom
        
        # 3. Formulasi Pemetaan Hiperbolik (Disparity -> Metric Depth)
        z_near = 0.45
        z_far = float(self.depth_scale)
        alpha = (1.0 / z_near) - (1.0 / z_far)
        beta = 1.0 / z_far
        depth_metric = 1.0 / (alpha * disp_norm + beta)

        # Resize ke resolusi asli kamera sebelum unproject
        depth_metric_resized = cv2.resize(depth_metric.astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)

        # 4. Ambil Parameter Intrinsik Kamera
        has_valid_info = (
            self.last_info is not None and
            len(self.last_info.K) == 9 and
            self.last_info.K[0] > 10.0 and
            self.last_info.K[4] > 10.0
        )
        if has_valid_info:
            orig_w = self.last_info.width if self.last_info.width > 0 else w
            orig_h = self.last_info.height if self.last_info.height > 0 else h
            scale_x = w / float(orig_w)
            scale_y = h / float(orig_h)
            fx = max(float(self.last_info.K[0]) * scale_x, 10.0)
            fy = max(float(self.last_info.K[4]) * scale_y, 10.0)
            cx = float(self.last_info.K[2]) * scale_x
            cy = float(self.last_info.K[5]) * scale_y
        else:
            fx = 520.0 * (w / 640.0)
            fy = 520.0 * (h / 480.0)
            cx = w / 2.0
            cy = h / 2.0

        # 5. ORB-SLAM3 Sparse-to-Dense Metric Anchoring
        # Memadukan titik-titik triangulasi ORB-SLAM3 untuk mengunci skala metrik absolut depth AI
        now = rospy.Time.now()
        b_anchored = False
        if (self.sparse_pts_world is not None and 
            self.latest_odom_pose is not None and 
            (now - self.latest_odom_time).to_sec() < 1.0):
            try:
                p = self.latest_odom_pose.position
                o = self.latest_odom_pose.orientation
                t_w = np.array([p.x, p.y, p.z], dtype=np.float32)
                R_odom = quat_to_rot_matrix(o.x, o.y, o.z, o.w)
                
                # Transformasi dari world odom ke camera optical frame:
                # P_cam_opt = R_odom^T * (P_world - t_w)
                diff = self.sparse_pts_world - t_w
                pts_cam = (R_odom.T @ diff.T).T
                
                Xc = pts_cam[:, 0]
                Yc = pts_cam[:, 1]
                Zc = pts_cam[:, 2]
                
                valid = (Zc > 0.35) & (Zc < 4.5)
                if np.count_nonzero(valid) >= 6:
                    Xc_v = Xc[valid]
                    Yc_v = Yc[valid]
                    Zc_v = Zc[valid]
                    
                    u_pts = np.round(fx * (Xc_v / Zc_v) + cx).astype(np.int32)
                    v_pts = np.round(fy * (Yc_v / Zc_v) + cy).astype(np.int32)
                    
                    in_img = (u_pts >= 15) & (u_pts < w - 15) & (v_pts >= 15) & (v_pts < h - 15)
                    if np.count_nonzero(in_img) >= 6:
                        u_valid = u_pts[in_img]
                        v_valid = v_pts[in_img]
                        z_gt = Zc_v[in_img]
                        
                        z_pred_samples = depth_metric_resized[v_valid, u_valid]
                        valid_samples = (z_pred_samples > 0.2) & np.isfinite(z_pred_samples)
                        if np.count_nonzero(valid_samples) >= 6:
                            ratios = z_gt[valid_samples] / z_pred_samples[valid_samples]
                            med_ratio = float(np.median(ratios))
                            if 0.40 <= med_ratio <= 2.5:
                                self.slam_scale = 0.88 * self.slam_scale + 0.12 * med_ratio
                                depth_metric_resized = depth_metric_resized * self.slam_scale
                                b_anchored = True
                                rospy.loginfo_throttle(5.0, f"[Anchor ORB-SLAM3] Skala terkunci via {len(ratios)} MapPoints: s={self.slam_scale:.3f}")
            except Exception:
                pass

        # 6. Fallback Kalibrasi Ping1D Sonar (jika ORB-SLAM3 belum aktif)
        if not b_anchored and self.latest_ping_distance is not None and (now - self.latest_ping_time).to_sec() < 1.5:
            cy_c, cx_c = h // 2, w // 2
            box_h = max(2, int(h * 0.10))
            box_w = max(2, int(w * 0.10))
            center_est = float(np.median(depth_metric_resized[cy_c - box_h:cy_c + box_h, cx_c - box_w:cx_c + box_w]))
            if center_est > 0.15:
                scale_correction = float(self.latest_ping_distance) / center_est
                scale_correction = np.clip(scale_correction, 0.35, 2.8)
                depth_metric_resized = depth_metric_resized * scale_correction

        # 7. Koreksi Anti-Kubah/Anti-Barrel (Spherical-to-Planar Ray Cosine):
        # MiDaS memprediksi jarak radial Euclidean sepanjang sinar kamera R = sqrt(X^2 + Y^2 + Z^2).
        # Tanpa koreksi cos(theta), titik di sudut gambar terdorong menjauh sebesar 1/cos(theta) (+26%),
        # menyebabkan koridor/dinding datar melengkung cembung membentuk kubah.
        u_grid_full, v_grid_full = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
        xn = (u_grid_full - cx) / fx
        yn = (v_grid_full - cy) / fy
        ray_cos = 1.0 / np.sqrt(1.0 + xn**2 + yn**2)
        depth_metric_resized = depth_metric_resized * ray_cos

        # 8. Perataan Temporal EMA antar Frame
        if self._prev_depth is not None and self._prev_depth.shape == depth_metric_resized.shape:
            depth_metric_resized = 0.65 * self._prev_depth + 0.35 * depth_metric_resized
        self._prev_depth = depth_metric_resized.copy()

        # 9. Inner Boundary Masking (6% margin) & Distance Cutoff
        by = max(2, int(h * 0.06))
        bx = max(2, int(w * 0.06))
        depth_metric_resized[:by, :] = np.nan
        depth_metric_resized[-by:, :] = np.nan
        depth_metric_resized[:, :bx] = np.nan
        depth_metric_resized[:, -bx:] = np.nan

        depth_metric_resized[depth_metric_resized > float(self.max_depth_range)] = np.nan
        depth_metric_resized[depth_metric_resized < 0.28] = np.nan
        
        # 10. Publikasi Gambar Kedalaman (32FC1)
        now = rospy.Time.now()
        depth_msg = self.bridge.cv2_to_imgmsg(depth_metric_resized.astype(np.float32), encoding="32FC1")
        depth_msg.header = msg.header
        depth_msg.header.stamp = now
        self.depth_pub.publish(depth_msg)
        self.synced_depth_pub.publish(depth_msg)
        
        # Publikasi Synchronized RGB
        msg.header.stamp = now
        self.synced_rgb_pub.publish(msg)
        
        # Publikasi Synchronized CameraInfo
        if has_valid_info:
            info = CameraInfo()
            info.header.stamp = now
            info.header.frame_id = msg.header.frame_id
            info.width = w
            info.height = h
            info.distortion_model = self.last_info.distortion_model
            info.D = list(self.last_info.D)
            
            K = list(self.last_info.K)
            K[0] *= scale_x
            K[2] *= scale_x
            K[4] *= scale_y
            K[5] *= scale_y
            info.K = K
            
            P = list(self.last_info.P)
            if len(P) == 12:
                P[0] *= scale_x
                P[2] *= scale_x
                P[5] *= scale_y
                P[6] *= scale_y
            info.P = P
            self.synced_info_pub.publish(info)
        else:
            info = CameraInfo()
            info.header.stamp = now
            info.header.frame_id = msg.header.frame_id
            info.width = w
            info.height = h
            info.distortion_model = "plumb_bob"
            info.D = [0.0, 0.0, 0.0, 0.0, 0.0]
            info.K = [fx, 0.0, cx, 0.0, fy, cy, 0.0, 0.0, 1.0]
            info.P = [fx, 0.0, cx, 0.0, 0.0, fy, cy, 0.0, 0.0, 0.0, 1.0, 0.0]
            self.synced_info_pub.publish(info)
        
        # 11. Publikasi Real-Time PointCloud2 untuk Visualisasi Permukaan 3D
        step = max(1, int(self.step))
        u_coords, v_coords = np.meshgrid(np.arange(0, w, step), np.arange(0, h, step))
        Z = depth_metric_resized[v_coords, u_coords].astype(np.float32)
        X = ((u_coords - cx) * Z / fx).astype(np.float32)
        Y = ((v_coords - cy) * Z / fy).astype(np.float32)
        
        rgb_down = cv_img[v_coords, u_coords]
        r = rgb_down[:, :, 2].astype(np.uint32)
        g = rgb_down[:, :, 1].astype(np.uint32)
        b = rgb_down[:, :, 0].astype(np.uint32)
        rgb_packed = (r << 16) | (g << 8) | b
        rgb_float = np.frombuffer(rgb_packed.tobytes(), dtype=np.float32).reshape(X.shape)
        
        border_u = int(w * 0.05)
        border_v = int(h * 0.05)
        inner_mask = (u_coords >= border_u) & (u_coords <= (w - border_u)) & \
                     (v_coords >= border_v) & (v_coords <= (h - border_v))
        valid_mask = (Z > 0.28) & (Z < float(self.max_depth_range)) & np.isfinite(X) & np.isfinite(Y) & np.isfinite(Z) & inner_mask
        
        X_val = X[valid_mask]
        Y_val = Y[valid_mask]
        Z_val = Z[valid_mask]
        rgb_val = rgb_float[valid_mask]
        
        points = np.stack([X_val, Y_val, Z_val, rgb_val], axis=-1)
        fields = [
            PointField('x', 0, PointField.FLOAT32, 1),
            PointField('y', 4, PointField.FLOAT32, 1),
            PointField('z', 8, PointField.FLOAT32, 1),
            PointField('rgb', 12, PointField.FLOAT32, 1)
        ]
        
        pc2_msg = pc2.create_cloud(msg.header, fields, points)
        self.points_pub.publish(pc2_msg)

if __name__ == "__main__":
    try:
        node = MonocularDepthNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
