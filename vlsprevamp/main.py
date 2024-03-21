from src.config import debug
from src.db.Entities import Role
from src.db.Management import Manager
from src.db.Services import DeviceService, UserService
from src import create_app
from werkzeug.security import generate_password_hash

app = create_app()

if __name__ == "__main__":

    try:
        Manager.connect(drop_schema = False)
        if not DeviceService.exists("34:85:18:40:CD:8C"): DeviceService.add("34:85:18:40:CD:8C", "Home-ESP", "ESP32S3", "OV5640", 173.00, 56.853470, 14.824620)
        if not DeviceService.exists("34:85:18:41:EB:78"): DeviceService.add("34:85:18:41:EB:78", "Work-ESP", "ESP32S3", "OV5640", 173.00, 56.853470, 14.824620)
        if not DeviceService.exists("34:85:18:41:59:14"): DeviceService.add("34:85:18:41:59:14", "ESP001", "ESP32S3", "OV5640", 173.00, 56.853470, 14.824620)
        if not UserService.exists("test@test.com"): UserService.add("Test User", "test@test.com", generate_password_hash("passwordyes"), Role.ADMIN)
    except Exception as e:
        debug(e)
        
    from waitress import serve
    app.config['SECRET_KEY'] = 'AMOGUSdugamladufria'
    app.run(host="0.0.0.0", port = 8080)