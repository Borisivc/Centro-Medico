from flask import Blueprint, render_template, g
from .decorators import login_required, role_required
from MySQLdb.cursors import DictCursor

roles_bp = Blueprint(
    "roles",
    __name__,
    url_prefix="/roles"
)


@roles_bp.route("/")
@login_required
@role_required("admin")
def index():

    cur = g.db.cursor(DictCursor)

    cur.execute("SELECT * FROM roles")

    roles = cur.fetchall()

    return render_template(
        "roles.html",
        roles=roles
    )