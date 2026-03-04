from flask import Flask, g, session
import MySQLdb

def create_app():

    app = Flask(__name__)
    app.secret_key = "super_secret_key"

    @app.before_request
    def before_request():

        g.db = MySQLdb.connect(
            host="localhost",
            user="root",
            passwd="77454419",
            db="centro_medico",
            charset="utf8"
        )

        # Cargar roles del usuario logueado
        if session.get("user_id"):
            cur = g.db.cursor()
            cur.execute("""
                SELECT r.nombre
                FROM roles r
                JOIN usuarios_roles ur ON r.id = ur.rol_id
                WHERE ur.usuario_id = %s
            """, (session["user_id"],))

            g.user_roles = [r[0] for r in cur.fetchall()]
        else:
            g.user_roles = []

    @app.teardown_request
    def teardown_request(exception):
        db = getattr(g, "db", None)
        if db:
            db.close()

    from .auth import auth_bp
    from .routes import routes_bp
    from .patients import patients_bp
    from .users import users_bp
    from .roles import roles_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(roles_bp)

    return app