#include <iostream>
#include <algorithm>
#include <chrono>
#include <opencv2/core/core.hpp>
#include <opencv2/videoio/videoio.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <System.h>

using namespace std;

int main(int argc, char **argv) {
    if (argc < 4) {
        cerr << "Usage: ./mono_live path_to_vocabulary path_to_settings (cam_id / video_file / stream_url)" << endl;
        return 1;
    }

    string source = argv[3];
    cv::VideoCapture cap;
    if (source.length() == 1 && isdigit(source[0])) {
        cap.open(stoi(source));
    } else {
        cap.open(source);
    }

    if (!cap.isOpened()) {
        cerr << "Error: Gagal membuka sumber video: " << source << endl;
        return 1;
    }

    cout << "Sumber video berhasil dibuka: " << source << endl;

    // Inisialisasi ORB-SLAM3 (Monocular + Pangolin GUI = true)
    ORB_SLAM3::System SLAM(argv[1], argv[2], ORB_SLAM3::System::MONOCULAR, true);
    float imageScale = SLAM.GetImageScale();

    cv::Mat frame;
    auto t0 = chrono::steady_clock::now();

    cout << "Memulai tracking 3D SLAM. Tekan Ctrl+C di terminal untuk berhenti." << endl;

    while (cap.read(frame)) {
        if (frame.empty()) break;

        if (imageScale != 1.f) {
            int width = frame.cols * imageScale;
            int height = frame.rows * imageScale;
            cv::resize(frame, frame, cv::Size(width, height));
        }

        auto t1 = chrono::steady_clock::now();
        double tframe = chrono::duration_cast<chrono::duration<double>>(t1 - t0).count();

        SLAM.TrackMonocular(frame, tframe);
    }

    SLAM.Shutdown();
    SLAM.SaveKeyFrameTrajectoryTUM("KeyFrameTrajectory.txt");
    cout << "Selesai. Trajectory tersimpan di KeyFrameTrajectory.txt" << endl;
    return 0;
}
