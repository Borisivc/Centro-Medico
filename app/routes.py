from flask import Blueprint, render_template, session, redirect, url_for

routes_bp = Blueprint("routes", __name__)


@routes_bp.route("/")
def home():

    if session.get("user_id"):
        return redirect(url_for("routes.dashboard"))

    return redirect(url_for("auth.login"))


@routes_bp.route("/dashboard")
def dashboard():

    if not session.get("user_id"):
        return redirect(url_for("auth.login"))

    return render_template("dashboard.html")