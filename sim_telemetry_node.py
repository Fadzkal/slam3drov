#!/usr/bin/env python3
"""
sim_telemetry_node.py
=====================
Simulates realistic BlueROV2 telemetry (Bar30 depth, Ping1D sonar range, Pixhawk IMU)
for dry-run/playback testing when the physical ROV is not connected.
Allows full end-to-end testing of EKF, RTAB-Map SLAM, and RViz with recorded video.
"""

import math
import rospy
from geometry_msgs.msg import PoseWithCovarianceStamped
from sensor_msgs.msg import Imu, Range
from std_msgs.msg import Float64


def main():
    rospy.init_node("sim_telemetry_node", anonymous=False)

    rate_hz = rospy.get_param("~rate", 20.0)
    base_depth_m = rospy.get_param("~base_depth_m", 2.3)
    base_range_m = rospy.get_param("~base_range_m", 1.85)

    depth_pub = rospy.Publisher("/bar30/pose_depth", PoseWithCovarianceStamped, queue_size=5)
    range_pub = rospy.Publisher("/sonar/ping1d/range", Range, queue_size=5)
    dist_cm_pub = rospy.Publisher("/sonar/ping1d/dist", Float64, queue_size=5)
    dist_m_pub = rospy.Publisher("/sonar/ping1d/distance", Float64, queue_size=5)
    imu_pub = rospy.Publisher("/mavros/imu/data", Imu, queue_size=5)

    rate = rospy.Rate(rate_hz)
    start_time = rospy.Time.now().to_sec()

    rospy.loginfo("[SimTelemetry] Simulating Bar30, Ping1D, and IMU telemetry for offline test...")

    while not rospy.is_shutdown():
        now = rospy.Time.now()
        t = now.to_sec() - start_time

        # Gentle subsea hydro-dynamic bobbing
        depth_osc = 0.05 * math.sin(0.4 * t)
        curr_depth = base_depth_m + depth_osc

        # Ping1D reading oscillation
        range_osc = 0.12 * math.cos(0.5 * t)
        curr_range = max(0.4, base_range_m + range_osc)

        # 1. Bar30 Hydrostatic Depth
        pose_msg = PoseWithCovarianceStamped()
        pose_msg.header.stamp = now
        pose_msg.header.frame_id = "odom"
        pose_msg.pose.pose.position.z = -curr_depth
        pose_msg.pose.pose.orientation.w = 1.0
        cov = [0.0] * 36
        cov[14] = 0.0001
        pose_msg.pose.covariance = cov
        depth_pub.publish(pose_msg)

        # 2. Ping1D Sonar Range
        range_msg = Range()
        range_msg.header.stamp = now
        range_msg.header.frame_id = "ping1d_sonar_link"
        range_msg.radiation_type = Range.ULTRASOUND
        range_msg.field_of_view = 0.5236  # ~30 deg acoustic cone
        range_msg.min_range = 0.20
        range_msg.max_range = 30.0
        range_msg.range = curr_range
        range_pub.publish(range_msg)
        dist_cm_pub.publish(Float64(curr_range * 100.0))
        dist_m_pub.publish(Float64(curr_range))

        # 3. IMU Orientation & Gyro
        imu_msg = Imu()
        imu_msg.header.stamp = now
        imu_msg.header.frame_id = "base_imu_link"
        roll = 0.015 * math.sin(0.6 * t)
        pitch = 0.010 * math.cos(0.5 * t)
        # Small angle approximation for quaternion
        imu_msg.orientation.x = roll * 0.5
        imu_msg.orientation.y = pitch * 0.5
        imu_msg.orientation.z = 0.0
        imu_msg.orientation.w = 1.0
        imu_msg.angular_velocity.x = 0.015 * 0.6 * math.cos(0.6 * t)
        imu_msg.angular_velocity.y = -0.010 * 0.5 * math.sin(0.5 * t)
        imu_msg.angular_velocity.z = 0.0
        imu_pub.publish(imu_msg)

        rate.sleep()


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
