from flask import Blueprint, render_template
from .decorators import login_required, role_required

routes_bp = Blueprint("routes", __name__)

@routes_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@routes_bp.route("/admin")
@login_required
@role_required("admin")
def admin_panel():
    return "<h1>Panel de Administración</h1>"


@routes_bp.route("/profesional")
@login_required
@role_required("profesional")
def profesional_panel():
    return "<h1>Panel Profesional</h1>"