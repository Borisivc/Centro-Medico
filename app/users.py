from flask import Blueprint, render_template, g
from .decorators import login_required, role_required
from MySQLdb.cursors import DictCursor

users_bp = Blueprint(
    "users",
    __name__,
    url_prefix="/users"
)


@users_bp.route("/")
@login_required
@role_required("admin")
def index():

    cur = g.db.cursor(DictCursor)

    cur.execute("SELECT * FROM usuarios")

    usuarios = cur.fetchall()

    return render_template(
        "users.html",
        usuarios=usuarios
    )