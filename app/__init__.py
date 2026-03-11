from flask import Flask, g, request, session
from .config import Config
from .extensions import mysql
import logging
import traceback
import datetime


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    mysql.init_app(app)

    # ==========================
    # LOGGING
    # ==========================

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    logger = logging.getLogger(__name__)

    logger.info("Aplicación iniciada")

    # ==========================
    # FILTRO RUT
    # ==========================

    @app.template_filter("format_rut")
    def format_rut(rut):

        if not rut:
            return ""

        rut = rut.replace(".", "").replace("-", "")

        cuerpo = rut[:-1]
        dv = rut[-1]

        try:
            cuerpo = "{:,}".format(int(cuerpo)).replace(",", ".")
        except:
            return rut

        return f"{cuerpo}-{dv}"

    # ==========================
    # FILTRO FECHA
    # ==========================

    @app.template_filter("format_date")
    def format_date(fecha):

        if not fecha:
            return ""

        if isinstance(fecha, str):
            fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d")

        return fecha.strftime("%d-%m-%Y")

    # ==========================
    # CONEXION DB
    # ==========================

    @app.before_request
    def before_request():

        try:

            g.db = mysql.connection

            logger.debug(
                f"Request: {request.method} {request.path} | "
                f"user_id={session.get('user_id')}"
            )

        except Exception as e:

            logger.error("Error conectando DB")
            logger.error(str(e))

    # ==========================
    # ERROR GLOBAL
    # ==========================

    @app.errorhandler(Exception)
    def handle_exception(e):

        logger.error("ERROR GLOBAL")
        logger.error(str(e))
        logger.error(traceback.format_exc())

        return f"""
        <h2>Error interno</h2>
        <pre>{str(e)}</pre>
        """

    # ==========================
    # IMPORTAR BLUEPRINTS
    # ==========================

    from .routes import main_bp
    from .auth import auth_bp
    from .patients import patients_bp
    from .professionals import professionals_bp
    from .users import users_bp
    from .roles import roles_bp
    from .specialties import specialties_bp
    from .agenda import agenda_bp

    # ==========================
    # REGISTRAR BLUEPRINTS
    # ==========================

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(professionals_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(roles_bp)
    app.register_blueprint(specialties_bp)
    app.register_blueprint(agenda_bp)

    return app