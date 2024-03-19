from flask import Blueprint, Request, request, Response, render_template, make_response, send_file,jsonify
from src.config import *
from src.db.Services import *

FIRMWARE_CONF:str = "firmware_cfg.toml"


def mac_filter(mac:str) -> bool:
    """
    Return True if the mac address does not exists in db.
    """
    return not DeviceService.exists(mac)

def pad_array(padding:int, arr:List[str]):
    """
    Pad an array of integers with 0s.
    """
    new_arr = ["0"]*padding
    for item in arr: new_arr.append(item)

def load_config() -> Dict[str, str]:
    """
    Attempt to load the database config file.
    """
    return load_toml(FIRMWARE_CONF)

def need_update(board_version:str) -> bool:
    """
    Return True if the firmware version needs to be updated.
    """
    conf_dict = load_config()
    firmware_version = conf_dict['version'] 
    firmware_version = firmware_version.split(".")
    board_version = board_version.split(".")
    if (firmware_version is None) or (board_version is None):
        debug("NONETYPE HERE")
    booolean = __greater(firmware_version, board_version)
    if booolean: debug("Update needed!")
    return booolean


def __greater(outgoing:List[str], incoming:List[str]) -> bool:
    """
    Compare one array of integers to another.
    """
    diff:int = len(incoming) - len(outgoing)
    if diff > 0: outgoing = pad_array(diff, outgoing)
    elif diff < 0: incoming = pad_array(0-diff, incoming)

    for i in range(len(outgoing)):
        if outgoing[i] > incoming[i]: return True

    return False

def timestamp_to_path(timestamp:str) -> str:
    """
    Convert a timestamp to format usable for path.
    """
    timestamp = timestamp.replace(" ", "-")
    timestamp = timestamp.replace(":", "-")
    return timestamp

def header_check(request: Request) -> Request | None:
    timestamp = request.headers.get('timestamp')
    mac = request.headers.get('MAC-Address')
    if not mac: return jsonify({"error": "Mac Address header is missing"}), 400
    if not timestamp: return jsonify({"error": "Timestamp header is missing"}), 400
    if mac_filter(mac): return jsonify({"error": "Unauthorized"}), 401
    return None