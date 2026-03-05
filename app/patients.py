from flask import Blueprint, render_template, g, request, redirect, url_for
from .decorators import login_required, role_required
from MySQLdb.cursors import DictCursor

patients_bp = Blueprint(
    "patients",
    __name__,
    url_prefix="/patients"
)


# ==============================
# LISTAR PACIENTES
# ==============================

@patients_bp.route("/")
@login_required
@role_required("admin")
def index():

    cur = g.db.cursor(DictCursor)

    cur.execute("SELECT * FROM pacientes")

    pacientes = cur.fetchall()

    return render_template(
        "patients.html",
        pacientes=pacientes
    )


# ==============================
# CREAR PACIENTE
# ==============================

@patients_bp.route("/create", methods=["POST"])
@login_required
@role_required("admin")
def create():

    rut = request.form["rut"]
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    fecha_nacimiento = request.form["fecha_nacimiento"]
    email = request.form["email"]
    telefono = request.form["telefono"]

    cur = g.db.cursor()

    cur.execute("""
        INSERT INTO pacientes
        (rut, nombre, apellido, fecha_nacimiento, email, telefono)
        VALUES (%s,%s,%s,%s,%s,%s)
    """,(
        rut,
        nombre,
        apellido,
        fecha_nacimiento,
        email,
        telefono
    ))

    g.db.commit()

    return redirect(url_for("patients.index"))


# ==============================
# EDITAR PACIENTE
# ==============================

@patients_bp.route("/edit/<int:id>", methods=["POST"])
@login_required
@role_required("admin")
def edit(id):

    rut = request.form["rut"]
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    fecha_nacimiento = request.form["fecha_nacimiento"]
    email = request.form["email"]
    telefono = request.form["telefono"]

    cur = g.db.cursor()

    cur.execute("""
        UPDATE pacientes
        SET rut=%s,
            nombre=%s,
            apellido=%s,
            fecha_nacimiento=%s,
            email=%s,
            telefono=%s
        WHERE id=%s
    """,(
        rut,
        nombre,
        apellido,
        fecha_nacimiento,
        email,
        telefono,
        id
    ))

    g.db.commit()

    return redirect(url_for("patients.index"))


# ==============================
# ELIMINAR PACIENTE
# ==============================

@patients_bp.route("/delete/<int:id>")
@login_required
@role_required("admin")
def delete(id):

    cur = g.db.cursor()

    cur.execute(
        "DELETE FROM pacientes WHERE id=%s",
        (id,)
    )

    g.db.commit()

    return redirect(url_for("patients.index"))