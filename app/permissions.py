from functools import wraps
from flask import session, redirect, url_for, flash, g


def role_required(nombre_rol):

    def decorator(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):

            if not session.get("user_id"):
                return redirect(url_for("auth.login"))

            cur = g.db.cursor()

            cur.execute("""
                SELECT r.nombre
                FROM roles r
                JOIN usuarios_roles ur ON r.id = ur.rol_id
                WHERE ur.usuario_id = %s
            """, (session["user_id"],))

            roles_usuario = [r[0] for r in cur.fetchall()]

            if nombre_rol not in roles_usuario:
                flash("⛔ No tiene permisos para acceder a esta sección")
                return redirect(url_for("routes.dashboard"))

            return f(*args, **kwargs)

        return decorated_function

    return decorator