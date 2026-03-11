from flask import Blueprint, render_template, g
from MySQLdb.cursors import DictCursor

main_bp = Blueprint(
    "main",
    __name__
)


@main_bp.route("/")
def dashboard():

    cur = g.db.cursor(DictCursor)

    # ==============================
    # ESPECIALIDADES
    # ==============================

    cur.execute("""
        SELECT id, nombre
        FROM especialidades
        ORDER BY nombre
    """)

    especialidades = cur.fetchall()

    # ==============================
    # PROFESIONALES + ESPECIALIDAD
    # ==============================

    cur.execute("""
        SELECT 
            p.id,
            p.nombre,
            pe.especialidad_id
        FROM profesionales p
        LEFT JOIN profesionales_especialidades pe
        ON pe.profesional_id = p.id
        ORDER BY p.nombre
    """)

    profesionales = cur.fetchall()

    return render_template(
        "dashboard.html",
        especialidades=especialidades,
        profesionales=profesionales
    )