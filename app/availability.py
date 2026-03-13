from flask import Blueprint, render_template, request, redirect, url_for, g
from MySQLdb.cursors import DictCursor
from .decorators import login_required


availability_bp = Blueprint(
    "availability",
    __name__,
    url_prefix="/availability"
)


# ======================================
# LISTAR DISPONIBILIDAD
# ======================================

@availability_bp.route("/")
@login_required
def index():

    cur = g.db.cursor(DictCursor)

    cur.execute("""
        SELECT 
            d.id,
            p.nombre profesional,
            d.dia_semana,
            d.hora_inicio,
            d.hora_fin,
            d.fecha_inicio,
            d.fecha_fin,
            d.duracion_cita
        FROM disponibilidad_profesional d
        JOIN profesionales p
        ON p.id = d.profesional_id
        ORDER BY p.nombre
    """)

    disponibilidad = cur.fetchall()

    cur.execute("""
        SELECT id,nombre
        FROM profesionales
        ORDER BY nombre
    """)

    profesionales = cur.fetchall()

    return render_template(
        "availability.html",
        disponibilidad=disponibilidad,
        profesionales=profesionales
    )


# ======================================
# CREAR DISPONIBILIDAD
# ======================================

@availability_bp.route("/create", methods=["POST"])
@login_required
def create():

    profesional_id = request.form["profesional_id"]
    dia_semana = request.form["dia_semana"]
    hora_inicio = request.form["hora_inicio"]
    hora_fin = request.form["hora_fin"]
    fecha_inicio = request.form["fecha_inicio"]
    fecha_fin = request.form["fecha_fin"]
    duracion_cita = request.form["duracion_cita"]

    cur = g.db.cursor()

    cur.execute("""
        INSERT INTO disponibilidad_profesional
        (
            profesional_id,
            dia_semana,
            hora_inicio,
            hora_fin,
            fecha_inicio,
            fecha_fin,
            duracion_cita
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """,(
        profesional_id,
        dia_semana,
        hora_inicio,
        hora_fin,
        fecha_inicio,
        fecha_fin,
        duracion_cita
    ))

    g.db.commit()

    return redirect(url_for("availability.index"))