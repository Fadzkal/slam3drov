@echo off
title Pembersih Database & Cache SLAM (Reset Pengujian Gagal)
echo ==========================================================
echo    PEMBERSIH DATABASE SLAM & CACHE PENGUJIAN GAGAL
echo ==========================================================
echo.
echo Sedang membersihkan database rtabmap.db dan log ROS di WSL...
wsl -d Ubuntu-20.04 -u fadzkal_luthfi -- bash -c "rm -f ~/.ros/rtabmap.db; rosclean purge -y 2>/dev/null || rm -rf ~/.ros/log/*"
echo.
echo Database rtabmap.db dan log ROS berhasil dibersihkan!
echo Sekarang Anda bisa mulai pengujian SLAM baru dengan kondisi database bersih.
echo.
pause
