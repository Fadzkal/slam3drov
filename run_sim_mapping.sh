#!/usr/bin/env bash
# =============================================================================
# run_sim_mapping.sh
# BlueROV2 Subsea 3D Mapping - Offline Replay & RViz Visualization
# =============================================================================

set -e

echo "=========================================================="
echo "   BlueROV2 Subsea 3D Mapping - Offline Replay Mode       "
echo "=========================================================="
echo "Mode ini memutar rekaman video bawah air nyata (Site-113 Steel Container)"
echo "dan menjalankan seluruh pipeline SLAM 3D & fusi sensor ke RViz"
echo "tanpa memerlukan BlueROV2 fisik tercolok!"
echo ""

source /opt/ros/noetic/setup.bash
source ~/catkin_ws/devel/setup.bash

echo "Membuka RViz dan memproses 3D SLAM..."
roslaunch subsea_3d_mapping sim_subsea_mapping.launch "$@"
