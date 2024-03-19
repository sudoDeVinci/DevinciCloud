from handlers import *

api = Blueprint("api", __name__) 

@api.route("/update", methods=["GET"])
def update() -> Response:
    """
    Handler for the api/update route on the server.
    """
    try:
        # Get the timestamp from the "timestamp" header
        mac = request.headers.get('X-esp32-sta-mac')
        board_ver = request.headers.get('X-esp32-version')
        board_sha256 = request.headers.get("X-esp32-sketch-sha256")
        
        # If no mac or wrong mac, tell that there's no updates.
        if mac is None: return jsonify({"message": "No Current updates"}), 304
        if mac_filter(mac): return jsonify({"message": "No Current updates"}), 304
        
        conf_dict = load_config()
        if conf_dict is None: return jsonify({"message": "No Current updates"}), 304
        FIRMWARE_FILE = conf_dict['path']
        if FIRMWARE_FILE is None: return jsonify({"message": "No Current updates"}), 304
        firmware_version = conf_dict['version']

        
    except Exception as e:
        debug(e)
        return jsonify({"error": str(e)}), 500