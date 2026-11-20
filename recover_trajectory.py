import sqlite3
import struct
import numpy as np

conn = sqlite3.connect('/home/fadzkal_luthfi/.ros/rtabmap.db')
c = conn.cursor()
rows = c.execute("SELECT id, stamp, pose FROM Node ORDER BY stamp ASC;").fetchall()

print(f"Total poses found: {len(rows)}")

poses = []
for node_id, stamp, pose_bytes in rows:
    if not pose_bytes or len(pose_bytes) != 48:
        continue
    # 12 floats: r11, r12, r13, tx, r21, r22, r23, ty, r31, r32, r33, tz
    vals = struct.unpack('12f', pose_bytes)
    R = np.array([
        [vals[0], vals[1], vals[2]],
        [vals[4], vals[5], vals[6]],
        [vals[8], vals[9], vals[10]]
    ])
    t = np.array([vals[3], vals[7], vals[11]])
    poses.append((stamp, t, R))

print(f"Unpacked {len(poses)} poses successfully!")
if poses:
    print(f"First pose t: {poses[0][1]}")
    print(f"Last pose t: {poses[-1][1]}")
    dist = sum(np.linalg.norm(poses[i][1] - poses[i-1][1]) for i in range(1, len(poses)))
    print(f"Total path distance: {dist:.4f} meters")

# Convert rotation matrix to quaternion
def rot_to_quat(R):
    tr = R[0,0] + R[1,1] + R[2,2]
    if tr > 0:
        S = np.sqrt(tr + 1.0) * 2
        qw = 0.25 * S
        qx = (R[2,1] - R[1,2]) / S
        qy = (R[0,2] - R[2,0]) / S
        qz = (R[1,0] - R[0,1]) / S
    elif (R[0,0] > R[1,1]) and (R[0,0] > R[2,2]):
        S = np.sqrt(1.0 + R[0,0] - R[1,1] - R[2,2]) * 2
        qw = (R[2,1] - R[1,2]) / S
        qx = 0.25 * S
        qy = (R[0,1] + R[1,0]) / S
        qz = (R[0,2] + R[2,0]) / S
    elif R[1,1] > R[2,2]:
        S = np.sqrt(1.0 + R[1,1] - R[0,0] - R[2,2]) * 2
        qw = (R[0,2] - R[2,0]) / S
        qx = (R[0,1] + R[1,0]) / S
        qy = 0.25 * S
        qz = (R[1,2] + R[2,1]) / S
    else:
        S = np.sqrt(1.0 + R[2,2] - R[0,0] - R[1,1]) * 2
        qw = (R[1,0] - R[0,1]) / S
        qx = (R[0,2] + R[2,0]) / S
        qy = (R[1,2] + R[2,1]) / S
        qz = 0.25 * S
    return qx, qy, qz, qw

# The poses in rtabmap.db are already in odom frame (ROS ENU)!
# Let's write TUM format for KeyFrameTrajectory.txt
# Note: In our viewer, it does R_align * [tx, ty, tz].
# R_align maps TUM optical [tx, ty, tz] to ROS ENU: x_enu = tz, y_enu = -tx, z_enu = -ty
# Inverse of R_align: tx_tum = -y_enu, ty_tum = -z_enu, tz_tum = x_enu
# R_tum = R_align^T * R_enu
R_align = np.array([
    [0.0, 0.0, 1.0],
    [-1.0, 0.0, 0.0],
    [0.0, -1.0, 0.0]
])
R_align_inv = R_align.T

lines_tum = []
for stamp, t_enu, R_enu in poses:
    t_tum = R_align_inv @ t_enu
    R_tum = R_align_inv @ R_enu
    qx, qy, qz, qw = rot_to_quat(R_tum)
    lines_tum.append(f"{stamp:.6f} {t_tum[0]:.7f} {t_tum[1]:.7f} {t_tum[2]:.7f} {qx:.7f} {qy:.7f} {qz:.7f} {qw:.7f}\n")

with open('/mnt/c/remote_ROV/KeyFrameTrajectory.txt', 'w') as f:
    f.writelines(lines_tum)

with open('/mnt/c/remote_ROV/export/KeyFrameTrajectory.txt', 'w') as f:
    f.writelines(lines_tum)

with open('/mnt/c/remote_ROV/export/KeyFrameTrajectory_20261022_191855.txt', 'w') as f:
    f.writelines(lines_tum)

print(f"Successfully recovered {len(lines_tum)} trajectory keyframes into KeyFrameTrajectory.txt!")
