from functools import wraps
from flask import session, redirect, url_for, abort

def login_required(f):
    """
    Verifica que el usuario esté logueado
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """
    Verifica que el usuario tenga uno de los roles permitidos
    Uso: @role_required("admin", "profesional")
    """
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "rol" not in session:
                return redirect(url_for("auth.login"))

            if session.get("rol") not in roles:
                abort(403)  # Acceso prohibido

            return f(*args, **kwargs)
        return decorated_function
    return wrapper