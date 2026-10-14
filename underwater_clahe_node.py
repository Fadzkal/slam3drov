#!/usr/bin/env python3
import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge

class UnderwaterClaheNode:
    def __init__(self):
        rospy.init_node('underwater_clahe_node')
        
        self.bridge = CvBridge()
        self.clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        
        self.target_width = rospy.get_param('~width', 960)
        self.target_height = rospy.get_param('~height', 540)
        
        self.last_stamp = None
        # Support both /image_raw and /camera/image_raw for seamless compatibility
        self.image_sub = rospy.Subscriber('/image_raw', Image, self.image_callback, queue_size=1, buff_size=2**24)
        self.image_sub_alt = rospy.Subscriber('/camera/image_raw', Image, self.image_callback, queue_size=1, buff_size=2**24)
        self.image_pub = rospy.Publisher('/camera/image_enhanced', Image, queue_size=1)
        self.info_pub = rospy.Publisher('/camera/camera_info', CameraInfo, queue_size=1)
        
        rospy.loginfo("Underwater CLAHE Enhancement Node running (IROS SVIn2 Architecture)")

    def image_callback(self, msg):
        if self.last_stamp is not None and msg.header.stamp == self.last_stamp:
            return
        self.last_stamp = msg.header.stamp
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            rospy.logerr(f"CvBridge Error: {e}")
            return
            
        # Resize to optimized processing resolution if needed
        if cv_image.shape[1] != self.target_width or cv_image.shape[0] != self.target_height:
            cv_image = cv2.resize(cv_image, (self.target_width, self.target_height), interpolation=cv2.INTER_AREA)

        # Apply CLAHE on Lightness (L channel in LAB color space)
        lab = cv2.cvtColor(cv_image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        cl = self.clahe.apply(l)
        enhanced_lab = cv2.merge((cl, a, b))
        enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        # Publish enhanced image
        out_msg = self.bridge.cv2_to_imgmsg(enhanced_bgr, encoding='bgr8')
        out_msg.header = msg.header
        self.image_pub.publish(out_msg)
        
        # Camera Info
        info = CameraInfo()
        info.header = msg.header
        info.width = self.target_width
        info.height = self.target_height
        fx = 0.625 * self.target_width
        fy = fx
        cx = self.target_width / 2.0
        cy = self.target_height / 2.0
        info.K = [fx, 0, cx, 0, fy, cy, 0, 0, 1]
        info.P = [fx, 0, cx, 0, 0, fy, cy, 0, 0, 0, 1, 0]
        self.info_pub.publish(info)

if __name__ == '__main__':
    node = UnderwaterClaheNode()
    rospy.spin()
