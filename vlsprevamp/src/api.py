from src.handlers import *
from flask import url_for, redirect

api = Blueprint("api", __name__) 

@api.route("/", methods=['GET'])
def re_to_docs() -> Response:
    return redirect(url_for('api.index'))

@api.route("/docs",methods=['GET'])
def index() -> Response:
    return render_template("api.html")

@api.route("/update", methods=["GET"])
def update() -> Response:
    """
    Handler for the api/update route on the server.
    """
    try:
        err = header_check(request, ('X-esp32-sta-mac', 'X-esp32-version', 'X-esp32-sketch-sha256'))
        if not err: return err

        # mac = request.headers.get('X-esp32-sta-mac')
        # board_sha256 = request.headers.get("X-esp32-sketch-sha256")
        board_ver = request.headers.get('X-esp32-version')
        
        conf_dict = load_config()
        if conf_dict is None: return jsonify({"message": "No Current updates"}), 304
        FIRMWARE_FILE = conf_dict['path']
        
        if FIRMWARE_FILE is None: return jsonify({"message": "No Current updates"}), 304
        if not need_update(board_ver): jsonify({"message": "No Current updates"}), 304
        if not os.path.exists(f"{ROOT}/{FIRMWARE_FILE}"): return jsonify({"message":"File Not Found"}), 404
        
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
        err = header_check(request, ('MAC-Address', 'timestamp'))
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
        err = header_check(request, ('MAC-Address', 'timestamp'))
        if not err: return err

        timestamp = request.headers.get('timestamp')
        mac = request.headers.get('MAC-Address')

        sht = request.args.get('sht')
        bmp = request.args.get('bmp')
        cam = request.args.get('cam')

        if sht not in valid or bmp not in valid or cam not in valid:
            return jsonify({"error": "Invalid status type received"}), 400
        
        if not StatusService.exists(mac): StatusService.add(mac, timestamp, sht, bmp, cam)
        else: StatusService.update(mac, timestamp, sht, bmp, cam)
        
        return jsonify({"message": "Thanks for the stats"}), 200

    except Exception as e:
        pass


@api.route("/images", methods = ['GET'])
def images() -> Response:
    """
    Handler for the /images in the server.
    """
    try:
        err = header_check(request, ('MAC-Address', 'timestamp'))
        if not err: return err

        timestamp = request.headers.get('timestamp')
        mac = request.headers.get('MAC-Address')
        image_raw_bytes = request.get_data()  #get the whole body
        # Assume the timestamp is already formattedon board.
        # Create a filename based on the timestamp
        filename = f"{timestamp_to_path(timestamp)}.jpg"

        # Save the image to the specified directory
        image_path = os.path.join(IMAGE_UPLOADS, filename)
        with open(image_path, 'wb') as f:
            f.write(image_raw_bytes)

        if not ReadingService.exists(mac, timestamp): ReadingService.add(mac, None, None, None, None, timestamp, image_path)
        else: ReadingService.update_path(mac, timestamp, image_path)

        return jsonify({"message": "Image saved successfully", "filename": filename}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500



