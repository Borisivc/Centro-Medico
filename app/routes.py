from flask import Blueprint, render_template, g, jsonify

main_bp = Blueprint("main", __name__)


# ===============================
# DASHBOARD
# ===============================
@main_bp.route("/")
def dashboard():

    cur = g.db.cursor()

    # ESPECIALIDADES
    cur.execute("""
        SELECT id, nombre
        FROM especialidades
        ORDER BY nombre
    """)

    specialties = cur.fetchall()

    return render_template(
        "dashboard.html",
        specialties=specialties
    )


# ===============================
# PROFESIONALES POR ESPECIALIDAD
# ===============================
@main_bp.route("/profesionales/<int:especialidad_id>")
def profesionales_por_especialidad(especialidad_id):

    cur = g.db.cursor()

    cur.execute("""
        SELECT DISTINCT
            p.id,
            p.nombre
        FROM profesionales p
        JOIN profesionales_especialidades pe
            ON p.id = pe.profesional_id
        WHERE pe.especialidad_id = %s
        ORDER BY p.nombre
    """, (especialidad_id,))

    rows = cur.fetchall()

    profesionales = []

    for r in rows:
        profesionales.append({
            "id": r[0],
            "nombre": r[1]
        })

    return jsonify(profesionales)