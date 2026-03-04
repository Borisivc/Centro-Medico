from flask import session, redirect, url_for, flash, g
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Debe iniciar sesión")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            if not session.get("user_id"):
                flash("Debe iniciar sesión")
                return redirect(url_for("auth.login"))

            user_roles = g.user_roles

            if not user_roles:
                flash("No tiene roles asignados")
                return redirect(url_for("routes.dashboard"))

            if not any(role in user_roles for role in allowed_roles):
                flash("No tiene acceso a esta sección. Contacte al administrador.")
                return redirect(url_for("routes.dashboard"))

            return f(*args, **kwargs)

        return decorated_function
    return decorator