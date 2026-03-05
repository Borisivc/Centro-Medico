from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:

            flash("Debe iniciar sesión")
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)

    return decorated_function



def role_required(role):

    def decorator(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):

            user_role = session.get("role")

            if not user_role:

                flash("No tiene rol asignado")
                return redirect(url_for("main.dashboard"))

            if user_role.lower() != role.lower():

                flash("No tiene permisos para acceder")
                return redirect(url_for("main.dashboard"))

            return f(*args, **kwargs)

        return decorated_function

    return decorator