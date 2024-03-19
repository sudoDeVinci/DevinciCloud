from src.config import debug
from src.db.Management import Manager
from src.db.Services import DeviceService
from src import create_app

app = create_app()

if __name__ == "__main__":

    try:
        Manager.connect(drop_schema = False)
        if (not DeviceService.exists("34:85:18:40:CD:8C")): DeviceService.add("34:85:18:40:CD:8C", "Home-ESP", "ESP32S3", "OV5640", 173.00, 56.853470, 14.824620)
        if (not DeviceService.exists("34:85:18:41:EB:78")): DeviceService.add("34:85:18:41:EB:78", "Work-ESP", "ESP32S3", "OV5640", 173.00, 56.853470, 14.824620)
        if (not DeviceService.exists("34:85:18:41:59:14")): DeviceService.add("34:85:18:41:59:14", "ESP001", "ESP32S3", "OV5640", 173.00, 56.853470, 14.824620)
    except Exception as e:
        debug(e)
        
    from waitress import serve
        
    serve(app, host="192.168.8.57", port = 8080)