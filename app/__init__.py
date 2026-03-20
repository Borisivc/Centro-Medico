import os
from flask import Flask, g
from .db import get_db_connection

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "integra_2026_key")

    # ==========================================================================
    # FILTRO DE JINJA PARA RUT (ESTÁNDAR VISUAL)
    # ==========================================================================
    @app.template_filter('formatear_rut')
    def formatear_rut(rut):
        if not rut: return ""
        rut = str(rut).replace(".", "").replace("-", "").strip()
        if len(rut) < 2: return rut
        cuerpo, dv = rut[:-1], rut[-1]
        c_formateado = ""
        while len(cuerpo) > 3:
            c_formateado = "." + cuerpo[-3:] + c_formateado
            cuerpo = cuerpo[:-3]
        return cuerpo + c_formateado + "-" + dv

    # Importaciones siguiendo tus nombres de archivos físicos
    from .routes import main_bp
    from .agenda import agenda_bp
    from .professionals import professionals_bp
    from .patients import patients_bp
    from .roles import roles_bp
    from .users import users_bp
    from .specialties import specialties_bp
    from .states import states_bp
    from app.availability import availability_bp

    # Registro de Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(agenda_bp, url_prefix='/administracion')
    app.register_blueprint(professionals_bp, url_prefix='/administracion')
    app.register_blueprint(patients_bp, url_prefix='/administracion')
    app.register_blueprint(roles_bp, url_prefix='/administracion')
    app.register_blueprint(users_bp, url_prefix='/administracion')
    app.register_blueprint(specialties_bp, url_prefix='/administracion')
    app.register_blueprint(states_bp, url_prefix='/administracion')
    app.register_blueprint(availability_bp, url_prefix='/administracion')

    @app.before_request
    def before_request():
        if 'db' not in g:
            g.db = get_db_connection()

    @app.teardown_appcontext
    def teardown_db(error):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    return app