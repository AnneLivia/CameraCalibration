# we need to capture the images of the chess boards in order to calibrate the camera
import cv2
import os
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-sdmm', required=False, default=1, help='Pass the dimensions of each square in millimeters')
parser.add_argument('-haveimgs', required=False, default='y', help='Inform if you already have images in the chessboard folder (y or n)')

args = parser.parse_args()

haveImages = args.haveimgs
imagesFiles = [] 

CHESSBOARD_PATH = './chessboards'
CALIBDATA_PATH = './calibData'

# creating path to save images and calibration data such as 
# (camera matrix, distortion patterns, rotation and translation vectors)
if not os.path.isdir(CHESSBOARD_PATH):
    os.makedirs(CHESSBOARD_PATH)
    # in case the user informed y, but the folder was never created before, it means there's no images yet
    haveImages = 'n'
else:
    imagesFiles = os.listdir(CHESSBOARD_PATH)
    if len(imagesFiles) == 0:
        # just in case user insert y, but there's no image in the folder
        haveImages = 'n'
    else:
        # in case there's image, but user insert n
        haveImages = 'y'

if not os.path.isdir(CALIBDATA_PATH):
    os.makedirs(CALIBDATA_PATH)

# number of insersection between the squares of the chess (we don't consider the square)
# Normally a chess board has 8x8 squares and 7x7 internal corners
CHESSBOARD_DIM = (7, 7)
# the size of the square in the chess in millimeters
SQUARE_SIZE = int(args.sdmm); 
# prepare object points. 3D points are called object points and 2D image points are called image points.
# So, we need to get the x, y and z from the 3D object in the real word, but for simplicity, 
# we say that the chess board was kept stationary at XY plane, (so Z=0 always)
# To obtain X and Y values, passing points as (0,0), (1,0), (2,0), etc., gives results in the 
# scale of chess board square size. Alternatively, passing values as (0,0), (30,0), (60,0), etc., 
# yields results in mm if the square size is known.
# in the code bellow, it's been created an array considering the dimensions of the chessboard
# and it has 3 channels, considering the object points.
objectPoints = np.zeros((CHESSBOARD_DIM[0] * CHESSBOARD_DIM[1], 3), np.float32)
# in the code bellow, we are creating a grid using mgrid, which return a dense multidimensional array
# then we transpose it (rows becomes cols and vice versa)
# then, reshapes the grid to have 2 columns and an undefined number of rows. 
# The value -1 is used to automatically determine the number of rows based on the size of the array.
# the objectPoints[:, :2] receives the valus of x, y only
objectPoints[:, :2] = np.mgrid[0 : CHESSBOARD_DIM[0], 0 : CHESSBOARD_DIM[1]].T.reshape(-1, 2)
#  if the square size is known, we can multiply it by its size, in order to get  
# detect the chessboard, find corner locations and draw the corners 
objectPoints*=SQUARE_SIZE
print(objectPoints);
# criteria of stop: when the total number of iterations was achieved or the result we want was achieved
# TERM_CRITERIA_EPS: stop the algorithm iteration if specified accuracy, epsilon, is reached. 
# TERM_CRITERIA_MAX_ITER: stop the iteration when any of condition is met
# 0.001 is the required precision, 30 is the number of iteration
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# object to save 2d points and 3d points
objPoints3D = []
imgPoints2D = []

def detectChessboardCorners(image, gray, addToList = True):
    # By detecting the corners, it is possible to obtain important 
    # information about the geometry of the scene and the position of objects relative to the camera.
    ret, corners = cv2.findChessboardCorners(gray, CHESSBOARD_DIM)
    # if it was detected successfully. The corners are from left-to-right, top-to-bottom
    if  ret:
        # once we find the corner we can use cornerSubPix to increase the accuracy
        # detect corners. (3, 3) is the winSize, the greater, the more information are considered which
        # results in more precise corner detection. draw all corners detected
        # zeroZone = (-1, -1) indicates that there's no dead zone defined. this zeroZone 
        # can be used to avoid autocorrelation problems in the matrix.
        cornersPix = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        # we can only insert in the object, the images we want to save
        if addToList:
            # saving 3d and 2d points
            objPoints3D.append(objectPoints)
            imgPoints2D.append(cornersPix);

        image = cv2.drawChessboardCorners(image, CHESSBOARD_DIM, cornersPix, ret)

    return ret

def loadCalibrationData():
   data = np.load(f'{CALIBDATA_PATH}/calibData.npz')
   print('The camera was calibrated:' +
        f'\n\nCamera Matrix: {data["camMatrix"]}' +
        f'\n\nDistortion coefficients: {data["distCoef"]}'+
        f'\n\nRotation vectors: {data["rVector"]}' +
        f'\n\nTranslation vectors: {data["tVector"]}')

def calibrateCamera(gray):
    ret, mtx, dist, rVecs, tVecs = cv2.calibrateCamera(objPoints3D, imgPoints2D, gray.shape[::-1], None, None)
    if ret:
        # savez it's used to save multiple arrays into a single compressed archive file with the .npz extension.
        np.savez(f'{CALIBDATA_PATH}/calibData.npz', camMatrix=mtx, distCoef=dist, rVector=rVecs, tVector=tVecs)
        # to load the data
        loadCalibrationData()

# function created to save the images
def getBoardImages():
    # in this function there's an update in this variable
    global imagesFiles;
    # if there's images already captured from the camera, then we can just perform the calibration considering them
    if haveImages == 'y':
        print(f'There are {len(imagesFiles)} images in the folder already')
        for imageFile in imagesFiles:
            imagePath = os.path.join(CHESSBOARD_PATH, imageFile)
            image = cv2.imread(imagePath)
            # we need to convert it to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            detectChessboardCorners(image, gray)
            cv2.imshow('Image', image)
            cv2.waitKey(0)
        # only calibrate when we already have images
        calibrateCamera(gray)
    # we need to save those images from the webcam    
    else:
        print(f'There\'s no image in the {CHESSBOARD_PATH} folder yet.')
        # Now it's time to capture the images from the camera
        cap = cv2.VideoCapture(0)
        nImage = 0
        while True:
            _, frame = cap.read()
            copyFrame = frame.copy()
             # we need to convert it to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # addToList is false, because the images used to calibrate are still being captured
            ret = detectChessboardCorners(frame, gray, addToList=False)
            
            cv2.imshow('Frame', copyFrame);
            cv2.imshow('FrameCorners', frame);

            if cv2.waitKey(1) == ord('q'):
                break;
            elif cv2.waitKey(1) == ord('s'):
                # saving only images that was correctly identified by the method findChessboardCorners
                if ret:
                    print(f'Saving image {nImage}')
                    cv2.imwrite(f'{CHESSBOARD_PATH}/chess_{nImage}.jpg', copyFrame)
                    nImage+=1

        cv2.destroyAllWindows()
        cap.release()
        print(f'{nImage} was saved');
        # updating the variable that references the images path
        imagesFiles = os.listdir(CHESSBOARD_PATH)

getBoardImages()

# it means that all images were save, then we can proceed to the calibration
if haveImages == 'n' and len(os.listdir(CHESSBOARD_PATH)) > 0:
    # now we have images
    haveImages = 'y'
    getBoardImages()
