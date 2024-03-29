import glob

from src.config import *

"""
Used code snippets from:
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

def __load_config(config: str) -> Dict | None:
    """
    Attempt to load the calibration config
    """
    confdict = load_toml(config)
    if not __valid_config_dict(confdict):
        debug(f"Confdict not loaded correctly, current config: {confdict}")
        return None
    return confdict

def __current_time_as_filename() -> str:
    """
    Generate current time as a filename string in the format: YYYY-MM-DD_HH-MM-SS
    """
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return current_time

def __calibrate(calibration_image_folder: str, confdict: Dict) -> Tuple[Matlike, Matlike, Sequence[Matlike], Sequence[Matlike]] | None:
    """
    Calculate camera matrix data via calibration with chessboard images.
    Return camera matrix data.
    """

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
    
    images = glob.glob(f'{calibration_image_folder}/*.jpg')

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

def __write_calibration_data(cam:Camera, cameraMatrix:Matlike, dist:Matlike, rvecs:Sequence[Matlike] = None, tvecs:Sequence[Matlike] = None, timestamp: str = __current_time_as_filename()) -> None:
    """
    Write camera calibration data to toml file.
    """
    data = {'model': cam.Model.value,
            'matrix': np.asarray(cameraMatrix).tolist(),
            'distCoeff': np.asarray(dist).tolist(),
            'rvecs': np.asarray(rvecs).tolist(),
            'tvecs': np.asarray(tvecs).tolist()}

    write_toml(data, f"{cam.camera_matrices}/{timestamp}.toml")

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

def __has_filetype(name: str) -> bool:
    """
    Return true if the given filenme has an accepted image filteype suffix. 
    """
    for filetype in IMAGE_TYPES:
        if name.endswith(f".{filetype}"): return True
    return False

def __filetype_match(name:str) -> str | None:
    """
    Retun the filename of an image with a matching name to the one entered, but with the filetype suffix.
    """
    for filetype in IMAGE_TYPES:
        if os.path.exists(f"{name}.{filetype}"): return filetype
    return None

def __load_matrix(cam: Camera, name: str) -> Dict[str, Any] | None:
    if not name.endswith('.toml'): name = f"{name}.toml"
    return load_toml(f"{cam.camera_matrices}/{name}")


def calibrate(image_name: str, cam: Camera) -> None:
    calibration_image_folder = cam.training_calibration_images
    # print(calibration_image_folder)
    config = cam.CALIBRATION_CONFIG
    if not __has_filetype(image_name):
        filetype = __filetype_match(image_name)
        if filetype is not None: image_name = f"{image_name}.{filetype}"
        else:
            debug(f"Image {image_name}.{filetype} does not exist.") 
            return None
    
    confdict:Dict = __load_config(config)
    if not confdict: return None
    calibration_vals = __calibrate(calibration_image_folder, confdict)
    if not calibration_vals: return None
    cameraMatrix, dist, rvecs, tvecs = calibration_vals

    timestamp = __current_time_as_filename()

    __write_calibration_data(cam, cameraMatrix, dist, rvecs, tvecs, timestamp)

    distorted = cv2.imread(f"{cam.distorted_calibration_images}/{image_name}")
    undistorted = undistort(distorted, cameraMatrix, dist, remapping=True, cropping=False)
    cv2.imwrite(f"{cam.undistorted_calibration_images}/{timestamp}__{image_name}", undistorted)

if __name__ == "__main__":
    cam = Camera(camera_model.IPHONE13MINI)
    img = 'sky.jpg'
    timestamp = "2024-03-25_04-39-35"

    matrix = __load_matrix(cam, timestamp)
    cmat = np.asarray(matrix['matrix'])
    dist = np.asarray(matrix['distCoeff'])
    rvecs = np.asarray(matrix['rvecs'])
    tvecs = np.asarray(matrix['tvecs'])

    distorted = cv2.imread(f"{cam.distorted_calibration_images}/{img}")
    undistorted = undistort(distorted, cmat, dist, remapping=False, cropping=False)
    cv2.imwrite(f"{cam.undistorted_calibration_images}/{timestamp}__{img}", undistorted)



