#!/usr/bin/env python3
"""
rov_trajectory_node.py
======================
Monitors filtered ROV odometry (/odometry/filtered or /rtabmap/odom).
Publishes:
  - /robot_path              (nav_msgs/Path) -> live 3D trail in RViz
  - /rov/model_marker        (visualization_msgs/Marker) -> 3D ROV body marker in RViz
  - /rov/distance_travelled  (std_msgs/Float64) -> total distance traveled in meters
"""

import math
import rospy
from nav_msgs.msg import Path, Odometry
from geometry_msgs.msg import PoseStamped, Point
from visualization_msgs.msg import Marker
from std_msgs.msg import Float64


class RovTrajectoryNode:
    def __init__(self):
        rospy.init_node("rov_trajectory_node", anonymous=False)

        self.max_path_length = rospy.get_param("~max_path_length", 10000)
        # Deadband threshold: 4cm minimum movement to ignore stationary sensor noise
        self.min_dist_threshold = rospy.get_param("~min_step_m", 0.04)

        self.path_pub = rospy.Publisher("/robot_path", Path, queue_size=5)
        self.marker_pub = rospy.Publisher("/rov/model_marker", Marker, queue_size=5)
        self.dist_travelled_pub = rospy.Publisher("/rov/distance_travelled", Float64, queue_size=5)

        self.path = Path()
        self.path.header.frame_id = "odom"

        self.last_pos = None
        self.total_distance = 0.0
        self._last_ekf_time = rospy.Time(0)

        # Primary subscriber: fused EKF odometry
        rospy.Subscriber("/odometry/filtered", Odometry, self.odom_callback, queue_size=10)
        # Fallback subscriber: visual odometry directly from RTAB-Map
        rospy.Subscriber("/rtabmap/odom", Odometry, self.rtab_odom_callback, queue_size=10)

        rospy.loginfo("[RovTrajectoryNode] Tracking ROV trajectory and publishing to /robot_path & /rov/model_marker")

    def _process_pose(self, stamp, frame_id, pose):
        curr_x = pose.position.x
        curr_y = pose.position.y
        curr_z = pose.position.z

        # Check movement distance
        if self.last_pos is not None:
            dx = curr_x - self.last_pos[0]
            dy = curr_y - self.last_pos[1]
            dz = curr_z - self.last_pos[2]
            dist_step = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            # Anti-teleport filter: reject anomalous jumps > 0.4m in a single frame
            if dist_step > 0.40:
                return

            # Deadband filter: ignore jitter/noise smaller than 4cm
            if dist_step < self.min_dist_threshold:
                self._publish_marker(stamp, frame_id, pose)
                return
            self.total_distance += dist_step
        else:
            dist_step = 0.0

        self.last_pos = (curr_x, curr_y, curr_z)

        # Update Path
        p = PoseStamped()
        p.header.stamp = stamp
        p.header.frame_id = frame_id
        p.pose = pose

        self.path.header.stamp = stamp
        self.path.header.frame_id = frame_id
        self.path.poses.append(p)

        if len(self.path.poses) > self.max_path_length:
            self.path.poses.pop(0)

        self.path_pub.publish(self.path)
        self.dist_travelled_pub.publish(Float64(self.total_distance))
        self._publish_marker(stamp, frame_id, pose)

    def _publish_marker(self, stamp, frame_id, pose):
        marker = Marker()
        marker.header.stamp = stamp
        marker.header.frame_id = frame_id
        marker.ns = "bluerov2_body"
        marker.id = 0
        marker.type = Marker.CUBE
        marker.action = Marker.ADD
        marker.pose = pose
        # BlueROV2 dimensions
        marker.scale.x = 0.457
        marker.scale.y = 0.338
        marker.scale.z = 0.254
        marker.color.r = 0.95
        marker.color.g = 0.15
        marker.color.b = 0.15
        marker.color.a = 0.85
        marker.lifetime = rospy.Duration(0)
        self.marker_pub.publish(marker)

    def odom_callback(self, msg):
        self._last_ekf_time = rospy.Time.now()
        self._process_pose(msg.header.stamp, msg.header.frame_id, msg.pose.pose)

    def rtab_odom_callback(self, msg):
        if (rospy.Time.now() - self._last_ekf_time).to_sec() > 0.8:
            # Check covariance: skip lost odometry (9999) and crazy spikes
            cov = msg.pose.covariance[0] if len(msg.pose.covariance) > 0 else 0
            if 0.0 <= cov < 5.0:
                self._process_pose(msg.header.stamp, msg.header.frame_id, msg.pose.pose)


if __name__ == "__main__":
    try:
        node = RovTrajectoryNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
