/**
 * orb_slam3_odom_node.cpp
 * ============================================================================
 * Fusi Cerdas: ORB-SLAM3 6-DoF Odometry Tracker untuk RTAB-Map & Depth AI
 * ----------------------------------------------------------------------------
 * Menghubungkan pelacakan rotasi/translasi kamera 100% presisi dari ORB-SLAM3
 * ke dalam sistem Dense Reconstruction RTAB-Map dan Depth AI (MiDaS).
 * ============================================================================
 */

#include <iostream>
#include <algorithm>
#include <fstream>
#include <chrono>
#include <memory>
#include <string>

#include <ros/ros.h>
#include <cv_bridge/cv_bridge.h>
#include <image_transport/image_transport.h>
#include <sensor_msgs/Image.h>
#include <sensor_msgs/CameraInfo.h>
#include <nav_msgs/Odometry.h>
#include <geometry_msgs/PoseStamped.h>
#include <geometry_msgs/TransformStamped.h>
#include <tf2_ros/transform_broadcaster.h>
#include <std_msgs/String.h>

#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/videoio/videoio.hpp>

#include <System.h>

using namespace std;

class OrbSlam3OdomNode
{
public:
    OrbSlam3OdomNode(ros::NodeHandle &nh, ros::NodeHandle &pnh)
        : nh_(nh), pnh_(pnh), it_(nh), mbTrackingOk(false)
    {
        // 1. Baca Parameter ROS
        pnh_.param<string>("voc_file", strVocFile_, "/home/fadzkal_luthfi/slam_ws/ORB_SLAM3/Vocabulary/ORBvoc.txt");
        pnh_.param<string>("settings_file", strSettingsFile_, "/home/fadzkal_luthfi/slam_ws/webcam_640.yaml");
        pnh_.param<string>("camera_source", strCameraSource_, "");
        pnh_.param<string>("image_topic", strImageTopic_, "/camera/image_raw");
        pnh_.param<string>("odom_topic", strOdomTopic_, "/rtabmap/odom");
        pnh_.param<string>("odom_frame_id", strOdomFrame_, "odom");
        pnh_.param<string>("child_frame_id", strChildFrame_, "camera_optical_link");
        pnh_.param<bool>("publish_tf", bPublishTf_, true);
        pnh_.param<bool>("use_pangolin", bUsePangolin_, true);
        pnh_.param<double>("fps", dFps_, 30.0);

        ROS_INFO("==========================================================");
        ROS_INFO("  ORB-SLAM3 ODOMETRY NODE: 6-DoF Tracker for RTAB-Map & AI");
        ROS_INFO("==========================================================");
        ROS_INFO("  Vocab File    : %s", strVocFile_.c_str());
        ROS_INFO("  Settings File : %s", strSettingsFile_.c_str());
        ROS_INFO("  Camera Source : %s", strCameraSource_.empty() ? "[Subscribing ROS Topic]" : strCameraSource_.c_str());
        ROS_INFO("  Image Topic   : %s", strImageTopic_.c_str());
        ROS_INFO("  Odom Topic    : %s", strOdomTopic_.c_str());
        ROS_INFO("  Frame IDs     : %s -> %s", strOdomFrame_.c_str(), strChildFrame_.c_str());
        ROS_INFO("==========================================================");

        // 2. Load Camera Intrinsics from YAML Settings
        fx_ = 520.0f; fy_ = 520.0f; cx_ = 320.0f; cy_ = 240.0f;
        try
        {
            cv::FileStorage fSettings(strSettingsFile_, cv::FileStorage::READ);
            if (fSettings.isOpened())
            {
                cv::FileNode nFx = fSettings["Camera.fx"];
                if (nFx.empty()) nFx = fSettings["Camera1.fx"];
                if (!nFx.empty()) fx_ = (float)nFx;

                cv::FileNode nFy = fSettings["Camera.fy"];
                if (nFy.empty()) nFy = fSettings["Camera1.fy"];
                if (!nFy.empty()) fy_ = (float)nFy;

                cv::FileNode nCx = fSettings["Camera.cx"];
                if (nCx.empty()) nCx = fSettings["Camera1.cx"];
                if (!nCx.empty()) cx_ = (float)nCx;

                cv::FileNode nCy = fSettings["Camera.cy"];
                if (nCy.empty()) nCy = fSettings["Camera1.cy"];
                if (!nCy.empty()) cy_ = (float)nCy;

                fSettings.release();
            }
        }
        catch (...) {}
        ROS_INFO("  Camera Intrinsics: fx=%.1f, fy=%.1f, cx=%.1f, cy=%.1f", fx_, fy_, cx_, cy_);

        // 3. Inisialisasi Sistem Inti ORB-SLAM3
        mpSLAM = make_shared<ORB_SLAM3::System>(
            strVocFile_, strSettingsFile_,
            ORB_SLAM3::System::MONOCULAR, bUsePangolin_
        );
        imageScale_ = mpSLAM->GetImageScale();

        // 4. Setup Publishers
        odomPub_ = nh_.advertise<nav_msgs::Odometry>(strOdomTopic_, 10);
        posePub_ = nh_.advertise<geometry_msgs::PoseStamped>("/orb_slam3/camera_pose", 10);
        statusPub_ = nh_.advertise<std_msgs::String>("/orb_slam3/status", 5);

        // 5. Mode Operasi: Langsung Buka Kamera atau Subscribe ROS Topic
        if (!strCameraSource_.empty())
        {
            ROS_INFO("[INFO] Membuka kamera langsung dari: %s", strCameraSource_.c_str());
            imagePub_ = it_.advertise(strImageTopic_, 5);
            camInfoPub_ = nh_.advertise<sensor_msgs::CameraInfo>("/camera/camera_info", 5);
            bDirectCapture_ = true;
        }
        else
        {
            ROS_INFO("[INFO] Berlangganan topik gambar: %s", strImageTopic_.c_str());
            imageSub_ = it_.subscribe(strImageTopic_, 1, &OrbSlam3OdomNode::ImageCallback, this);
            bDirectCapture_ = false;
        }
    }

    ~OrbSlam3OdomNode()
    {
        if (mpSLAM)
        {
            mpSLAM->Shutdown();
            mpSLAM->SaveKeyFrameTrajectoryTUM("KeyFrameTrajectory.txt");
        }
    }

    void Run()
    {
        if (bDirectCapture_)
        {
            RunDirectCaptureLoop();
        }
        else
        {
            ros::spin();
        }
    }

private:
    void ProcessFrame(const cv::Mat &frameRaw, const ros::Time &stamp)
    {
        if (frameRaw.empty()) return;

        cv::Mat frame = frameRaw;
        if (imageScale_ != 1.0f)
        {
            int w = frameRaw.cols * imageScale_;
            int h = frameRaw.rows * imageScale_;
            cv::resize(frameRaw, frame, cv::Size(w, h));
        }

        double tframe = stamp.toSec();

        // 1. Eksekusi Pelacakan 6-DoF ORB-SLAM3
        Sophus::SE3f Tcw = mpSLAM->TrackMonocular(frame, tframe);
        int trackingState = mpSLAM->GetTrackingState();

        // Status string
        std_msgs::String statusMsg;
        if (trackingState == 2 || trackingState == 5)
        {
            statusMsg.data = "TRACKING_OK";
            mbTrackingOk = true;
        }
        else if (trackingState == 1)
        {
            statusMsg.data = "NOT_INITIALIZED";
            mbTrackingOk = false;
        }
        else
        {
            statusMsg.data = "LOST";
            mbTrackingOk = false;
        }
        statusPub_.publish(statusMsg);

        // 2. Jika pelacakan berhasil, publikasikan Odometri presisi ke RTAB-Map
        if (mbTrackingOk && !Tcw.matrix().isZero())
        {
            Sophus::SE3f Twc = Tcw.inverse();
            Eigen::Vector3f t = Twc.translation();
            Eigen::Quaternionf q = Twc.unit_quaternion();

            // Odometry Message
            nav_msgs::Odometry odomMsg;
            odomMsg.header.stamp = stamp;
            odomMsg.header.frame_id = strOdomFrame_;
            odomMsg.child_frame_id = strChildFrame_;

            odomMsg.pose.pose.position.x = t.x();
            odomMsg.pose.pose.position.y = t.y();
            odomMsg.pose.pose.position.z = t.z();

            odomMsg.pose.pose.orientation.x = q.x();
            odomMsg.pose.pose.orientation.y = q.y();
            odomMsg.pose.pose.orientation.z = q.z();
            odomMsg.pose.pose.orientation.w = q.w();

            // Kovariansi posisi tinggi (tracking ORB-SLAM3 sangat dipercaya)
            for (int i = 0; i < 36; i++) odomMsg.pose.covariance[i] = 0.0;
            odomMsg.pose.covariance[0] = 0.0001;  // X
            odomMsg.pose.covariance[7] = 0.0001;  // Y
            odomMsg.pose.covariance[14] = 0.0001; // Z
            odomMsg.pose.covariance[21] = 0.0001; // Roll
            odomMsg.pose.covariance[28] = 0.0001; // Pitch
            odomMsg.pose.covariance[35] = 0.0001; // Yaw

            odomPub_.publish(odomMsg);

            // PoseStamped Message
            geometry_msgs::PoseStamped poseMsg;
            poseMsg.header = odomMsg.header;
            poseMsg.pose = odomMsg.pose.pose;
            posePub_.publish(poseMsg);

            // TF Broadcast (odom -> camera_optical_link)
            if (bPublishTf_)
            {
                geometry_msgs::TransformStamped tfMsg;
                tfMsg.header.stamp = stamp;
                tfMsg.header.frame_id = strOdomFrame_;
                tfMsg.child_frame_id = strChildFrame_;

                tfMsg.transform.translation.x = t.x();
                tfMsg.transform.translation.y = t.y();
                tfMsg.transform.translation.z = t.z();

                tfMsg.transform.rotation.x = q.x();
                tfMsg.transform.rotation.y = q.y();
                tfMsg.transform.rotation.z = q.z();
                tfMsg.transform.rotation.w = q.w();

                tfBroadcaster_.sendTransform(tfMsg);
            }
        }
    }

    void ImageCallback(const sensor_msgs::ImageConstPtr &msg)
    {
        cv_bridge::CvImageConstPtr cvPtr;
        try
        {
            cvPtr = cv_bridge::toCvShare(msg, sensor_msgs::image_encodings::BGR8);
        }
        catch (cv_bridge::Exception &e)
        {
            ROS_ERROR("cv_bridge exception: %s", e.what());
            return;
        }

        ProcessFrame(cvPtr->image, msg->header.stamp);
    }

    void RunDirectCaptureLoop()
    {
        cv::VideoCapture cap;
        int retry = 0;
        while (!cap.isOpened() && retry < 6 && ros::ok())
        {
            if (retry > 0)
            {
                ROS_WARN("[WARN] Mencoba menghubungkan kembali ke kamera (%d/5)...", retry);
                ros::Duration(1.0).sleep();
            }
            if (strCameraSource_.length() == 1 && isdigit(strCameraSource_[0]))
            {
                cap.open(stoi(strCameraSource_));
            }
            else
            {
                cap.open(strCameraSource_);
            }
            retry++;
        }

        if (!cap.isOpened())
        {
            ROS_ERROR("[ERROR] Gagal membuka sumber kamera: %s setelah beberapa percobaan.", strCameraSource_.c_str());
            return;
        }

        ROS_INFO("[OK] Kamera aktif. Memulai tracking dan siaran gambar ROS...");

        ros::Rate rate(dFps_ > 0 ? dFps_ : 30.0);
        cv::Mat frame;

        while (ros::ok())
        {
            if (!cap.read(frame) || frame.empty())
            {
                ROS_WARN_THROTTLE(5, "[WARN] Frame kosong atau video selesai.");
                break;
            }

            ros::Time now = ros::Time::now();

            // 1. Publikasikan ke ROS Image Topic agar Depth AI bisa membaca frame ini
            sensor_msgs::ImagePtr imgMsg = cv_bridge::CvImage(
                std_msgs::Header(), "bgr8", frame
            ).toImageMsg();
            imgMsg->header.stamp = now;
            imgMsg->header.frame_id = strChildFrame_;
            imagePub_.publish(imgMsg);

            // 2. Publikasikan CameraInfo dengan intrinsik kalibrasi nyata
            sensor_msgs::CameraInfo infoMsg;
            infoMsg.header = imgMsg->header;
            infoMsg.width = frame.cols;
            infoMsg.height = frame.rows;
            infoMsg.distortion_model = "plumb_bob";
            infoMsg.D.assign(5, 0.0);

            // Matriks K (3x3)
            infoMsg.K.assign(0.0);
            infoMsg.K[0] = fx_;
            infoMsg.K[2] = cx_;
            infoMsg.K[4] = fy_;
            infoMsg.K[5] = cy_;
            infoMsg.K[8] = 1.0;

            // Matriks P (3x4)
            infoMsg.P.assign(0.0);
            infoMsg.P[0] = fx_;
            infoMsg.P[2] = cx_;
            infoMsg.P[5] = fy_;
            infoMsg.P[6] = cy_;
            infoMsg.P[10] = 1.0;

            camInfoPub_.publish(infoMsg);

            // 3. Olah di ORB-SLAM3 dan publikasikan Odometry
            ProcessFrame(frame, now);

            ros::spinOnce();
            rate.sleep();
        }
    }

    ros::NodeHandle nh_;
    ros::NodeHandle pnh_;
    image_transport::ImageTransport it_;
    image_transport::Subscriber imageSub_;
    image_transport::Publisher imagePub_;
    ros::Publisher odomPub_;
    ros::Publisher posePub_;
    ros::Publisher statusPub_;
    ros::Publisher camInfoPub_;
    tf2_ros::TransformBroadcaster tfBroadcaster_;

    float fx_, fy_, cx_, cy_;

    shared_ptr<ORB_SLAM3::System> mpSLAM;
    float imageScale_;
    bool mbTrackingOk;

    string strVocFile_;
    string strSettingsFile_;
    string strCameraSource_;
    string strImageTopic_;
    string strOdomTopic_;
    string strOdomFrame_;
    string strChildFrame_;
    bool bPublishTf_;
    bool bUsePangolin_;
    bool bDirectCapture_;
    double dFps_;
};

int main(int argc, char **argv)
{
    ros::init(argc, argv, "orb_slam3_odom_node");
    ros::NodeHandle nh;
    ros::NodeHandle pnh("~");

    try
    {
        OrbSlam3OdomNode node(nh, pnh);
        node.Run();
    }
    catch (const std::exception &e)
    {
        ROS_ERROR("Exception in orb_slam3_odom_node: %s", e.what());
        return 1;
    }

    return 0;
}
