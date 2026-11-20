import os
import sys

# 1. Patch FrameDrawer.cc
frame_drawer_path = "/home/fadzkal_luthfi/slam_ws/ORB_SLAM3/src/FrameDrawer.cc"
if os.path.exists(frame_drawer_path):
    with open(frame_drawer_path, "r", encoding="utf-8") as f:
        fd = f.read()

    # Replace initialization section
    target_fd = """    if(state==Tracking::NOT_INITIALIZED)
    {
        for(size_t i=0; i<vCurrentKeys.size(); i++)
        {
            cv::Point2f pt = (imageScale != 1.f) ? (vCurrentKeys[i].pt / imageScale) : vCurrentKeys[i].pt;
            cv::rectangle(im, cv::Point(pt.x-2, pt.y-2), cv::Point(pt.x+2, pt.y+2), standardColor, 1);
        }
        for(unsigned int i=0; i<vMatches.size(); i++)
        {
            if(vMatches[i]>=0)
            {
                cv::Point2f pt1,pt2;
                if(imageScale != 1.f)
                {
                    pt1 = vIniKeys[i].pt / imageScale;
                    pt2 = vCurrentKeys[vMatches[i]].pt / imageScale;
                }
                else
                {
                    pt1 = vIniKeys[i].pt;
                    pt2 = vCurrentKeys[vMatches[i]].pt;
                }
                cv::line(im,pt1,pt2,standardColor);
            }
        }
        for(vector<pair<cv::Point2f, cv::Point2f> >::iterator it=vTracks.begin(); it!=vTracks.end(); it++)
        {
            cv::Point2f pt1,pt2;
            if(imageScale != 1.f)
            {
                pt1 = (*it).first / imageScale;
                pt2 = (*it).second / imageScale;
            }
            else
            {
                pt1 = (*it).first;
                pt2 = (*it).second;
            }
            cv::line(im,pt1,pt2, standardColor,5);
        }

    }"""

    replacement_fd = """    if(state==Tracking::NOT_INITIALIZED)
    {
        for(size_t i=0; i<vCurrentKeys.size(); i++)
        {
            cv::Point2f pt = (imageScale != 1.f) ? (vCurrentKeys[i].pt / imageScale) : vCurrentKeys[i].pt;
            if (pt.x >= 2 && pt.x < im.cols - 2 && pt.y >= 2 && pt.y < im.rows - 2)
            {
                cv::rectangle(im, cv::Point(pt.x-2, pt.y-2), cv::Point(pt.x+2, pt.y+2), standardColor, 1);
            }
        }
        for(unsigned int i=0; i<vMatches.size(); i++)
        {
            if(i < vIniKeys.size() && vMatches[i] >= 0 && (size_t)vMatches[i] < vCurrentKeys.size())
            {
                cv::Point2f pt1,pt2;
                if(imageScale != 1.f)
                {
                    pt1 = vIniKeys[i].pt / imageScale;
                    pt2 = vCurrentKeys[vMatches[i]].pt / imageScale;
                }
                else
                {
                    pt1 = vIniKeys[i].pt;
                    pt2 = vCurrentKeys[vMatches[i]].pt;
                }
                if (pt1.x >= 0 && pt1.x < im.cols && pt1.y >= 0 && pt1.y < im.rows &&
                    pt2.x >= 0 && pt2.x < im.cols && pt2.y >= 0 && pt2.y < im.rows)
                {
                    cv::line(im,pt1,pt2,standardColor);
                }
            }
        }
        for(vector<pair<cv::Point2f, cv::Point2f> >::iterator it=vTracks.begin(); it!=vTracks.end(); it++)
        {
            cv::Point2f pt1,pt2;
            if(imageScale != 1.f)
            {
                pt1 = (*it).first / imageScale;
                pt2 = (*it).second / imageScale;
            }
            else
            {
                pt1 = (*it).first;
                pt2 = (*it).second;
            }
            if (pt1.x >= 0 && pt1.x < im.cols && pt1.y >= 0 && pt1.y < im.rows &&
                pt2.x >= 0 && pt2.x < im.cols && pt2.y >= 0 && pt2.y < im.rows)
            {
                cv::line(im,pt1,pt2, standardColor,5);
            }
        }

    }"""

    if target_fd in fd:
        fd = fd.replace(target_fd, replacement_fd)
        with open(frame_drawer_path, "w", encoding="utf-8") as f:
            f.write(fd)
        print("[OK] FrameDrawer.cc patched.")
    else:
        print("[WARN] target_fd not found in FrameDrawer.cc")

# 2. Patch MapDrawer.cc
map_drawer_path = "/home/fadzkal_luthfi/slam_ws/ORB_SLAM3/src/MapDrawer.cc"
if os.path.exists(map_drawer_path):
    with open(map_drawer_path, "r", encoding="utf-8") as f:
        md = f.read()

    target_md = """        for(size_t i=0, iend=vpMPs.size(); i<iend; i++)
        {
            if(!vpMPs[i] || vpMPs[i]->isBad() || spRefMPs.count(vpMPs[i]))
                continue;
            Eigen::Matrix<float,3,1> pos = vpMPs[i]->GetWorldPos();
            if(vpMPs[i]->mbHasColor) {
                glColor3f(vpMPs[i]->mColorR, vpMPs[i]->mColorG, vpMPs[i]->mColorB);
            } else {
                glColor3f(0.0f, 0.0f, 0.0f);
            }
            glVertex3f(pos(0), pos(1), pos(2));
        }
    }
    glEnd();

    // === Pass 2: Draw Active Reference MapPoints (larger & vivid) ===
    glPointSize(mPointSize * 1.8f);
    glBegin(GL_POINTS);
    for(size_t m=0; m<vpMaps.size(); m++)
    {
        Map* pMap = vpMaps[m];
        if(!pMap) continue;

        const vector<MapPoint*> &vpRefMPs = pMap->GetReferenceMapPoints();
        for(size_t i=0, iend=vpRefMPs.size(); i<iend; i++)
        {
            if(!vpRefMPs[i] || vpRefMPs[i]->isBad())
                continue;
            Eigen::Matrix<float,3,1> pos = vpRefMPs[i]->GetWorldPos();
            if(vpRefMPs[i]->mbHasColor) {
                glColor3f(fminf(1.0f, vpRefMPs[i]->mColorR * 1.25f + 0.05f),
                          fminf(1.0f, vpRefMPs[i]->mColorG * 1.25f + 0.05f),
                          fminf(1.0f, vpRefMPs[i]->mColorB * 1.25f + 0.05f));
            } else {
                glColor3f(1.0f, 0.2f, 0.2f);
            }
            glVertex3f(pos(0), pos(1), pos(2));
        }
    }"""

    replacement_md = """        for(size_t i=0, iend=vpMPs.size(); i<iend; i++)
        {
            if(!vpMPs[i]) continue;
            try {
                if(vpMPs[i]->isBad() || spRefMPs.count(vpMPs[i]))
                    continue;
                Eigen::Matrix<float,3,1> pos = vpMPs[i]->GetWorldPos();
                if (!std::isfinite(pos(0)) || !std::isfinite(pos(1)) || !std::isfinite(pos(2)))
                    continue;
                if(vpMPs[i]->mbHasColor) {
                    glColor3f(vpMPs[i]->mColorR, vpMPs[i]->mColorG, vpMPs[i]->mColorB);
                } else {
                    glColor3f(0.0f, 0.0f, 0.0f);
                }
                glVertex3f(pos(0), pos(1), pos(2));
            } catch (...) {
                continue;
            }
        }
    }
    glEnd();

    // === Pass 2: Draw Active Reference MapPoints (larger & vivid) ===
    glPointSize(mPointSize * 1.8f);
    glBegin(GL_POINTS);
    for(size_t m=0; m<vpMaps.size(); m++)
    {
        Map* pMap = vpMaps[m];
        if(!pMap) continue;

        const vector<MapPoint*> &vpRefMPs = pMap->GetReferenceMapPoints();
        for(size_t i=0, iend=vpRefMPs.size(); i<iend; i++)
        {
            if(!vpRefMPs[i]) continue;
            try {
                if(vpRefMPs[i]->isBad())
                    continue;
                Eigen::Matrix<float,3,1> pos = vpRefMPs[i]->GetWorldPos();
                if (!std::isfinite(pos(0)) || !std::isfinite(pos(1)) || !std::isfinite(pos(2)))
                    continue;
                if(vpRefMPs[i]->mbHasColor) {
                    glColor3f(fminf(1.0f, vpRefMPs[i]->mColorR * 1.25f + 0.05f),
                              fminf(1.0f, vpRefMPs[i]->mColorG * 1.25f + 0.05f),
                              fminf(1.0f, vpRefMPs[i]->mColorB * 1.25f + 0.05f));
                } else {
                    glColor3f(1.0f, 0.2f, 0.2f);
                }
                glVertex3f(pos(0), pos(1), pos(2));
            } catch (...) {
                continue;
            }
        }
    }"""

    if target_md in md:
        md = md.replace(target_md, replacement_md)
        with open(map_drawer_path, "w", encoding="utf-8") as f:
            f.write(md)
        print("[OK] MapDrawer.cc patched.")
    else:
        print("[WARN] target_md not found in MapDrawer.cc")

# 3. Patch System.cc
system_path = "/home/fadzkal_luthfi/slam_ws/ORB_SLAM3/src/System.cc"
if os.path.exists(system_path):
    with open(system_path, "r", encoding="utf-8") as f:
        sys_code = f.read()

    target_sys = """    // Real-Time Camera RGB Pixel Sampling for 3D MapPoints
    if (imToFeed.channels() >= 3)
    {
        const size_t nTracked = mTrackedMapPoints.size();
        for (size_t i = 0; i < nTracked; i++)
        {
            MapPoint* pMP = mTrackedMapPoints[i];
            if (pMP && !pMP->isBad())
            {
                const cv::KeyPoint &kp = mTrackedKeyPointsUn[i];
                int u = (int)(kp.pt.x + 0.5f);
                int v = (int)(kp.pt.y + 0.5f);
                if (u >= 0 && u < imToFeed.cols && v >= 0 && v < imToFeed.rows)
                {
                    cv::Vec3b bgr = imToFeed.at<cv::Vec3b>(v, u);
                    float r = bgr[2] / 255.0f;
                    float g = bgr[1] / 255.0f;
                    float b = bgr[0] / 255.0f;

                    if (pMP->mbHasColor) {
                        pMP->mColorR = 0.65f * pMP->mColorR + 0.35f * r;
                        pMP->mColorG = 0.65f * pMP->mColorG + 0.35f * g;
                        pMP->mColorB = 0.65f * pMP->mColorB + 0.35f * b;
                    } else {
                        pMP->SetColor(r, g, b);
                    }
                }
            }
        }
    }"""

    replacement_sys = """    // Real-Time Camera RGB Pixel Sampling for 3D MapPoints
    if (imToFeed.channels() >= 3)
    {
        const size_t nTracked = mTrackedMapPoints.size();
        for (size_t i = 0; i < nTracked; i++)
        {
            if (i >= mTrackedKeyPointsUn.size()) break;
            MapPoint* pMP = mTrackedMapPoints[i];
            if (pMP)
            {
                try {
                    if (!pMP->isBad())
                    {
                        const cv::KeyPoint &kp = mTrackedKeyPointsUn[i];
                        int u = (int)(kp.pt.x + 0.5f);
                        int v = (int)(kp.pt.y + 0.5f);
                        if (u >= 0 && u < imToFeed.cols && v >= 0 && v < imToFeed.rows)
                        {
                            cv::Vec3b bgr = imToFeed.at<cv::Vec3b>(v, u);
                            float r = bgr[2] / 255.0f;
                            float g = bgr[1] / 255.0f;
                            float b = bgr[0] / 255.0f;

                            if (pMP->mbHasColor) {
                                pMP->mColorR = 0.65f * pMP->mColorR + 0.35f * r;
                                pMP->mColorG = 0.65f * pMP->mColorG + 0.35f * g;
                                pMP->mColorB = 0.65f * pMP->mColorB + 0.35f * b;
                            } else {
                                pMP->SetColor(r, g, b);
                            }
                        }
                    }
                } catch (...) {}
            }
        }
    }"""

    if target_sys in sys_code:
        sys_code = sys_code.replace(target_sys, replacement_sys)
        with open(system_path, "w", encoding="utf-8") as f:
            f.write(sys_code)
        print("[OK] System.cc patched.")
    else:
        print("[WARN] target_sys not found in System.cc")
