from flask import Blueprint, render_template, session, redirect, url_for

routes_bp = Blueprint("routes", __name__)


# Ruta principal
@routes_bp.route("/")
def home():

    # Siempre mostrar login primero
    return redirect(url_for("auth.login"))


# Dashboard
@routes_bp.route("/dashboard")
def dashboard():

    # Si no hay sesión volver al login
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))

    return render_template("dashboard.html")