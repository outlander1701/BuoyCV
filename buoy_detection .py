"""
Bennet Outland
Buoy Detection Algorithm
License: GNU General Public License v3.0

Thank you to the creators of the OpenCV Docs for the great documentation and
example code that was modified to achieve these results.

Input: USB Camera Video, Scaling Factor

Basic Process:
  . Scale down the Video
  . Create masks of given color ranges (Blue, Yellow, and Red in this case)
  . Load SimpleBlobDetector and filter by area
  . Calculate blob size and approximate turning angle to blob

Return: Blob Size, Turning Angle to Blob, Buoy Color {'Blue': 0, 'Yellow': 1, 'Red': 2}
"""

import cv2 as cv
import numpy as np

def relative_angle(x, frame_width):
    """
    x: x position of the center of the blob
    frame_width: width of the frame

    Return: the relative/approximate angle based upon the
    center of the blob and its position on the screen.
    """
    return ((-np.pi / frame_width) * x) + np.pi

def blob_detection(hsv, lower_color, upper_color, color):
    """
    hsv: frame converted to HSV color format
    lower_color: lowest designated HSV color [numpy array, rank 1, 3 entries]
    upper_color: highest designated HSV color [numpy array, rank 1, 3 entries]
    color: string identifying the color to be identified

    Note: color variable is used to determine whether or not the color to
    identify is red, so the circularity can be adjusted.

    Return: Keypoints.
    """
    # Threshold the HSV image to get only blue colors
    mask = cv.inRange(hsv, lower_color, upper_color)
    # Bitwise-AND mask and original image
    #res = cv.bitwise_and(frame,frame, mask = mask)
    inv_mask = cv.bitwise_not(mask)

    params = cv.SimpleBlobDetector_Params()

    #Thresholds for reporting
    params.minThreshold = 50
    params.maxThreshold = 1000 #10000

    #Area filtering. Make sure that the areas are of a reasonable size
    params.filterByArea = True
    params.minArea = 50
    params.maxArea = 1000

    #Color filtering: search for black blobs
    params.filterByColor = True
    params.blobColor = 0

    #Circularity
    """
    f = (4 * np.pi * w * h) / (2 * w + 2 * h) ** 2
      = 0.78 +- 0.16 (20% tolerance) => [0.62, 0.93] (Blue/Yellow)
      = 0.65 +- 0.13 (20% tolerance) => [0.52, 0.78] (Red)
    """
    params.filterByCircularity = True
    if (color == "red" or color == "Red"):
        params.minCircularity = 0.52 #Red: 0.52, Blue/Yellow: 0.62
        params.maxCircularity = 0.78 #Red: 0.78, Blue/Yello: 0.93
    else:
        params.minCircularity = 0.62 #Red: 0.52, Blue/Yellow: 0.62
        params.maxCircularity = 0.93 #Red: 0.78, Blue/Yellow: 0.93

    #Negate the following filters
    params.filterByInertia = False
    params.filterByConvexity = False

    ver = (cv.__version__).split('.')
    if int(ver[0]) < 3:
        detector = cv.SimpleBlobDetector(params)
    else:
        detector = cv.SimpleBlobDetector_create(params)

    #Detect blobs
    keypoints = detector.detect(inv_mask)

    return keypoints


def main(cap, scale):
    while (True):
        #Read each frame
        _, frame = cap.read()

        #Scale down the frame and determine the image width
        frame = cv.resize(frame,None,fx=scale, fy=scale, interpolation = cv.INTER_CUBIC)
        frame_width = frame.shape[1]

        #Convert image to HSV
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        #Define color ranges. Note: Will need to be tweaked for production runs
        #Blue:
        lower_blue = np.array([105,50,50]) #[115,50,50]
        upper_blue = np.array([135,255,255]) #[123,255,255]

        #Red:
        lower_red = np.array([150, 15, 15])
        upper_red = np.array([250, 255, 255])

        #Yellow:
        lower_yellow = np.array([30,25,25]) #[30, 25, 25]
        upper_yellow = np.array([85,255,255])

        #Report Blue Buckets
        kp_b = blob_detection(hsv, lower_blue, upper_blue, 'blue')
        try:
            print(kp_b[0].size, relative_angle(kp_b[0].pt[0], frame_width), 'blue')
            #return [kp_b[0].size, relative_angle(kp_b[0].pt[0], frame_width), 0]
        except IndexError:
            pass

        #Report Yellow Buckets
        kp_y = blob_detection(hsv, lower_yellow, upper_yellow, 'yellow')
        try:
            print(kp_y[0].size, relative_angle(kp_y[0].pt[0], frame_width), 'yellow')
            #return [kp_y[0].size, relative_angle(kp_y[0].pt[0], frame_width), 1]
        except IndexError:
            pass

        #Report Red Buckets
        kp_r = blob_detection(hsv, lower_red, upper_red, 'red')
        try:
            print(kp_r[0].size, relative_angle(kp_r[0].pt[0], frame_width), 'red')
            #return [kp_y[0].size, relative_angle(kp_y[0].pt[0], frame_width), 2]
        except IndexError:
            pass

    """
    #Used for video demonstration
        frame_with_keypoints_b = cv.drawKeypoints(frame, kp_b, np.array([]), (0, 255, 0), cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        #frame_with_keypoints_r = cv.drawKeypoints(frame, kp_r, np.array([]), (0, 0, 255), cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        #frame_with_keypoints_y = cv.drawKeypoints(frame, kp_y, np.array([]), (0, 255, 255), cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        #frame_with_keypoints_br = cv.bitwise_or(frame_with_keypoints_b, frame_with_keypoints_r)
        #frame_with_keypoints_bry = cv.bitwise_or(frame_with_keypoints_br, frame_with_keypoints_y)
    
        cv.imshow("Keypoints", frame_with_keypoints_b) #frame_with_keypoints_bry
        k = cv.waitKey(5) & 0xFF
        if k == 27:
            break
    cv.destroyAllWindows()
    """

#Define camera input. Can be file or camera index
capture = cv.VideoCapture(0)

main(capture, 0.3)
