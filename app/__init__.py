from flask import Flask, g
import MySQLdb

def create_app():

    app = Flask(__name__)

    app.secret_key = "dev_secret_key"

    app.config["MYSQL_HOST"] = "localhost"
    app.config["MYSQL_USER"] = "root"
    app.config["MYSQL_PASSWORD"] = "77454419"
    app.config["MYSQL_DB"] = "centro_medico"


    @app.before_request
    def before_request():

        g.db = MySQLdb.connect(
            host=app.config["MYSQL_HOST"],
            user=app.config["MYSQL_USER"],
            passwd=app.config["MYSQL_PASSWORD"],
            db=app.config["MYSQL_DB"]
        )


    from .auth import auth_bp
    from .routes import routes_bp
    from .patients import bp as patients_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)
    app.register_blueprint(patients_bp, url_prefix="/patients")

    return app