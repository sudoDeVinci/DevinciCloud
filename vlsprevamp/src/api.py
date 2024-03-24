from src.handlers import *
from flask import url_for, redirect
from flask_login import current_user

api = Blueprint("api", __name__) 

@api.route("/", methods=['GET'])
def re_to_docs() -> Response:
    return redirect(url_for('api.index'))

@api.route("/docs",methods=['GET'])
def index() -> Response:
    return render_template("api.html", user=current_user)

@api.route("/update", methods=["GET"])
def update() -> Response:
    """
    Handler for the api/update route on the server.
    """
    ESPMAC = HEADERS.ESP_MAC.value
    ESPVER = HEADERS.ESP_VERSION.value
    ESPSHA = HEADERS.ESP_SHA256.value

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
    MAH = HEADERS.MACADDRESS.value
    TSH = HEADERS.TIMESTAMP.value
    try:

        err = header_check(request.headers, (MAH, TSH))
        if err is not None:return err

        timestamp = request.headers.get(TSH)
        mac = request.headers.get(MAH)

        readings = [request.args.get("temperature"),
                    request.args.get("humidity"),
                    request.args.get("pressure"),
                    request.args.get("dewpoint")]

        if None in readings:
            return jsonify({"error": "Missing values in readings"}), 400
        
        out:dict = {}

        if "None" in readings:
            out = {"message": "Some missing values but values received"} 
        else:
            out = {"message": "Thanks for the readings!"}

        for index, reading in enumerate(readings):
            try:
                readings[index] = float(reading)
            except Exception:
                readings[index] = -999.00

        
        t, h, p, d = readings
        if not ReadingService.exists(mac, timestamp): ReadingService.add(mac, t, h, p, d, timestamp)
        else: ReadingService.update_readings(mac, t, h, p, d, timestamp)

        return jsonify(out), 200
        

    except Exception as e:
        debug(e)
        return jsonify({"error": str(e)}), 500

@api.route("/status", methods = ['GET'])
def status() -> Response:
    """
    Handler for the /status route on the server
    """
    valid = ("1","0")
    MAH = HEADERS.MACADDRESS.value
    TSH =HEADERS.TIMESTAMP.value
    try:

        err = header_check(request.headers, (MAH, TSH))
        if err is not None:return err

        timestamp = request.headers.get(TSH)
        mac = request.headers.get(MAH)

        sht = request.args.get('sht')
        bmp = request.args.get('bmp')
        cam = request.args.get('cam')

        if sht not in valid or bmp not in valid or cam not in valid:
            return jsonify({"error": "Invalid status type received"}), 400
        
        if not StatusService.exists(mac): StatusService.add(mac, timestamp, sht, bmp, cam)
        else: StatusService.update(mac, timestamp, sht, bmp, cam)
        
        return jsonify({"message": "Thanks for the stats"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/images", methods = ['POST'])
def images() -> Response:
    """
    Handler for the /images in the server.
    """
    MAH = HEADERS.MACADDRESS.value
    TSH =HEADERS.TIMESTAMP.value
    try:

        err = header_check(request.headers, (MAH, TSH))
        if err is not None:return err

        timestamp = request.headers.get(TSH)
        mac = request.headers.get(MAH)
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
        return jsonify({"error": str(e)}), 500



