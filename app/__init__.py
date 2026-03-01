from flask import Flask, render_template
from .config import Config
from .extensions import mysql
from .auth import auth_bp
from .routes import routes_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mysql.init_app(app)

    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)

    # Error 403 - Acceso denegado
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("403.html"), 403

    return app