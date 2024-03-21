from flask import Flask
from flask_login import LoginManager
from src.db.Services import UserService, UserEntity

def create_app():
    app = Flask(__name__)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(ID: str) -> UserEntity:
        return UserService.get_user(userID = ID)

    from src.views import views
    from src.auth import auth
    from src.api import api
    
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(api, url_prefix="/api/")

    return app