from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from MySQLdb.cursors import DictCursor
from .decorators import login_required, role_required

agenda_bp = Blueprint(
    "agenda",
    __name__,
    url_prefix="/agenda"
)


# =========================
# LISTAR AGENDA
# =========================

@agenda_bp.route("/")
@login_required
def index():

    cur = g.db.cursor(DictCursor)

    cur.execute("""
        SELECT
            a.id,
            p.rut,
            p.nombre,
            p.apellido,
            pr.nombre AS profesional,
            a.fecha,
            a.hora,
            e.nombre AS estado
        FROM agenda a
        JOIN pacientes p ON p.id = a.paciente_id
        JOIN profesionales pr ON pr.id = a.profesional_id
        JOIN estados_agenda e ON e.id = a.estado_id
        ORDER BY a.fecha,a.hora
    """)

    agenda = cur.fetchall()

    cur.execute("""
        SELECT id,nombre
        FROM profesionales
        ORDER BY nombre
    """)

    professionals = cur.fetchall()

    return render_template(
        "agenda.html",
        agenda=agenda,
        professionals=professionals
    )


# =========================
# CREAR DESDE MANTENEDOR
# =========================

@agenda_bp.route("/create", methods=["POST"])
@login_required
@role_required("ADMIN","PROFESIONAL","RECEPCION")
def create():

    rut = request.form["rut"].replace(".", "").replace("-", "")
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    profesional_id = request.form["profesional_id"]
    fecha = request.form["fecha"]
    hora = request.form["hora"]

    cur = g.db.cursor(DictCursor)

    cur.execute(
        "SELECT id FROM pacientes WHERE rut=%s",
        (rut,)
    )

    paciente = cur.fetchone()

    if not paciente:

        cur.execute("""
            INSERT INTO pacientes
            (rut,nombre,apellido)
            VALUES (%s,%s,%s)
        """,(rut,nombre,apellido))

        paciente_id = cur.lastrowid

    else:

        paciente_id = paciente["id"]


    cur.execute("""
        SELECT id
        FROM estados_agenda
        WHERE nombre='AGENDADA'
    """)

    estado_id = cur.fetchone()["id"]

    cur.execute("""
        INSERT INTO agenda
        (paciente_id,profesional_id,fecha,hora,estado_id)
        VALUES (%s,%s,%s,%s,%s)
    """,(paciente_id,profesional_id,fecha,hora,estado_id))

    g.db.commit()

    flash("Cita creada correctamente")

    return redirect(url_for("agenda.index"))


# =========================
# CREAR DESDE WEB PUBLICA
# =========================

@agenda_bp.route("/public_create", methods=["POST"])
def public_create():

    rut = request.form["rut"].replace(".", "").replace("-", "")
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    profesional_id = request.form["profesional_id"]
    fecha = request.form["fecha"]
    hora = request.form["hora"]

    cur = g.db.cursor(DictCursor)

    cur.execute(
        "SELECT id FROM pacientes WHERE rut=%s",
        (rut,)
    )

    paciente = cur.fetchone()

    if not paciente:

        cur.execute("""
            INSERT INTO pacientes
            (rut,nombre,apellido)
            VALUES (%s,%s,%s)
        """,(rut,nombre,apellido))

        paciente_id = cur.lastrowid

    else:

        paciente_id = paciente["id"]


    cur.execute("""
        SELECT id
        FROM estados_agenda
        WHERE nombre='AGENDADA'
    """)

    estado_id = cur.fetchone()["id"]

    cur.execute("""
        INSERT INTO agenda
        (paciente_id,profesional_id,fecha,hora,estado_id)
        VALUES (%s,%s,%s,%s,%s)
    """,(paciente_id,profesional_id,fecha,hora,estado_id))

    g.db.commit()

    flash("Su hora ha sido agendada correctamente")

    return redirect(url_for("main.dashboard"))


# =========================
# ANULAR CITA
# =========================

@agenda_bp.route("/anular/<int:id>")
@login_required
@role_required("ADMIN","PROFESIONAL","RECEPCION")
def anular(id):

    cur = g.db.cursor()

    cur.execute("""
        UPDATE agenda
        SET estado_id = (
            SELECT id
            FROM estados_agenda
            WHERE nombre='ANULADA'
        )
        WHERE id=%s
    """,(id,))

    g.db.commit()

    flash("Cita anulada")

    return redirect(url_for("agenda.index"))


# =========================
# ELIMINAR
# =========================

@agenda_bp.route("/delete/<int:id>")
@login_required
@role_required("ADMIN","PROFESIONAL","RECEPCION")
def delete(id):

    cur = g.db.cursor()

    cur.execute(
        "DELETE FROM agenda WHERE id=%s",
        (id,)
    )

    g.db.commit()

    flash("Cita eliminada")

    return redirect(url_for("agenda.index"))