import MySQLdb
import MySQLdb.cursors
import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env que ya tienes creado
load_dotenv()

def get_db_connection():
    """Establece la conexión usando las variables de entorno del usuario."""
    return MySQLdb.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        passwd=os.getenv("DB_PASSWORD"),
        db=os.getenv("DB_NAME"),
        cursorclass=MySQLdb.cursors.DictCursor
    )