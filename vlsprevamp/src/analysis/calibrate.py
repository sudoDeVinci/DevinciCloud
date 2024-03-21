from src.config import *
import glob

"""
Code snippets from:
https://github.com/jeongwhanchoi/find-chessboard-corners/blob/master/calibrating_a_camera.ipynb
"""

def __valid_config_dict(confdict: Dict) -> bool:
    """
    Return True if the config dict matches the below structure.
    """
    required_keys = {
        "chessboard": ["vertical", "horizontal", "sqmm"],
        "frame": ["width", "height"]
    }
    
    if confdict is None or not isinstance(confdict, dict):
        return False
    
    for key, subkeys in required_keys.items():
        if confdict[key] is None:
            return False
        if key not in confdict:
            return False
        if not all(subkey in confdict[key] for subkey in subkeys):
            return False
    
    return True

def __load_config() -> Dict:
    """
    Attempt to load the calibration config
    """
    return load_toml(CALIBRATION_CONFIG)

def __calibrate() -> Tuple[Matlike, Matlike, Sequence[Matlike], Sequence[Matlike]]:
    """
    Calculate camera matrix data via calibration with chessboard images.
    Return camera matrix data.
    """

    confdict:Dict = __load_config(CALIBRATION_CONFIG)

    board_conf = confdict["chessboard"]
    frame_conf = confdict["frame"]
    chessboard = (board_conf["vertical"], board_conf["horizontal"])
    frame = (frame_conf["width"], frame_conf["height"])

    objp = np.zeros((chessboard[0] * chessboard[1], 3), np.float32)
    objp[:,:2] = np.mgrid[0:chessboard[0],0:chessboard[1]].T.reshape(-1,2)

    size_of_chessboard_squares_mm = board_conf["sqmm"]
    objp = objp * size_of_chessboard_squares_mm

    # Arrays to store object points and image points from all the images.
    # 3d point in real world space
    objpoints:List[Mat] = [] 
    # 2d points in image plane.
    imgpoints = [] 
    
    images = glob.glob(f'{calibration_images}/*.jpg')

    for image in images:

        img = cv2.imread(image)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, chessboard, None)

        # If found, add object points, image points (after refining them)
        if ret:
            objpoints.append(objp)
            imgpoints.append(corners)
            
    _, cameraMatrix, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, frame, None, None)

    return (cameraMatrix, dist, rvecs, tvecs)

def __write_calibration_data(cam_model:camera_model, cameraMatrix:Matlike, dist:Matlike, rvecs:Sequence[Matlike] = None, tvecs:Sequence[Matlike] = None) -> None:
    """
    Write camera calibration data to toml file.
    """
    data = {'model': cam_model.value,
            'matrix': np.asarray(cameraMatrix).tolist(),
            'distCoeff': np.asarray(dist).tolist(),
            'rvecs': np.asarray(rvecs).tolist(),
            'tvecs': np.asarray(tvecs).tolist()}

    write_toml(data, f"{camera_matrices}/{cam_model}.toml")

def undistort(img:Matlike, cameraMatrix:Matlike, dist:Matlike, remapping:bool = True, cropping:bool = True) -> Matlike:
    """
    Undistort an image using the distortion matrix and distance vectors.
    Can specify whether to remap or crop the image. Returns the undistorted image.
    """
    h, w = img.shape[:2]
    newCameraMatrix, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix, dist, (w,h), 1, (w,h))

    if not remapping:
        undistorted = cv2.undistort(img, cameraMatrix, dist, None, newCameraMatrix)

    else:
        mapx, mapy = cv2.initUndistortRectifyMap(cameraMatrix, dist, None, newCameraMatrix, (w,h), 5)
        undistorted = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)

    if cropping:
        x, y, w, h = roi
        undistorted = undistorted[y:y+h, x:x+w]
    
    return undistorted

def main(image_name: str, calibration_image_folder: str) -> None:
    cameraMatrix, dist, rvecs, tvecs = __calibrate(calibration_image_folder)
    __write_calibration_data(camera_model.OV5640, cameraMatrix, dist, rvecs, tvecs)
    distorted = cv2.imread(f"{distorted_calibration_images}/{image_name}")
    undistorted = undistort(distorted, cameraMatrix, dist, remapping=True, cropping=False)
    cv2.imwrite(f"{undistorted_calibration_images}/{image_name}", undistorted)

if __name__ == "__main__":
    main("can")