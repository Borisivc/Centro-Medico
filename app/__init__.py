from flask import Flask, g
from .config import Config
from .extensions import mysql


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    mysql.init_app(app)


    # conexión disponible en g.db
    @app.before_request
    def before_request():

        g.db = mysql.connection


    # importar blueprints
    from .routes import main_bp
    from .auth import auth_bp
    from .patients import patients_bp
    from .users import users_bp
    from .roles import roles_bp
    from .professionals import professionals_bp


    # registrar blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(roles_bp)
    app.register_blueprint(professionals_bp)


    return app