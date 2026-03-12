from functools import wraps
from flask import session, redirect, url_for, flash, g
from MySQLdb.cursors import DictCursor


# ==============================
# LOGIN REQUIRED
# ==============================

def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:

            flash("Debe iniciar sesión")

            # redirige al dashboard donde está el login modal
            return redirect(url_for("main.dashboard"))

        return f(*args, **kwargs)

    return decorated_function


# ==============================
# ROLE REQUIRED (MULTIROL)
# ==============================

def role_required(*roles):

    def decorator(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):

            user_id = session.get("user_id")

            if not user_id:

                flash("Debe iniciar sesión")

                return redirect(url_for("main.dashboard"))

            cur = g.db.cursor(DictCursor)

            cur.execute("""
                SELECT r.nombre
                FROM usuarios_roles ur
                JOIN roles r ON r.id = ur.rol_id
                WHERE ur.usuario_id = %s
            """,(user_id,))

            user_roles = [r["nombre"].upper() for r in cur.fetchall()]

            for role in roles:

                if role.upper() in user_roles:

                    return f(*args, **kwargs)

            flash("No tiene permisos para acceder")

            return redirect(url_for("main.dashboard"))

        return decorated_function

    return decorator