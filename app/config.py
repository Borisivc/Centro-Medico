import os
from dotenv import load_dotenv

# Forzar carga del .env
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "centro_medico_secret_key_2026")
    
    # MYSQL - Intentar leer del .env, si no, usar tus valores conocidos
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "77454419") # Tu clave aquí como fallback
    MYSQL_DB = os.environ.get("MYSQL_DB", "centro_medico")
    
    MYSQL_CURSORCLASS = "DictCursor"