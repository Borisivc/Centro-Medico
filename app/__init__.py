from flask import Flask, g
import MySQLdb
from .config import Config


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    # conexión a la base
    @app.before_request
    def before_request():

        g.db = MySQLdb.connect(
            host=app.config["MYSQL_HOST"],
            user=app.config["MYSQL_USER"],
            passwd=app.config["MYSQL_PASSWORD"],
            db=app.config["MYSQL_DB"],
            charset="utf8"
        )

    @app.teardown_request
    def teardown_request(exception):

        db = getattr(g, "db", None)

        if db is not None:
            db.close()

    # blueprints
    from .auth import auth_bp
    from .routes import routes_bp
    from .patients import bp as patients_bp
    from .users import users_bp
    from .roles import roles_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(routes_bp)
    app.register_blueprint(patients_bp, url_prefix="/patients")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(roles_bp)
    
    return app