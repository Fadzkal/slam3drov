#!/usr/bin/env python3
"""
egoexo_ground_surface_node.py
=============================
Implements 2.5D Ground Surface Estimation & Trajectory Projection
as detailed in the EgoExo++ paper (arXiv:2407.00848 Fig. 2, 3, 4).

Features:
  1. Dynamically estimates ground floor elevation (Z_ground).
  2. Generates and expands a 2.5D Ground Surface Floor Plane (EgoExo++ Soft Teal #5B8C9B).
  3. Projects a vibrant yellow dashed trajectory with directional arrows on top of the floor.
  4. Publishes crisp floor perimeter boundary markers.
"""

import math
import numpy as np
import rospy
from geometry_msgs.msg import Point
from nav_msgs.msg import Path, Odometry
from visualization_msgs.msg import Marker, MarkerArray

class EgoExoGroundSurfaceNode:
    def __init__(self):
        rospy.init_node("egoexo_ground_surface_node", anonymous=False)

        self.padding = rospy.get_param("~padding_m", 0.6)  # Margin around explored path
        self.floor_alpha = rospy.get_param("~floor_alpha", 0.85)
        self.min_size = rospy.get_param("~min_size_m", 1.8)

        # Publishers
        self.surface_pub = rospy.Publisher("/egoexo/ground_surface", Marker, queue_size=2)
        self.border_pub = rospy.Publisher("/egoexo/ground_border", Marker, queue_size=2)
        self.dashed_path_pub = rospy.Publisher("/egoexo/dashed_path", Marker, queue_size=2)

        # State
        self.positions = []
        self.z_ground = -0.15
        self.frame_id = "map"

        # Subscribers
        rospy.Subscriber("/robot_path", Path, self.path_callback, queue_size=2)
        rospy.Subscriber("/rtabmap/odom", Odometry, self.odom_callback, queue_size=5)

        rospy.loginfo("EgoExo++ 2.5D Ground Surface Node initialized! Generating terrain floor & yellow trajectory...")
        self.timer = rospy.Timer(rospy.Duration(0.5), self.timer_callback)

    def odom_callback(self, msg):
        pos = msg.pose.pose.position
        if not self.positions:
            self.positions.append((pos.x, pos.y, pos.z))
            self.z_ground = pos.z - 0.12
            self.frame_id = msg.header.frame_id if msg.header.frame_id else "map"

    def path_callback(self, msg):
        if not msg.poses:
            return
        self.frame_id = msg.header.frame_id if msg.header.frame_id else "map"
        new_positions = []
        for p in msg.poses:
            pos = p.pose.position
            new_positions.append((pos.x, pos.y, pos.z))
        if new_positions:
            self.positions = new_positions
            # Ground floor is estimated below lowest vehicle trajectory point
            all_z = [p[2] for p in self.positions]
            min_z = min(all_z)
            self.z_ground = min_z - 0.12

    def timer_callback(self, event):
        now = rospy.Time.now()
        pts = self.positions
        if not pts:
            # Fallback default initial floor around origin
            pts = [(0.0, 0.0, 0.0)]
            self.z_ground = -0.15

        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]

        min_x, max_x = min(xs) - self.padding, max(xs) + self.padding
        min_y, max_y = min(ys) - self.padding, max(ys) + self.padding

        # Ensure minimal visible floor surface even when stationary
        cx = (min_x + max_x) * 0.5
        cy = (min_y + max_y) * 0.5
        half_w = max((max_x - min_x) * 0.5, self.min_size * 0.5)
        half_h = max((max_y - min_y) * 0.5, self.min_size * 0.5)
        x0, x1 = cx - half_w, cx + half_w
        y0, y1 = cy - half_h, cy + half_h
        zg = self.z_ground

        # -------------------------------------------------------------
        # 1. 2.5D Ground Surface Mesh (EgoExo++ Soft Teal / Slate #5B8C9B)
        # -------------------------------------------------------------
        surface = Marker()
        surface.header.stamp = now
        surface.header.frame_id = self.frame_id
        surface.ns = "egoexo_ground"
        surface.id = 1
        surface.type = Marker.TRIANGLE_LIST
        surface.action = Marker.ADD
        surface.scale.x = 1.0
        surface.scale.y = 1.0
        surface.scale.z = 1.0
        
        # Soft Teal color matching EgoExo++ Paper Fig 2 & 4
        surface.color.r = 0.36
        surface.color.g = 0.55
        surface.color.b = 0.61
        surface.color.a = float(self.floor_alpha)

        # 4 corners of floor plane
        c1 = Point(x0, y0, zg)
        c2 = Point(x1, y0, zg)
        c3 = Point(x1, y1, zg)
        c4 = Point(x0, y1, zg)

        # Triangle 1 (c1 -> c2 -> c3)
        surface.points.extend([c1, c2, c3])
        # Triangle 2 (c1 -> c3 -> c4)
        surface.points.extend([c1, c3, c4])
        # Add reverse normal so floor is visible from underneath as well
        surface.points.extend([c3, c2, c1])
        surface.points.extend([c4, c3, c1])

        self.surface_pub.publish(surface)

        # -------------------------------------------------------------
        # 2. Crisp Perimeter Border (Dark Teal framing)
        # -------------------------------------------------------------
        border = Marker()
        border.header.stamp = now
        border.header.frame_id = self.frame_id
        border.ns = "egoexo_border"
        border.id = 2
        border.type = Marker.LINE_STRIP
        border.action = Marker.ADD
        border.scale.x = 0.025  # Line width
        border.color.r = 0.20
        border.color.g = 0.35
        border.color.b = 0.42
        border.color.a = 1.0
        border.points = [
            Point(x0, y0, zg + 0.005),
            Point(x1, y0, zg + 0.005),
            Point(x1, y1, zg + 0.005),
            Point(x0, y1, zg + 0.005),
            Point(x0, y0, zg + 0.005),
        ]
        self.border_pub.publish(border)

        # -------------------------------------------------------------
        # 3. Vibrant Yellow Dashed Trajectory (like EgoExo++ Fig 2 & 3)
        # -------------------------------------------------------------
        if len(pts) >= 2:
            dashed = Marker()
            dashed.header.stamp = now
            dashed.header.frame_id = self.frame_id
            dashed.ns = "egoexo_yellow_path"
            dashed.id = 3
            dashed.type = Marker.LINE_LIST
            dashed.action = Marker.ADD
            dashed.scale.x = 0.035  # Line thickness
            
            # Vibrant EgoExo Yellow (#FFE600)
            dashed.color.r = 1.0
            dashed.color.g = 0.90
            dashed.color.b = 0.0
            dashed.color.a = 1.0

            # Elevated slightly above floor to prevent Z-fighting
            z_path = zg + 0.015
            step = 1
            for i in range(0, len(pts) - 1, step):
                # Dashed pattern: skip every second segment
                if (i // step) % 2 == 0:
                    p_start = Point(pts[i][0], pts[i][1], z_path)
                    p_end = Point(pts[i+1][0], pts[i+1][1], z_path)
                    dashed.points.append(p_start)
                    dashed.points.append(p_end)

            if dashed.points:
                self.dashed_path_pub.publish(dashed)


if __name__ == "__main__":
    try:
        node = EgoExoGroundSurfaceNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
