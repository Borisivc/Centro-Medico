from flask import Blueprint, render_template, g
from MySQLdb.cursors import DictCursor

main_bp = Blueprint(
    "main",
    __name__
)


@main_bp.route("/")
def dashboard():

    cur = g.db.cursor(DictCursor)

    # ==========================
    # ESPECIALIDADES
    # ==========================

    cur.execute("""
        SELECT 
            id,
            nombre
        FROM especialidades
        ORDER BY nombre
    """)

    specialties = cur.fetchall()

    # ==========================
    # PROFESIONALES
    # ==========================

    cur.execute("""
        SELECT 
            p.id,
            p.nombre,
            pe.especialidad_id
        FROM profesionales p
        LEFT JOIN profesionales_especialidades pe
            ON p.id = pe.profesional_id
        ORDER BY p.nombre
    """)

    professionals = cur.fetchall()

    return render_template(
        "dashboard.html",
        specialties=specialties,
        professionals=professionals
    )