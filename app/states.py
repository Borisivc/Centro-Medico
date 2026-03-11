from flask import Blueprint, render_template, g
from .decorators import login_required
from MySQLdb.cursors import DictCursor

states_bp = Blueprint(
    "states",
    __name__,
    url_prefix="/states"
)


@states_bp.route("/")
@login_required
def index():

    cur = g.db.cursor(DictCursor)

    cur.execute("""
        SELECT *
        FROM estados_agenda
        ORDER BY nombre
    """)

    states = cur.fetchall()

    return render_template(
        "states.html",
        states=states
    )