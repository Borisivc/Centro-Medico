from flask import Blueprint, render_template, g, request, redirect, url_for, flash
from .decorators import login_required, role_required
from MySQLdb.cursors import DictCursor

agenda_bp = Blueprint(
    "agenda",
    __name__,
    url_prefix="/agenda"
)


# ==============================
# LISTAR AGENDA
# ==============================

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
            a.estado
        FROM agenda a
        JOIN pacientes p ON p.id = a.paciente_id
        JOIN profesionales pr ON pr.id = a.profesional_id
        ORDER BY a.fecha, a.hora
    """)

    agenda = cur.fetchall()

    return render_template(
        "agenda.html",
        agenda=agenda
    )


# ==============================
# CREAR CITA DESDE ADMIN
# ==============================

@agenda_bp.route("/create", methods=["POST"])
@login_required
@role_required("ADMIN","PROFESIONAL","RECEPCION")
def create():

    paciente_id = request.form["paciente_id"]
    profesional_id = request.form["profesional_id"]
    fecha = request.form["fecha"]
    hora = request.form["hora"]
    estado = request.form["estado"]
    observacion = request.form["observacion"]

    cur = g.db.cursor()

    cur.execute("""
        INSERT INTO agenda
        (paciente_id, profesional_id, fecha, hora, estado, observacion)
        VALUES (%s,%s,%s,%s,%s,%s)
    """,(paciente_id, profesional_id, fecha, hora, estado, observacion))

    g.db.commit()

    flash("Cita creada correctamente")

    return redirect(url_for("agenda.index"))


# ==============================
# AGENDAR DESDE PAGINA PUBLICA
# ==============================

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
            (rut, nombre, apellido)
            VALUES (%s,%s,%s)
        """,(rut, nombre, apellido))

        paciente_id = cur.lastrowid

    else:

        paciente_id = paciente["id"]

    cur.execute("""
        INSERT INTO agenda
        (paciente_id, profesional_id, fecha, hora, estado)
        VALUES (%s,%s,%s,%s,'AGENDADA')
    """,(paciente_id, profesional_id, fecha, hora))

    g.db.commit()

    flash("Evaluación agendada correctamente")

    return redirect(url_for("main.dashboard"))


# ==============================
# ELIMINAR
# ==============================

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