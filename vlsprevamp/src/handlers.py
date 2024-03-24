from flask import Blueprint, Request, request, Response, render_template, make_response, send_file,jsonify, flash
from src.config import *
from src.db.Services import *
from werkzeug.datastructures import Headers

class HEADERS(Enum):
    """
    Expected Headers to the /api route from esp devices.
    """
    MACADDRESS = 'Mac-Address'
    TIMESTAMP = 'Timestamp'
    CONTENTTYPE = 'Content-Type'
    USERAGENT = 'User-Agent'
    
    ESP_MAC = 'X-esp32-sta-mac'
    ESP_VERSION = 'X-esp32-version'
    ESP_SHA256 = 'X-esp32-sketch-sha256'


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


def header_check(req_headers: Headers, headers: Tuple[str]) -> Request | None:
    """
    Check for header existence and apply MAC filter.
    """
    missing_headers = [header for header in headers if req_headers.get(header) is None]
    if missing_headers:
        return jsonify({"error": f"Missing headers: {', '.join(missing_headers)}"}), 400

    mac_headers = {HEADERS.MACADDRESS.value, HEADERS.ESP_MAC.value}
    mac_header = list(mac_headers.intersection(headers))
    if len(mac_header) > 1:
        return jsonify({"error": f"Incorrect header fields: {', '.join(missing_headers)}"}), 400
    
    if len(mac_header) == 1:
        # print(f"Is the mac {req_headers.get(mac_header[0])} in the thing? - {not mac_filter(req_headers.get(mac_header[0]))}")
        if mac_filter(req_headers.get(mac_header[0])):
            return jsonify({"error": "Unauthorized"}), 401

    return None

def email_check(email: str) -> bool:
    import re
    pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    return bool(re.match(pat, email))