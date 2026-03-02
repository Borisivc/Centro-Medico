from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        if not session.get("user_id"):
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)

    return decorated


def role_required(role):

    def decorator(f):

        @wraps(f)
        def decorated(*args, **kwargs):

            roles = session.get("roles", [])

            if role not in roles:

                flash("No tienes permisos para acceder a esta página")

                return redirect(url_for("routes.dashboard"))

            return f(*args, **kwargs)

        return decorated

    return decorator