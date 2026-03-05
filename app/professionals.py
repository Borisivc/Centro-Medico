from flask import Blueprint, render_template, g, request, redirect, url_for
from .decorators import login_required, role_required
from MySQLdb.cursors import DictCursor

professionals_bp = Blueprint(
    "professionals",
    __name__,
    url_prefix="/professionals"
)


# ===============================
# LISTAR PROFESIONALES
# ===============================

@professionals_bp.route("/")
@login_required
@role_required("admin")
def index():

    cur = g.db.cursor(DictCursor)

    cur.execute("SELECT * FROM profesionales")

    profesionales = cur.fetchall()

    return render_template(
        "professionals.html",
        profesionales=profesionales
    )


# ===============================
# CREAR PROFESIONAL
# ===============================

@professionals_bp.route("/create", methods=["POST"])
@login_required
@role_required("admin")
def create():

    rut = request.form["rut"]
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    especialidad = request.form["especialidad"]
    email = request.form["email"]
    telefono = request.form["telefono"]

    cur = g.db.cursor()

    cur.execute("""
        INSERT INTO profesionales
        (rut, nombre, apellido, especialidad, email, telefono)
        VALUES (%s,%s,%s,%s,%s,%s)
    """,(
        rut,
        nombre,
        apellido,
        especialidad,
        email,
        telefono
    ))

    g.db.commit()

    return redirect(url_for("professionals.index"))


# ===============================
# EDITAR PROFESIONAL
# ===============================

@professionals_bp.route("/edit/<int:id>", methods=["POST"])
@login_required
@role_required("admin")
def edit(id):

    rut = request.form["rut"]
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    especialidad = request.form["especialidad"]
    email = request.form["email"]
    telefono = request.form["telefono"]

    cur = g.db.cursor()

    cur.execute("""
        UPDATE profesionales
        SET rut=%s,
            nombre=%s,
            apellido=%s,
            especialidad=%s,
            email=%s,
            telefono=%s
        WHERE id=%s
    """,(
        rut,
        nombre,
        apellido,
        especialidad,
        email,
        telefono,
        id
    ))

    g.db.commit()

    return redirect(url_for("professionals.index"))


# ===============================
# ELIMINAR PROFESIONAL
# ===============================

@professionals_bp.route("/delete/<int:id>")
@login_required
@role_required("admin")
def delete(id):

    cur = g.db.cursor()

    cur.execute(
        "DELETE FROM profesionales WHERE id=%s",
        (id,)
    )

    g.db.commit()

    return redirect(url_for("professionals.index"))