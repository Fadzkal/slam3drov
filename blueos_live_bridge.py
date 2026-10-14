#!/usr/bin/env python3
import time
import json
import math
import urllib.request
import rospy
import tf2_ros
from geometry_msgs.msg import TransformStamped, PoseStamped
from nav_msgs.msg import Path, Odometry
from sensor_msgs.msg import Imu, Range
from std_msgs.msg import Float64

def euler_to_quaternion(roll, pitch, yaw):
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)

    qw = cr * cp * cy + sr * sp * sy
    qx = sr * cp * cy - cr * sp * sy
    qy = cr * sp * cy + sr * cp * sy
    qz = cr * cp * sy - sr * sp * cy
    return qx, qy, qz, qw

def main():
    rospy.init_node("blueos_live_bridge", anonymous=False)
    blueos_ip = rospy.get_param("~blueos_ip", "192.168.2.2")
    rate_hz = rospy.get_param("~rate", 20.0)
    publish_tf = rospy.get_param("~publish_tf", False)
    
    imu_pub = rospy.Publisher("/mavros/imu/data", Imu, queue_size=5)
    imu_pub_std = rospy.Publisher("/imu/data", Imu, queue_size=5)
    alt_pub = rospy.Publisher("/mavros/altitude", Float64, queue_size=5)
    bar30_depth_pub = rospy.Publisher("/bar30/depth", Float64, queue_size=5)
    ping1d_range_pub = rospy.Publisher("/sonar/ping1d/range", Range, queue_size=5)
    ping1d_dist_pub = rospy.Publisher("/sonar/ping1d/distance", Float64, queue_size=5)
    
    br = tf2_ros.TransformBroadcaster()

    base_url_comp1 = f"http://{blueos_ip}/mavlink2rest/mavlink/vehicles/1/components/1/messages"
    base_url_comp194 = f"http://{blueos_ip}/mavlink2rest/mavlink/vehicles/1/components/194/messages"
    rospy.loginfo(f"Connecting to BlueOS telemetry at {blueos_ip} (IMU, Bar30, Ping1D)...")
    
    rate = rospy.Rate(rate_hz)
    loop_count = 0
    
    while not rospy.is_shutdown():
        now = rospy.Time.now()
        loop_count += 1
        
        # 1. Fetch ATTITUDE & IMU (High rate: every iteration)
        try:
            req = urllib.request.urlopen(f"{base_url_comp1}/ATTITUDE", timeout=0.1)
            att = json.loads(req.read().decode())["message"]
            roll = att["roll"]
            pitch = att["pitch"]
            yaw = att["yaw"]
            qx, qy, qz, qw = euler_to_quaternion(roll, pitch, yaw)

            # RAW_IMU (optional for accel/gyro)
            req_imu = urllib.request.urlopen(f"{base_url_comp1}/RAW_IMU", timeout=0.1)
            raw_imu = json.loads(req_imu.read().decode())["message"]
            
            # Publish Imu Message
            imu_msg = Imu()
            imu_msg.header.stamp = now
            imu_msg.header.frame_id = "base_imu_link"
            imu_msg.orientation.x = qx
            imu_msg.orientation.y = qy
            imu_msg.orientation.z = qz
            imu_msg.orientation.w = qw
            imu_msg.angular_velocity.x = att.get("rollspeed", 0.0)
            imu_msg.angular_velocity.y = att.get("pitchspeed", 0.0)
            imu_msg.angular_velocity.z = att.get("yawspeed", 0.0)
            imu_msg.linear_acceleration.x = raw_imu.get("xacc", 0) * 9.80665 / 1000.0
            imu_msg.linear_acceleration.y = raw_imu.get("yacc", 0) * 9.80665 / 1000.0
            imu_msg.linear_acceleration.z = raw_imu.get("zacc", -1000) * 9.80665 / 1000.0
            imu_pub.publish(imu_msg)
            imu_pub_std.publish(imu_msg)

            # Broadcast TF: odom -> base_link (if enabled)
            if publish_tf:
                t = TransformStamped()
                t.header.stamp = now + rospy.Duration(0.1)
                t.header.frame_id = "odom"
                t.child_frame_id = "base_link"
                t.transform.translation.x = 0.0
                t.transform.translation.y = 0.0
                t.transform.translation.z = 0.0
                t.transform.rotation.x = qx
                t.transform.rotation.y = qy
                t.transform.rotation.z = qz
                t.transform.rotation.w = qw
                br.sendTransform(t)
        except Exception:
            pass

        # 2. Fetch Bar30 Hydrostatic Depth (from VFR_HUD or AHRS2)
        if loop_count % 2 == 0:
            try:
                req_vfr = urllib.request.urlopen(f"{base_url_comp1}/VFR_HUD", timeout=0.1)
                vfr = json.loads(req_vfr.read().decode())["message"]
                alt = float(vfr.get("alt", 0.0))
                depth_m = max(0.0, -alt)
                
                alt_pub.publish(Float64(alt))
                bar30_depth_pub.publish(Float64(depth_m))
            except Exception:
                try:
                    # Fallback to AHRS2
                    req_ahrs2 = urllib.request.urlopen(f"{base_url_comp1}/AHRS2", timeout=0.1)
                    ahrs2 = json.loads(req_ahrs2.read().decode())["message"]
                    alt = float(ahrs2.get("altitude", 0.0))
                    depth_m = max(0.0, -alt)
                    alt_pub.publish(Float64(alt))
                    bar30_depth_pub.publish(Float64(depth_m))
                except Exception:
                    pass

        # 3. Fetch Ping1D Sonar Distance (DISTANCE_SENSOR comp 194 or comp 1)
        if loop_count % 2 == 0:
            try:
                dist_sensor_data = None
                # Check component 194 first (dedicated Ping1D component ID in BlueOS)
                try:
                    req_dist = urllib.request.urlopen(f"{base_url_comp194}/DISTANCE_SENSOR", timeout=0.1)
                    dist_sensor_data = json.loads(req_dist.read().decode())["message"]
                except Exception:
                    # Fallback to component 1
                    req_dist = urllib.request.urlopen(f"{base_url_comp1}/DISTANCE_SENSOR", timeout=0.1)
                    dist_sensor_data = json.loads(req_dist.read().decode())["message"]

                if dist_sensor_data:
                    raw_cm = float(dist_sensor_data.get("current_distance", 0.0))
                    dist_m = raw_cm / 100.0
                    
                    if 0.15 <= dist_m <= 35.0:
                        range_msg = Range()
                        range_msg.header.stamp = now
                        range_msg.header.frame_id = "ping1d_sonar_link"
                        range_msg.radiation_type = Range.ULTRASOUND
                        range_msg.field_of_view = 0.5236  # ~30 degrees acoustic cone
                        range_msg.min_range = 0.20
                        range_msg.max_range = 30.0
                        range_msg.range = dist_m
                        
                        ping1d_range_pub.publish(range_msg)
                        ping1d_dist_pub.publish(Float64(dist_m))
            except Exception:
                pass

        rate.sleep()

if __name__ == "__main__":
    main()
