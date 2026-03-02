from flask import Blueprint, render_template, redirect, url_for, session

routes_bp = Blueprint("routes", __name__)


@routes_bp.route("/")
def home():

    if not session.get("user_id"):
        return redirect(url_for("auth.login"))

    return redirect(url_for("routes.dashboard"))


@routes_bp.route("/dashboard")
def dashboard():

    if not session.get("user_id"):
        return redirect(url_for("auth.login"))

    return render_template("dashboard.html")