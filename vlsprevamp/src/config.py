import os
import cv2
import numpy as np
import numpy.typing
from gc import collect
import functools
from datetime import datetime
from enum import Enum
from typing import List, Sequence, Tuple, Dict
import toml



class camera_model(Enum):
    """
    Enum holding the various camera modules information.
    To be expanded later.
    """
    OV2640 = "ov2640"
    OV5640 = "ov5640"
    DSLR = "dslr"
    UNKNOWN = "unknown"


    @classmethod
    @functools.lru_cache(maxsize=None)
    def match(cls, camera:str):
        """
        Match input string to camera model.
        """
        camera = camera.lower()
        return camera_model[camera] if camera in cls.__members__.items() else cls.UNKNOWN


    @classmethod
    @functools.lru_cache(maxsize=None)
    def __contains__(cls, camera:str) -> bool:
        """
        Check if a camera model is supported.
        """
        return camera.lower() in cls.__members__.values()

# Camera model for current visualization
camera:str = camera_model['OV5640'].value


# For typing, these are inexact because out memory layout differences such as between Mat and UMat
type Mat = cv2.Mat
type Matlike = cv2.typing.MatLike
type NDArray = numpy.typing.NDArray[any]



# Ensure path exists then return it.
def mkdir(folder:str) -> str:
    """
    Ensure a directory exists and return path to it.
    """
    if not os.path.exists(folder): os.makedirs(folder)
    return folder

ROOT = f"{os.getcwd()}/src"
IMAGE_UPLOADS = mkdir(f"{ROOT}/uploads")

# Database related folders
db_schema_folder = mkdir('schemas')


# Various Image folders
root_image_folder = 'images'
blocked_images_folder = mkdir(f"{root_image_folder}/{camera}/blocked")
reference_images_folder = mkdir(f"{root_image_folder}/{camera}/reference")
cloud_images_folder = mkdir(f"{root_image_folder}/{camera}/cloud")
sky_images_folder = mkdir(f"{root_image_folder}/{camera}/sky")
root_graph_folder = mkdir('Graphs')


# Calibration image paths and settings  
calibration_folder = "calibration"
calibration_images = mkdir(f"{calibration_folder}/trainers")
camera_matrices = mkdir(f"{calibration_folder}/matrices")
undistorted_calibration_images = mkdir(f"{calibration_folder}/undistorted")
distorted_calibration_images = mkdir(f"{calibration_folder}/distorted")
calibration_config = "calibration_cfg.toml"


# If debug is True, print. Otherwise, do nothing.
DEBUG:bool = True
def out01(x:str) -> None:
    print(x)
def out02(x:str) -> None:
    pass
debug = out01 if DEBUG else out02


# Functions for reading and writing from toml files.
# Most/all of the config files use toml format for simplicity.
def write_toml(data:Dict, path:str) -> None:
    """
    Write to a toml file.
    """
    try:
        out = toml.dumps(data)
        with open(path, "w") as f:
            f.write(out)
    except Exception as e:
        debug(f"Error writing to TOML file: {e}")


def load_toml(file_path:str) -> Dict:
    """ 
    Attempt to load a toml file as a dictionary.
    """
    toml_data = None
    try:
        with open(file_path, 'r') as file:
            toml_data = toml.load(file)
            if not toml_data: return None
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except toml.TomlDecodeError as e:
        print(f"Error decoding TOML file: {e}")
        return None

    return toml_data