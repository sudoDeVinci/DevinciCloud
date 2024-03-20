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


def header_check(request: Request, headers: Tuple[str]) -> Request | None:
    """
    Check for header existence and apply MAC filter.
    """
    missing_headers = [header for header in headers if request.headers.get(header) is None]
    if missing_headers:
        return jsonify({"error": f"Missing headers: {', '.join(missing_headers)}"}), 400

    mac_headers = {'MAC-Address', 'X-esp32-sta-mac'}
    mac_header = mac_headers.intersection(headers)
    if mac_header:
        if mac_filter(mac_header[0]): return jsonify({"error": "Unauthorized"}), 401

    return None