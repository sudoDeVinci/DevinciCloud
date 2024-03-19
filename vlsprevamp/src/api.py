from src.handlers import *

api = Blueprint("api", __name__) 

@api.route("/update", methods=["GET"])
def update() -> Response:
    """
    Handler for the api/update route on the server.
    """
    try:
        mac = request.headers.get('X-esp32-sta-mac')
        board_ver = request.headers.get('X-esp32-version')
        # board_sha256 = request.headers.get("X-esp32-sketch-sha256")
        
        if not mac: return jsonify({"error": "Mac Address header is missing"}), 400
        if mac_filter(mac): return jsonify({"error": "Unauthorized"}), 401
        
        conf_dict = load_config()
        if conf_dict is None: return jsonify({"message": "No Current updates"}), 304
        FIRMWARE_FILE = conf_dict['path']
        if FIRMWARE_FILE is None: return jsonify({"message": "No Current updates"}), 304

        if not need_update(board_ver): jsonify({"message": "No Current updates"}), 304
            
        if not os.path.exists(f"{ROOT}/{FIRMWARE_FILE}")
        response = make_response(send_file(f"{ROOT}/{FIRMWARE_FILE}", mimetype="application/octet-stream"), 200)
        return response
    
    except Exception as e:
        return jsonify({"message": "No Current updates"}), 304


@api.route("/reading", methods=['GET'])
def reading() -> Response:
    """
    Handler for reading the /reading route on the server.
    """
    try:
        err = header_check(request)
        if not err: return err

        timestamp = request.headers.get('timestamp')
        mac = request.headers.get('MAC-Address')

        t = request.args.get("temperature")
        h = request.args.get("humidity")
        p = request.args.get("pressure")
        d = request.args.get("dewpoint")

        if t is None or h is None or p is None or d is None:
            return jsonify({"error": "Missing values in readings"}), 400
        
        out:dict = {}

        if t == "None" or h == "None" or p == "None" or d == "None":
            out = {"message": "Some missing values but values received"} 
        else:
            out = {"message": "Thanks for the readings!"}

        if not ReadingService.exists(mac, timestamp): ReadingService.add(mac, t, h, p, d, timestamp)
        else: ReadingService.update_readings(mac, t, h, p, d, timestamp)

        return jsonify(out), 200
        

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route("/status", methods = ['GET'])
def status() -> Response:
    """
    Handler for the /status route on the server
    """
    valid = ("1","0")
    try:
        err = header_check(request)
        if not err: return err

        timestamp = request.headers.get('timestamp')
        mac = request.headers.get('MAC-Address')

        sht = request.args.get('sht')
        bmp = request.args.get('bmp')
        cam = request.args.get('cam')

    except Exception as e:
        pass



@api.route("/images", methods = ['GET'])
def images() -> Response:
    pass

