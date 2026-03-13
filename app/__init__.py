import logging
import MySQLdb

from flask import Flask, g, request

from .config import Config


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

    app.logger.info("Aplicación iniciada")

    # ======================================
    # FILTROS JINJA
    # ======================================

    from .filters import format_rut, format_date

    app.jinja_env.filters["format_rut"] = format_rut
    app.jinja_env.filters["format_date"] = format_date

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


    # ======================================
    # BEFORE REQUEST
    # ======================================

    @app.before_request
    def before_request():

        g.db = get_db()

        app.logger.info(
            f"{request.method} {request.path}"
        )


    # ======================================
    # TEARDOWN
    # ======================================

    @app.teardown_request
    def teardown_request(exception):

        db = g.pop("db", None)

        if db is not None:
            db.close()

    # ======================================
    # BLUEPRINTS
    # ======================================

    from .routes import main_bp
    app.register_blueprint(main_bp)

    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .patients import patients_bp
    app.register_blueprint(patients_bp)

    from .users import users_bp
    app.register_blueprint(users_bp)

    from .roles import roles_bp
    app.register_blueprint(roles_bp)

    from .specialties import specialties_bp
    app.register_blueprint(specialties_bp)

    from .states import states_bp
    app.register_blueprint(states_bp)

    from .professionals import professionals_bp
    app.register_blueprint(professionals_bp)

    from .agenda import agenda_bp
    app.register_blueprint(agenda_bp)

    # NUEVO MODULO DISPONIBILIDAD
    from .availability import availability_bp
    app.register_blueprint(availability_bp)

    return app