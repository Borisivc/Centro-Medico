from flask import Flask, g
from .config import Config
import MySQLdb


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

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


    @app.teardown_appcontext
    def teardown_db(exception):

        db = g.pop("db", None)

        if db is not None:
            db.close()


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