from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from .decorators import login_required
import MySQLdb

agenda_bp = Blueprint("agenda", __name__, url_prefix="/agenda")


# ======================================
# LISTAR AGENDA
# ======================================
@agenda_bp.route("/")
@login_required
def index():

    cur = g.db.cursor(MySQLdb.cursors.DictCursor)

    cur.execute("""
        SELECT 
            a.id,
            CONCAT(p.nombre,' ',p.apellido) AS paciente,
            CONCAT(pr.nombre,' ',pr.apellido) AS profesional,
            a.fecha,
            a.hora
        FROM agenda a
        JOIN pacientes p ON a.paciente_id = p.id
        JOIN profesionales pr ON a.profesional_id = pr.id
        ORDER BY a.fecha, a.hora
    """)

    citas = cur.fetchall()

    return render_template(
        "agenda.html",
        citas=citas
    )


# ======================================
# CREAR CITA (ADMIN)
# ======================================
@agenda_bp.route("/create", methods=["POST"])
@login_required
def create():

    paciente_id = request.form["paciente_id"]
    profesional_id = request.form["profesional_id"]
    fecha = request.form["fecha"]
    hora = request.form["hora"]

    cur = g.db.cursor()

    cur.execute("""
        INSERT INTO agenda
        (paciente_id, profesional_id, fecha, hora)
        VALUES (%s,%s,%s,%s)
    """, (paciente_id, profesional_id, fecha, hora))

    g.db.commit()

    flash("Cita creada correctamente")

    return redirect(url_for("agenda.index"))


# ======================================
# CREAR CITA PUBLICA
# ======================================
@agenda_bp.route("/public_create", methods=["POST"])
def public_create():

    rut = request.form["rut"]
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    profesional_id = request.form["profesional_id"]
    fecha = request.form["fecha"]
    hora = request.form["hora"]

    cur = g.db.cursor(MySQLdb.cursors.DictCursor)

    cur.execute(
        "SELECT id FROM pacientes WHERE rut=%s",
        (rut,)
    )

    paciente = cur.fetchone()

    if paciente:
        paciente_id = paciente["id"]
    else:

        cur.execute("""
            INSERT INTO pacientes
            (rut,nombre,apellido)
            VALUES (%s,%s,%s)
        """, (rut, nombre, apellido))

        g.db.commit()

        paciente_id = cur.lastrowid

    cur.execute("""
        INSERT INTO agenda
        (paciente_id, profesional_id, fecha, hora)
        VALUES (%s,%s,%s,%s)
    """, (paciente_id, profesional_id, fecha, hora))

    g.db.commit()

    flash("Evaluación agendada correctamente")

    return redirect(url_for("routes.dashboard"))


# ======================================
# ELIMINAR CITA
# ======================================
@agenda_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):

    cur = g.db.cursor()

    cur.execute(
        "DELETE FROM agenda WHERE id=%s",
        (id,)
    )

    g.db.commit()

    flash("Cita eliminada")

    return redirect(url_for("agenda.index"))