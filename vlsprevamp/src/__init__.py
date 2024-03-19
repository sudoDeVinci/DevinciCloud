from flask import Flask

def create_app():
    app = Flask(__name__)

    from src.views import views
    from src.auth import auth
    from src.api import api
    
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(api, url_prefix="/api/")

    return app