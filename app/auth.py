from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    session
)
from werkzeug.security import check_password_hash
from .extensions import mysql

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Seguridad básica
        if not email or not password:
            flash("Debe ingresar email y contraseña", "error")
            return render_template("login.html")

        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                u.id,
                u.nombre,
                u.password_hash,
                r.nombre AS rol
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
            WHERE u.email = %s
            AND u.activo = 1
        """, (email,))
        user = cur.fetchone()
        cur.close()

        # VALIDACIÓN REAL
        if user is None:
            flash("Credenciales incorrectas", "error")
            return render_template("login.html")

        stored_hash = user[2]

        if not check_password_hash(stored_hash, password):
            flash("Credenciales incorrectas", "error")
            return render_template("login.html")

        # Login exitoso
        session.clear()
        session["user_id"] = user[0]
        session["user_name"] = user[1]
        session["rol"] = user[3]

        return redirect(url_for("routes.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))