from flask import Flask
from .config import Config
from .extensions import mysql

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mysql.init_app(app)

    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    return app