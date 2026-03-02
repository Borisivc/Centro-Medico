# app/db.py
from flask import g

def get_db():
    """
    Retorna la conexión actual de la base de datos de Flask.
    """
    return g.db