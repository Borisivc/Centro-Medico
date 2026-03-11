from flask import Flask, g
from .config import Config
from .extensions import mysql
import datetime


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    mysql.init_app(app)


    # ==============================
    # CONEXION GLOBAL DB
    # ==============================

    @app.before_request
    def before_request():

        g.db = mysql.connection


    # ==============================
    # FILTRO FORMATO RUT
    # ==============================

    @app.template_filter("format_rut")
    def format_rut(rut):

        if not rut:
            return ""

        rut = rut.replace(".", "").replace("-", "")

        cuerpo = rut[:-1]
        dv = rut[-1]

        cuerpo = "{:,}".format(int(cuerpo)).replace(",", ".")

        return f"{cuerpo}-{dv}"


    # ==============================
    # FILTRO FORMATO FECHA
    # ==============================

    @app.template_filter("format_date")
    def format_date(fecha):

        if not fecha:
            return ""

        if isinstance(fecha, str):
            fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d")

        return fecha.strftime("%d-%m-%Y")


    # ==============================
    # IMPORTAR BLUEPRINTS
    # ==============================

    from .routes import main_bp
    from .auth import auth_bp
    from .patients import patients_bp
    from .professionals import professionals_bp
    from .users import users_bp
    from .roles import roles_bp
    from .specialties import specialties_bp


    # ==============================
    # REGISTRAR BLUEPRINTS
    # ==============================

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(professionals_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(roles_bp)
    app.register_blueprint(specialties_bp)


    return app