import cv2
import numpy as np
import matplotlib.pyplot as plt

def drawlines(img1,img2,lines,pts1,pts2):
    ''' img1 - image on which we draw the epilines for the points in img2
        lines - corresponding epilines '''
    r,c = img1.shape
    img1 = cv2.cvtColor(img1,cv2.COLOR_GRAY2BGR)
    img2 = cv2.cvtColor(img2,cv2.COLOR_GRAY2BGR)
    for r,pt1,pt2 in zip(lines,pts1,pts2):
        color = tuple(np.random.randint(0,255,3).tolist())
        x0,y0 = map(int, [0, -r[2]/r[1] ])
        x1,y1 = map(int, [c, -(r[2]+r[0]*c)/r[1] ])
        img1 = cv2.line(img1, (x0,y0), (x1,y1), color,1)
        img1 = cv2.circle(img1,tuple(pt1),5,color,-1)
        img2 = cv2.circle(img2,tuple(pt2),5,color,-1)
    return img1,img2

def generateDepthMap(img1, img2):
    #img1 = cv2.imread('left.jpg',cv2.IMREAD_GRAYSCALE)          # queryImage
    #img2 = cv2.imread('right.jpg',cv2.IMREAD_GRAYSCALE) # trainImage

    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)


    # Initiate SIFT detector
    sift = cv2.SIFT_create()
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(img1,None)
    kp2, des2 = sift.detectAndCompute(img2,None)
    # FLANN parameters
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks=50)   # or pass empty dictionary
    flann = cv2.FlannBasedMatcher(index_params,search_params)
    matches = flann.knnMatch(des1,des2,k=2)

    # Need to draw only good matches, so create a mask
    matchesMask = [[0,0] for i in range(len(matches))]

    good = []
    pts1 = []
    pts2 = []

    # ratio test as per Lowe's paper
    for i,(m,n) in enumerate(matches):
        if m.distance < 0.4*n.distance:
            matchesMask[i]=[1,0]
            good.append(m)
            pts2.append(kp2[m.trainIdx].pt)
            pts1.append(kp1[m.queryIdx].pt)

    draw_params = dict(matchColor = (0,255,0),
                       singlePointColor = (255,0,0),
                       matchesMask = matchesMask,
                       flags = cv2.DrawMatchesFlags_DEFAULT)
    img3 = cv2.drawMatchesKnn(img1,kp1,img2,kp2,matches,None,**draw_params)
    #plt.imshow(img3,),plt.show()

    # ############## Compute Fundamental Matrix ##############
    # F, I, points1, points2 = compute_fundamental_matrix(good_matches, kp1, kp2)
    pts1 = np.int32(pts1)
    pts2 = np.int32(pts2)
    F, mask = cv2.findFundamentalMat(pts1,pts2,cv2.FM_LMEDS,ransacReprojThreshold=3,
                confidence=0.99)

    # We select only inlier points
    pts1 = pts1[mask.ravel()==1]
    pts2 = pts2[mask.ravel()==1]


    # Find epilines corresponding to points in right image (second image) and
    # drawing its lines on left image
    lines1 = cv2.computeCorrespondEpilines(pts2.reshape(-1,1,2), 2,F)
    lines1 = lines1.reshape(-1,3)
    img5,img6 = drawlines(img1,img2,lines1,pts1,pts2)

    # Find epilines corresponding to points in left image (first image) and
    # drawing its lines on right image
    lines2 = cv2.computeCorrespondEpilines(pts1.reshape(-1,1,2), 1,F)
    lines2 = lines2.reshape(-1,3)
    img3,img4 = drawlines(img2,img1,lines2,pts2,pts1)

    # plt.subplot(121),plt.imshow(img5)
    # plt.subplot(122),plt.imshow(img3)
    # plt.show()

    # print("2")

    # ############## Stereo rectify uncalibrated ##############
    h1, w1 = img1.shape
    h2, w2 = img2.shape
    thresh = 0
    _, H1, H2 = cv2.stereoRectifyUncalibrated(
        np.float32(pts1), np.float32(pts2), F, imgSize=(w1, h1),
    )

    # print("3")

    ############## Undistort (Rectify) ##############
    img1_undistorted = cv2.warpPerspective(img1, H1, (w1, h1))
    img2_undistorted = cv2.warpPerspective(img2, H2, (w2, h2))
    
    composite = np.dstack((img2_undistorted, img1_undistorted, img2_undistorted))
    #cv2.imshow("imfuse", composite)
    #cv2.waitKey(0)

    cv2.imwrite("undistorted_1.png", img1_undistorted)
    cv2.imwrite("undistorted_2.png", img2_undistorted)

    # print("4")

    # ############## Calculate Disparity (Depth Map) ##############

    # Using StereoBM
    stereo = cv2.StereoBM_create(numDisparities=16, blockSize=15)
    # disparity_BM = stereo.compute(img1_undistorted, img2_undistorted)
    # plt.imshow(disparity_BM, "gray")
    # plt.colorbar()
    # plt.show()

    # print("5")

    # Using StereoSGBM
    # Set disparity parameters. Note: disparity range is tuned according to
    #  specific parameters obtained through trial and error.
    win_size = 7
    min_disp = 0
    max_disp = 16
    num_disp = max_disp - min_disp  # Needs to be divisible by 16
    stereo = cv2.StereoSGBM_create(
        minDisparity=min_disp,
        numDisparities=num_disp,
        blockSize=5,
        uniquenessRatio=5,
        speckleWindowSize=5,
        speckleRange=5,
        disp12MaxDiff=2,
        P1=8 * 3 * win_size ** 2,
        P2=32 * 3 * win_size ** 2,
    )
    disparity_SGBM = stereo.compute(img1_undistorted, img2_undistorted)
    cv2.normalize(disparity_SGBM, disparity_SGBM, 0, 255, cv2.NORM_MINMAX)
    plt.imshow(disparity_SGBM, "gray")
    plt.colorbar()
    plt.show()

    # print("6")






# =============================================================================
# PROJECT CHRONO - http:#projectchrono.org
#
# Copyright (c) 2019 projectchrono.org
# All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be found
# in the LICENSE file at the top level of the distribution and at
# http:#projectchrono.org/license-chrono.txt.
#
# =============================================================================
# Authors: Asher Elmquist
# =============================================================================
#
# Chrono demonstration of a camera sensor.
# Generates a mesh object and rotates camera sensor around the mesh.
#
# =============================================================================

import pychrono.core as chrono
import pychrono.sensor as sens

import math
import time

def main():
    # -----------------
    # Create the system
    # -----------------
    mphysicalSystem = chrono.ChSystemNSC()

    # -----------------------------------
    # add a mesh to be sensed by a camera
    # -----------------------------------
    mmesh = chrono.ChTriangleMeshConnected()
    mmesh.LoadWavefrontMesh("../../../chrono/data/vehicle/hmmwv/hmmwv_chassis.obj", False, True)
    # scale to a different size
    mmesh.Transform(chrono.ChVectorD(0, 0, 0), chrono.ChMatrix33D(2))

    trimesh_shape = chrono.ChTriangleMeshShape()
    trimesh_shape.SetMesh(mmesh)
    trimesh_shape.SetName("HMMWV Chassis Mesh")
    trimesh_shape.SetStatic(True)

    mesh_body = chrono.ChBody()
    mesh_body.SetPos(chrono.ChVectorD(0, 0, 0))
    mesh_body.AddAsset(trimesh_shape)
    mesh_body.SetBodyFixed(True)
    mphysicalSystem.Add(mesh_body)

    # -----------------------
    # Create a sensor manager
    # -----------------------
    manager = sens.ChSensorManager(mphysicalSystem)

    intensity = 1.0;
    manager.scene.AddPointLight(chrono.ChVectorF(2, 2.5, 100), chrono.ChVectorF(intensity, intensity, intensity), 500.0)
    manager.scene.AddPointLight(chrono.ChVectorF(9, 2.5, 100), chrono.ChVectorF(intensity, intensity, intensity), 500.0)
    manager.scene.AddPointLight(chrono.ChVectorF(16, 2.5, 100), chrono.ChVectorF(intensity, intensity, intensity), 500.0)
    manager.scene.AddPointLight(chrono.ChVectorF(23, 2.5, 100), chrono.ChVectorF(intensity, intensity, intensity), 500.0)

    # manager.SetKeyframeSizeFromTimeStep(.001,1/exposure_time)
    # ------------------------------------------------
    # Create a camera and add it to the sensor manager
    # ------------------------------------------------
    offset_pose = chrono.ChFrameD(chrono.ChVectorD(-5, 0, 2), chrono.Q_from_AngAxis(2, chrono.ChVectorD(0, 1, 0)))
    cam = sens.ChCameraSensor(
        mesh_body,              # body camera is attached to
        update_rate,            # update rate in Hz
        offset_pose,            # offset pose
        image_width,            # image width
        image_height,           # image height
        fov                    # camera's horizontal field of view
    )
    cam.SetName("Camera Sensor")
    cam.SetLag(lag);
    cam.SetCollectionWindow(exposure_time);


    offset_pose2 = chrono.ChFrameD(chrono.ChVectorD(-5, -30, 2), chrono.Q_from_AngAxis(2, chrono.ChVectorD(0, 1, 0)))
    cam2 = sens.ChCameraSensor(
        mesh_body,              # body camera is attached to
        update_rate,            # update rate in Hz
        offset_pose2,            # offset pose
        image_width,            # image width
        image_height,           # image height
        fov                    # camera's horizontal field of view
    )
    cam2.SetName("Camera Sensor 2")
    cam2.SetLag(lag);
    cam2.SetCollectionWindow(exposure_time);

    # Provides the host access to this RGBA8 buffer
    cam.PushFilter(sens.ChFilterRGBA8Access())
    cam2.PushFilter(sens.ChFilterRGBA8Access())

    # Filter the sensor to grayscale
    cam.PushFilter(sens.ChFilterGrayscale());
    cam2.PushFilter(sens.ChFilterGrayscale());

    # Render the buffer again to see the new grayscaled image
    if vis:
        cam.PushFilter(sens.ChFilterVisualize(int(image_width / 2), int(image_height / 2), "Grayscale Image"))
        cam2.PushFilter(sens.ChFilterVisualize(int(image_width / 2), int(image_height / 2), "Grayscale Image 2"))

    # Resizes the image to the provided width and height
    cam.PushFilter(sens.ChFilterImageResize(int(image_width / 2), int(image_height / 2)))
    cam2.PushFilter(sens.ChFilterImageResize(int(image_width / 2), int(image_height / 2)))

    # Access the grayscaled buffer as R8 pixels
    cam.PushFilter(sens.ChFilterR8Access())
    cam2.PushFilter(sens.ChFilterR8Access())

    # add sensor to manager
    manager.AddSensor(cam)
    manager.AddSensor(cam2)


    # ---------------
    # Simulate system
    # ---------------
    orbit_radius = 10
    orbit_rate = 0.5
    ch_time = 0.0

    t1 = time.time()

    while (ch_time < end_time):
        cam.SetOffsetPose(chrono.ChFrameD(
            chrono.ChVectorD(-orbit_radius * math.cos(ch_time * orbit_rate), 0.1 + -orbit_radius * math.sin(ch_time * orbit_rate), 1),
            chrono.Q_from_AngAxis(ch_time * orbit_rate, chrono.ChVectorD(0, 0, 1))))

        cam2.SetOffsetPose(chrono.ChFrameD(
            chrono.ChVectorD(-orbit_radius * math.cos(ch_time * orbit_rate), -0.1 + -orbit_radius * math.sin(ch_time * orbit_rate), 1),
            chrono.Q_from_AngAxis(ch_time * orbit_rate, chrono.ChVectorD(0, 0, 1))))


        # Access the RGBA8 buffer from the camera
        rgba8_buffer = cam.GetMostRecentRGBA8Buffer()
        rgba8_buffer2 = cam2.GetMostRecentRGBA8Buffer()
        if (rgba8_buffer.HasData() and rgba8_buffer2.HasData()):
            rgba8_data = rgba8_buffer.GetRGBA8Data()
            rgba8_data2 = rgba8_buffer2.GetRGBA8Data()
            
            generateDepthMap(rgba8_data, rgba8_data2)
            exit()
            


        # Update sensor manager
        # Will render/save/filter automatically
        manager.Update()

        # Perform step of dynamics
        mphysicalSystem.DoStepDynamics(step_size)

        # Get the current time of the simulation
        ch_time = mphysicalSystem.GetChTime()

    print("Sim time:", end_time, "Wall time:", time.time() - t1)

# -----------------
# Camera parameters
# -----------------

# Noise model attached to the sensor
# TODO: Noise models haven't been implemented in python
# noise_model="CONST_NORMAL"      # Gaussian noise with constant mean and standard deviation
# noise_model="PIXEL_DEPENDENT"   # Pixel dependent gaussian noise
# noise_model="RESPONSE_FUNCTION" # Noise model based on camera's response and parameters
noise_model="NONE"              # No noise model

# Camera lens model
# Either CameraLensModelType_PINHOLE or CameraLensModelType_SPHERICAL
lens_model = sens.PINHOLE;

# Update rate in Hz
update_rate = 30

# Image width and height
image_width = 1280
image_height = 720

# Camera's horizontal field of view
fov = 1.408

# Lag (in seconds) between sensing and when data becomes accessible
lag = 0

# Exposure (in seconds) of each image
exposure_time = 0

# ---------------------
# Simulation parameters
# ---------------------

# Simulation step size
step_size = 1e-3

# Simulation end time
end_time = 20.0

# Save camera images
save = False

# Render camera images
vis = True

# Output directory
out_dir = "SENSOR_OUTPUT/"

# The path to the Chrono data directory containing various assets (meshes, textures, data files)
# is automatically set, relative to the default location of this demo.
# If running from a different directory, you must change the path to the data directory with:
# chrono.SetChronoDataPath('path/to/data')

main()

