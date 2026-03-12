from flask import Flask, g, request
from .config import Config
import MySQLdb
import logging


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    # ======================================
    # LOGGING
    # ======================================

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    logger = logging.getLogger(__name__)

    logger.info("Aplicación iniciada")


    # ======================================
    # FILTROS JINJA
    # ======================================

    @app.template_filter("format_rut")
    def format_rut(rut):

        if not rut:
            return ""

        rut = rut.replace(".", "").replace("-", "")

        cuerpo = rut[:-1]
        dv = rut[-1]

        cuerpo = f"{int(cuerpo):,}".replace(",", ".")

        return f"{cuerpo}-{dv}"


    @app.template_filter("format_date")
    def format_date(fecha):

        if not fecha:
            return ""

        return fecha.strftime("%d-%m-%Y")


    # ======================================
    # CONEXION BASE DE DATOS
    # ======================================

    def get_db():

        if "db" not in g:

            g.db = MySQLdb.connect(
                host=app.config["MYSQL_HOST"],
                user=app.config["MYSQL_USER"],
                passwd=app.config["MYSQL_PASSWORD"],
                db=app.config["MYSQL_DB"],
                charset="utf8mb4"
            )

        return g.db


    @app.before_request
    def before_request():

        g.db = get_db()

        logger.info(f"{request.method} {request.path}")


    @app.teardown_appcontext
    def teardown_db(exception):

        db = g.pop("db", None)

        if db is not None:
            db.close()


    # ======================================
    # MANEJO DE ERRORES
    # ======================================

    @app.errorhandler(404)
    def not_found(error):

        logger.error(f"404 Not Found: {request.url}")

        return "Página no encontrada", 404


    @app.errorhandler(405)
    def method_not_allowed(error):

        logger.error(
            f"405 Method Not Allowed: {request.method} {request.url}"
        )

        return "Method Not Allowed", 405


    @app.errorhandler(Exception)
    def handle_exception(error):

        logger.exception(
            f"Error en {request.method} {request.url}"
        )

        return "Error interno del servidor", 500


    # ======================================
    # REGISTRO DE BLUEPRINTS
    # ======================================

    from .routes import main_bp
    from .auth import auth_bp
    from .agenda import agenda_bp
    from .patients import patients_bp
    from .professionals import professionals_bp
    from .users import users_bp
    from .roles import roles_bp
    from .specialties import specialties_bp
    from .states import states_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(agenda_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(professionals_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(roles_bp)
    app.register_blueprint(specialties_bp)
    app.register_blueprint(states_bp)

    return app