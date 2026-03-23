from flask import Flask, g
import os
from .db import get_db_connection
from .utils import formatear_rut

def create_app():
    app = Flask(__name__)
    
    # Cargar Secret Key desde el entorno o usar una por defecto
    app.secret_key = os.getenv("SECRET_KEY", "integra_secret_2026")

    # --- GESTIÓN DE BASE DE DATOS ---
    @app.before_request
    def before_request():
        """Inicializa la conexión antes de cada petición."""
        if 'db' not in g:
            g.db = get_db_connection()

    @app.teardown_appcontext
    def teardown_db(error):
        """Cierra la conexión al finalizar la petición."""
        db = g.pop('db', None)
        if db is not None:
            db.close()

    # --- FILTROS JINJA2 ---
    @app.template_filter('formatear_rut')
    def filter_rut(s):
        return formatear_rut(s)

    # --- REGISTRO DE BLUEPRINTS ---
    from .main import main_bp
    from .agenda import agenda_bp
    from .patients import patients_bp
    from .users import users_bp
    from .professionals import professionals_bp
    from .availability import availability_bp
    from .specialties import specialties_bp
    from .roles import roles_bp
    from .states import states_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(agenda_bp, url_prefix='/agenda')
    app.register_blueprint(states_bp, url_prefix='/administracion/estados')
    app.register_blueprint(roles_bp, url_prefix='/administracion/roles')
    app.register_blueprint(specialties_bp, url_prefix='/administracion/especialidades')
    app.register_blueprint(availability_bp, url_prefix='/administracion/disponibilidad')
    app.register_blueprint(patients_bp, url_prefix='/administracion/pacientes')
    app.register_blueprint(users_bp, url_prefix='/administracion/usuarios')
    app.register_blueprint(professionals_bp, url_prefix='/administracion/profesionales')

    return app