from flask import Blueprint, request, redirect, url_for, session, g, flash
from MySQLdb.cursors import DictCursor
from werkzeug.security import check_password_hash
import logging

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


# LOGIN

@auth_bp.route("/login", methods=["POST"])
def login():

    try:

        email = request.form.get("email")
        password = request.form.get("password")

        cur = g.db.cursor(DictCursor)

        cur.execute("""
            SELECT id, nombre, email, password_hash, activo
            FROM usuarios
            WHERE email = %s
        """, (email,))

        user = cur.fetchone()

        if not user:
            flash("Credenciales incorrectas", "login_error")
            return redirect(url_for("main.dashboard"))

        if user["activo"] != 1:
            flash("Usuario deshabilitado", "login_error")
            return redirect(url_for("main.dashboard"))

        if not check_password_hash(user["password_hash"], password):
            flash("Credenciales incorrectas", "login_error")
            return redirect(url_for("main.dashboard"))

        session["user_id"] = user["id"]
        session["user_nombre"] = user["nombre"]
        session["user_email"] = user["email"]

        logging.info(f"Login exitoso: {user['email']}")

        return redirect(url_for("main.dashboard"))

    except Exception as e:

        logging.exception("Error en login")

        flash("Error al iniciar sesión", "login_error")

        return redirect(url_for("main.dashboard"))


# LOGOUT

@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("main.dashboard"))