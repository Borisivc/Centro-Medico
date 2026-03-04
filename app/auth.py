from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import check_password_hash

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    # Si ya está logueado, redirige al dashboard
    if session.get("user_id"):
        return redirect(url_for("routes.dashboard"))

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Debe ingresar email y contraseña")
            return render_template("auth/login.html")

        cur = g.db.cursor()

        cur.execute("""
            SELECT id, nombre, email, password_hash
            FROM usuarios
            WHERE email = %s
        """, (email,))

        usuario = cur.fetchone()

        # Usuario no existe
        if not usuario:
            flash("Usuario no encontrado")
            return render_template("auth/login.html")

        # Password incorrecto
        if not check_password_hash(usuario[3], password):
            flash("Credenciales incorrectas")
            return render_template("auth/login.html")

        # Login correcto
        session["user_id"] = usuario[0]
        session["user_name"] = usuario[1]

        flash(f"Bienvenido {usuario[1]}")
        return redirect(url_for("routes.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():

    session.clear()
    flash("Sesión cerrada correctamente")

    return redirect(url_for("auth.login"))