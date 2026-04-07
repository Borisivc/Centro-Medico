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

    # --- IMPORTACIÓN DE BLUEPRINTS ---
    from .main import main_bp
    from .agenda import agenda_bp
    from .clinical import clinical_bp      # <-- NUEVO MÓDULO CLÍNICO (Ficha Médica)
    from .patients import patients_bp
    from .users import users_bp
    from .professionals import professionals_bp
    from .availability import availability_bp
    from .specialties import specialties_bp
    from .roles import roles_bp
    from .states import states_bp

    # --- REGISTRO DE BLUEPRINTS ---
    
    # 1. Rutas Principales y Públicas (Index, Login, Dashboard)
    app.register_blueprint(main_bp)
    
    # 2. Módulos Operativos (El motor diario de la clínica)
    app.register_blueprint(agenda_bp, url_prefix='/agenda')
    app.register_blueprint(clinical_bp, url_prefix='/clinica') # <-- NUEVO REGISTRO
    
    # 3. Mantenedores de Administración (Configuraciones y catálogos)
    app.register_blueprint(patients_bp, url_prefix='/administracion/pacientes')
    app.register_blueprint(professionals_bp, url_prefix='/administracion/profesionales')
    app.register_blueprint(users_bp, url_prefix='/administracion/usuarios')
    app.register_blueprint(availability_bp, url_prefix='/administracion/disponibilidad')
    app.register_blueprint(specialties_bp, url_prefix='/administracion/especialidades')
    app.register_blueprint(roles_bp, url_prefix='/administracion/roles')
    app.register_blueprint(states_bp, url_prefix='/administracion/estados')

    return app