import os
import cv2
import numpy as np
import numpy.typing
from gc import collect
import functools
from datetime import datetime
from enum import Enum
from typing import List, Sequence, Tuple, Dict, NamedTuple
import toml

class camera_model(Enum):
    """
    Enum holding the various camera modules information.
    To be expanded later.
    """
    OV2640 = "ov2640"
    OV5640 = "ov5640"
    DSLR = "dslr"
    IPHONE13MINI = "iphone13mini"
    UNKNOWN = "unknown"

    @classmethod
    @functools.lru_cache(maxsize=None)
    def match(cls, camera:str):
        """
        Match input string to camera model.
        """
        camera = camera.lower()
        for _, camtype in cls.__members__.items():
            if camera == camtype.value: return camtype
        return cls.UNKNOWN

    @classmethod
    @functools.lru_cache(maxsize=None)
    def __contains__(cls, camera:str) -> bool:
        """
        Check if a camera model is supported.
        """
        return camera_model.match(camera) != cls.UNKNOWN


class Camera:
    """
    Camera class wrapper to automatically handle the format
    of various paths for a specific camera.
    """

    def __init__(self, Model):
        self.Model = Model
        # Graphing paths
        self.root_graph_folder = 'Graphs'
        self.histogram_folder = mkdir(f"{self.root_graph_folder}/{Model.value}/hist")
        self.pca_folder = mkdir(f"{self.root_graph_folder}/{Model.value}/pca")

        # Various Image folders
        self.root_image_folder = 'images'
        self.blocked_images_folder = self.mkdir(f"{self.root_image_folder}/{Model.value}/blocked")
        self.reference_images_folder = self.mkdir(f"{self.root_image_folder}/{Model.value}/reference")
        self.cloud_images_folder = self.mkdir(f"{self.root_image_folder}/{Model.value}/cloud")
        self.sky_images_folder = self.mkdir(f"{self.root_image_folder}/{Model.value}/sky")

        # Calibration image paths and settings
        self.calibration_folder = "calibration"
        self.camera_matrices = self.mkdir(f"{self.calibration_folder}/{Model.value}/matrices")
        self.training_calibration_images = self.mkdir(f"{self.calibration_folder}/{Model.value}/trainers")
        self.undistorted_calibration_images = self.mkdir(f"{self.calibration_folder}/{Model.value}/undistorted")
        self.distorted_calibration_images = self.mkdir(f"{self.calibration_folder}/{Model.value}/distorted")
        self.CALIBRATION_CONFIG = self.mkdir(f"{self.calibration_folder}/{Model.value}/calibration_cfg.toml")

        # Various config files
        root_config_folder = 'configs'

    def _eq(self, name: str):
        return name == self.Model.value

    def mkdir(self, path: str):
        """
        Create directories if they do not exist.
        """
        os.makedirs(path, exist_ok=True)
        return path
    

# Camera model for current visualization
CAMERA:str = camera_model['IPHONE13MINI'].value


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

IMAGE_TYPES = ("jpg","png","jpeg","bmp","svg")

# Various config files
root_config_folder = mkdir('configs')
FIRMWARE_CONF:str = f"{root_config_folder}/firmware_cfg.toml"
DB_CONFIG:str = f"{root_config_folder}/db_cfg.toml"


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
        debug(f"Error: File '{file_path}' not found.")
        return None
    except toml.TomlDecodeError as e:
        debug(f"Error decoding TOML file: {e}")
        return None

    return toml_data