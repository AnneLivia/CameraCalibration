## Camera Calibration

Camera calibration is a vital procedure that involves estimating the intrinsic (focal length and the optical center) and extrinsic parameters (rotation and translation of objects) of a camera to rectify distortions and guarantee precise outcomes. Those distortions can be radial or tangential, where straight lines appears curved and makes things in the picture look crooked or slanted, respectively. 
In order to use this code and calibrate your came, it's necessary to have a chessboard due to its well-defined structure and distinct grid pattern. The chessboard pattern provides clear and easily detectable reference points, making it easier to accurately estimate the camera's intrinsic and extrinsic parameters.

## Code Flow
1. File calibration.py
    1. You can specify two arguments when running this program:
        - sdmm: Specify the dimensions of each square of the chessboard in millimeters if you know them. The default value is 1;
        - haveimgs: Inform whether you already have images in the chessboard folder (y or n). The default value is 'y';
    2. If there are no images in the chessboard folder yet, the webcam will be initialized to capture images that can be successfully used. Press (s) to save the images and (q) to quit when you finish capturing them.
    3. When there are images in the chessboard folder, the program will perform camera calibration to obtain all the calibration data, which includes the Camera Matrix, Distortion Coefficients, Rotation Vectors, and Translation Vectors. These values will be saved in the calibData folder with the .npz extension.

## Example image showcasing Chessboard Corners detection process
<img src="https://github.com/AnneLivia/CameraCalibration/assets/31932673/f380b182-fdd7-457a-9775-679df6f19952" alt="chessboard corners detection process" width="75%"/>
