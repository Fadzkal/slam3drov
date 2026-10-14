#!/usr/bin/env python3
"""
depth_to_pose_publisher.py
==========================
Converts Bar30 hydrostatic depth reading and Ping1D acoustic sonar distance
into ROS messages for robot_localization EKF and RTAB-Map SLAM.

Dual-redundant pipeline:
  1. Subscribes to MAVROS topics if available (/mavros/altitude, etc.)
  2. Falls back to BlueOS REST API (mavlink2rest @ 192.168.2.2)

Topics published:
  /bar30/pose_depth    -> geometry_msgs/PoseWithCovarianceStamped  (for EKF Z-constraint)
  /sonar/ping1d/range  -> sensor_msgs/Range                        (for RTAB-Map & RViz cone)
  /sonar/ping1d/dist   -> std_msgs/Float64                         (metric distance in cm)
  /sonar/ping1d/distance -> std_msgs/Float64                       (metric distance in m)
"""

import json
import math
import urllib.request
import rospy
from geometry_msgs.msg import PoseWithCovarianceStamped
from sensor_msgs.msg import Range
from std_msgs.msg import Float64


class SensorBridgeNode:
    def __init__(self):
        rospy.init_node("sensor_bridge", anonymous=False)

        self.blueos_ip = rospy.get_param("~blueos_ip", "192.168.2.2")
        self.rate_hz   = rospy.get_param("~rate_hz", 15.0)

        # Bar30 depth covariance (m^2). Bar30 has ±2mm accuracy -> 0.0001 m^2
        self.depth_cov = rospy.get_param("~depth_covariance", 0.0001)

        # Ping1D valid range bounds
        self.ping_min_m = rospy.get_param("~ping_min_m", 0.20)
        self.ping_max_m = rospy.get_param("~ping_max_m", 30.0)

        # Median filter buffer for Ping1D (reject acoustic multipath spikes)
        self._ping_buf = []
        self._ping_buf_size = 5

        # Cache from MAVROS callbacks if active
        self._mavros_depth = None
        self._mavros_depth_time = rospy.Time(0)

        self.depth_pub = rospy.Publisher(
            "/bar30/pose_depth",
            PoseWithCovarianceStamped,
            queue_size=5
        )
        self.range_pub = rospy.Publisher(
            "/sonar/ping1d/range",
            Range,
            queue_size=5
        )
        self.dist_cm_pub = rospy.Publisher(
            "/sonar/ping1d/dist",
            Float64,
            queue_size=5
        )
        self.dist_m_pub = rospy.Publisher(
            "/sonar/ping1d/distance",
            Float64,
            queue_size=5
        )

        # Listen to MAVROS altitude if present
        rospy.Subscriber("/mavros/altitude", Float64, self._mavros_alt_cb, queue_size=5)

        # URL bases for BlueOS REST API fallback
        self._base1   = f"http://{self.blueos_ip}/mavlink2rest/mavlink/vehicles/1/components/1/messages"
        self._base194 = f"http://{self.blueos_ip}/mavlink2rest/mavlink/vehicles/1/components/194/messages"

        rospy.loginfo(f"[SensorBridge] Initialized for BlueOS at {self.blueos_ip}")
        rospy.loginfo("[SensorBridge] Publishing /bar30/pose_depth and /sonar/ping1d/range")

    def _mavros_alt_cb(self, msg):
        # ArduSub convention: negative altitude = underwater depth
        alt = msg.data
        if alt < 0:
            self._mavros_depth = -alt
            self._mavros_depth_time = rospy.Time.now()

    def _fetch(self, url, timeout=0.10):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                return json.loads(resp.read().decode())
        except Exception:
            return None

    def _median_filtered_ping(self, raw_m):
        """Apply 5-sample median filter to Ping1D distance readings."""
        self._ping_buf.append(raw_m)
        if len(self._ping_buf) > self._ping_buf_size:
            self._ping_buf.pop(0)
        buf_sorted = sorted(self._ping_buf)
        return buf_sorted[len(buf_sorted) // 2]

    def spin(self):
        rate = rospy.Rate(self.rate_hz)
        while not rospy.is_shutdown():
            now = rospy.Time.now()

            # --- 1. Bar30 Depth ---
            depth_m = None

            # Check if fresh MAVROS depth received in last 0.5s
            if (now - self._mavros_depth_time).to_sec() < 0.5 and self._mavros_depth is not None:
                depth_m = self._mavros_depth
            else:
                # Fallback to BlueOS REST API
                data = self._fetch(f"{self._base1}/VFR_HUD")
                if data and "message" in data:
                    alt = float(data["message"].get("alt", 0.0))
                    depth_m = max(0.0, -alt)
                else:
                    data = self._fetch(f"{self._base1}/AHRS2")
                    if data and "message" in data:
                        alt = float(data["message"].get("altitude", 0.0))
                        depth_m = max(0.0, -alt)

            if depth_m is not None:
                pose_msg = PoseWithCovarianceStamped()
                pose_msg.header.stamp = now
                pose_msg.header.frame_id = "odom"
                # In ROS ENU: Z positive = up. Underwater depth = negative Z.
                pose_msg.pose.pose.position.z = -depth_m
                pose_msg.pose.pose.orientation.w = 1.0
                # 6x6 covariance: only Z (index 14) is set
                cov = [0.0] * 36
                cov[14] = self.depth_cov
                pose_msg.pose.covariance = cov
                self.depth_pub.publish(pose_msg)

            # --- 2. Ping1D Sonar (DISTANCE_SENSOR from component 194 or fallback 1) ---
            dist_data = self._fetch(f"{self._base194}/DISTANCE_SENSOR")
            if dist_data is None:
                dist_data = self._fetch(f"{self._base1}/DISTANCE_SENSOR")

            if dist_data and "message" in dist_data:
                raw_cm  = float(dist_data["message"].get("current_distance", 0.0))
                raw_m   = raw_cm / 100.0

                if self.ping_min_m <= raw_m <= self.ping_max_m:
                    filtered_m = self._median_filtered_ping(raw_m)

                    range_msg = Range()
                    range_msg.header.stamp    = now
                    range_msg.header.frame_id = "ping1d_sonar_link"
                    range_msg.radiation_type  = Range.ULTRASOUND
                    range_msg.field_of_view   = 0.5236   # ~30 deg acoustic cone
                    range_msg.min_range        = self.ping_min_m
                    range_msg.max_range        = self.ping_max_m
                    range_msg.range            = filtered_m
                    self.range_pub.publish(range_msg)
                    self.dist_cm_pub.publish(Float64(filtered_m * 100.0))
                    self.dist_m_pub.publish(Float64(filtered_m))

            rate.sleep()


if __name__ == "__main__":
    try:
        SensorBridgeNode().spin()
    except rospy.ROSInterruptException:
        pass
