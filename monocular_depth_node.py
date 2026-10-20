#!/usr/bin/env python3
import os
import struct
import numpy as np
import cv2
import onnxruntime as ort
import rospy
from sensor_msgs.msg import Image, PointCloud2, PointField, CameraInfo, Range
from std_msgs.msg import Float64
from cv_bridge import CvBridge
import sensor_msgs.point_cloud2 as pc2

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
        self.depth_scale = rospy.get_param("~depth_scale", 4.5)
        self.step = rospy.get_param("~point_step", 3)
        
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
        rospy.Subscriber("/camera/camera_info", CameraInfo, self.info_callback, queue_size=5)
        rospy.Subscriber(self.image_topic, Image, self.image_callback, queue_size=1, buff_size=2**24)
        if self.image_topic != "/camera/image_raw":
            rospy.Subscriber("/camera/image_raw", Image, self.fallback_image_callback, queue_size=1, buff_size=2**24)
        rospy.Subscriber("/sonar/ping1d/distance", Float64, self.ping_dist_callback, queue_size=5)
        rospy.Subscriber("/sonar/ping1d/range", Range, self.ping_range_callback, queue_size=5)
        rospy.loginfo(f"Hyperbolic Monocular AI Depth initialized! Listening to: {self.image_topic}")

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
        
        img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(img_rgb, (256, 256), interpolation=cv2.INTER_CUBIC)
        norm = resized.astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        norm = (norm - mean) / std
        input_tensor = np.transpose(norm, (2, 0, 1))[np.newaxis, ...].astype(np.float32)
        
        out = self.session.run(None, {self.input_name: input_tensor})[0]
        depth_raw = out[0]
        
        # Robust percentile clipping to eliminate outliers and glares
        p_low = np.percentile(depth_raw, 2)
        p_high = np.percentile(depth_raw, 98)
        depth_clamped = np.clip(depth_raw, p_low, p_high)
        
        # Normalize disparity to [0.0, 1.0] (1.0 = close, 0.0 = far)
        denom = max(p_high - p_low, 1e-4)
        disp_norm = (depth_clamped - p_low) / denom
        
        # Physical Hyperbolic Depth Mapping (Disparity -> True Metric Depth):
        # MiDaS memprediksi disparitas (inverse depth).
        # Transformasi fisik yang benar: Z = 1.0 / (alpha * disp_norm + beta)
        # Menghilangkan distorsi kerucut cembung dan menjaga dinding/lantai tetap datar!
        z_near = 0.35
        z_far = float(self.depth_scale)
        alpha = (1.0 / z_near) - (1.0 / z_far)
        beta = 1.0 / z_far
        depth_metric = 1.0 / (alpha * disp_norm + beta)
        
        # Ping1D Metric Scale Anchor Calibration:
        # Matches the monocular depth center field to true physical acoustic ground truth
        now = rospy.Time.now()
        if self.latest_ping_distance is not None and (now - self.latest_ping_time).to_sec() < 1.5:
            h_raw, w_raw = depth_metric.shape
            cy_c, cx_c = h_raw // 2, w_raw // 2
            # Center acoustic cone region (approx 10% center box)
            box_h = max(2, int(h_raw * 0.10))
            box_w = max(2, int(w_raw * 0.10))
            center_est = float(np.median(depth_metric[cy_c - box_h:cy_c + box_h, cx_c - box_w:cx_c + box_w]))
            if center_est > 0.15:
                scale_correction = float(self.latest_ping_distance) / center_est
                # Bound scaling factor to prevent anomalous spikes
                scale_correction = np.clip(scale_correction, 0.35, 2.8)
                depth_metric = depth_metric * scale_correction
        
        # Remove edge flare artifacts
        h_d, w_d = depth_metric.shape
        by = int(h_d * 0.05)
        bx = int(w_d * 0.05)
        depth_metric[:by, :] = depth_metric[by, :]
        depth_metric[-by:, :] = depth_metric[-by-1, :]
        depth_metric[:, :bx] = depth_metric[:, bx:bx+1]
        depth_metric[:, -bx:] = depth_metric[:, -bx-1:-bx]
        
        depth_metric_resized = cv2.resize(depth_metric.astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)
        
        # Common timestamp for perfect synchronization
        now = rospy.Time.now()
        
        depth_msg = self.bridge.cv2_to_imgmsg(depth_metric_resized.astype(np.float32), encoding="32FC1")
        depth_msg.header = msg.header
        depth_msg.header.stamp = now
        self.depth_pub.publish(depth_msg)
        self.synced_depth_pub.publish(depth_msg)
        
        # Publish synchronized RGB
        msg.header.stamp = now
        self.synced_rgb_pub.publish(msg)
        
        # Publish synchronized CameraInfo
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
            
            fx = max(float(K[0]), 10.0)
            cx = float(K[2])
            fy = max(float(K[4]), 10.0)
            cy = float(K[5])
        else:
            info = CameraInfo()
            info.header.stamp = now
            info.header.frame_id = msg.header.frame_id
            info.width = w
            info.height = h
            fx = 520.0 * (w / 640.0)
            fy = 520.0 * (h / 480.0)
            cx = w / 2.0
            cy = h / 2.0
            info.distortion_model = "plumb_bob"
            info.D = [0.0, 0.0, 0.0, 0.0, 0.0]
            info.K = [fx, 0.0, cx, 0.0, fy, cy, 0.0, 0.0, 1.0]
            info.P = [fx, 0.0, cx, 0.0, 0.0, fy, cy, 0.0, 0.0, 0.0, 1.0, 0.0]
            self.synced_info_pub.publish(info)
        
        # Always publish dense per-frame PointCloud2 for real-time 3D surface visualization
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
        
        # Filter NaN, Inf, out-of-range points, and outer flared border wings
        border_u = int(w * 0.05)
        border_v = int(h * 0.05)
        inner_mask = (u_coords >= border_u) & (u_coords <= (w - border_u)) & \
                     (v_coords >= border_v) & (v_coords <= (h - border_v))
        valid_mask = (Z > 0.25) & (Z < 5.0) & np.isfinite(X) & np.isfinite(Y) & np.isfinite(Z) & inner_mask
        
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
