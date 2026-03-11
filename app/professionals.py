from flask import Blueprint, render_template, g, request, redirect, url_for, flash
from .decorators import login_required, role_required
from MySQLdb.cursors import DictCursor

professionals_bp = Blueprint(
    "professionals",
    __name__,
    url_prefix="/professionals"
)


# ==============================
# LISTAR PROFESIONALES
# ==============================

@professionals_bp.route("/")
@login_required
@role_required("admin")
def index():

    cur = g.db.cursor(DictCursor)

    cur.execute("""
        SELECT 
            p.id,
            p.rut,
            p.nombre,
            p.apellido,
            p.email,
            p.telefono,
            GROUP_CONCAT(e.nombre SEPARATOR ', ') AS especialidades
        FROM profesionales p
        LEFT JOIN profesionales_especialidades pe 
            ON pe.profesional_id = p.id
        LEFT JOIN especialidades e 
            ON e.id = pe.especialidad_id
        GROUP BY p.id
    """)

    profesionales = cur.fetchall()

    cur.execute("SELECT * FROM especialidades")
    especialidades = cur.fetchall()

    cur.execute("""
        SELECT profesional_id, especialidad_id
        FROM profesionales_especialidades
    """)

    profesionales_especialidades = cur.fetchall()

    return render_template(
        "professionals.html",
        profesionales=profesionales,
        especialidades=especialidades,
        profesionales_especialidades=profesionales_especialidades
    )


# ==============================
# CREAR PROFESIONAL
# ==============================

@professionals_bp.route("/create", methods=["POST"])
@login_required
@role_required("admin")
def create():

    rut = request.form["rut"]
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    email = request.form["email"]
    telefono = request.form["telefono"]

    especialidades = request.form.getlist("especialidades")

    cur = g.db.cursor()

    cur.execute("""
        INSERT INTO profesionales
        (rut,nombre,apellido,email,telefono)
        VALUES (%s,%s,%s,%s,%s)
    """,(rut,nombre,apellido,email,telefono))

    profesional_id = cur.lastrowid

    for esp in especialidades:

        cur.execute("""
            INSERT INTO profesionales_especialidades
            (profesional_id,especialidad_id)
            VALUES (%s,%s)
        """,(profesional_id,esp))

    g.db.commit()

    flash("Profesional creado")

    return redirect(url_for("professionals.index"))


# ==============================
# EDITAR PROFESIONAL
# ==============================

@professionals_bp.route("/edit/<int:id>", methods=["POST"])
@login_required
@role_required("admin")
def edit(id):

    rut = request.form["rut"]
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    email = request.form["email"]
    telefono = request.form["telefono"]

    especialidades = request.form.getlist("especialidades")

    cur = g.db.cursor()

    cur.execute("""
        UPDATE profesionales
        SET rut=%s,
            nombre=%s,
            apellido=%s,
            email=%s,
            telefono=%s
        WHERE id=%s
    """,(rut,nombre,apellido,email,telefono,id))

    cur.execute(
        "DELETE FROM profesionales_especialidades WHERE profesional_id=%s",
        (id,)
    )

    for esp in especialidades:

        cur.execute("""
            INSERT INTO profesionales_especialidades
            (profesional_id,especialidad_id)
            VALUES (%s,%s)
        """,(id,esp))

    g.db.commit()

    flash("Profesional actualizado")

    return redirect(url_for("professionals.index"))


# ==============================
# ELIMINAR PROFESIONAL
# ==============================

@professionals_bp.route("/delete/<int:id>")
@login_required
@role_required("admin")
def delete(id):

    cur = g.db.cursor()

    cur.execute(
        "DELETE FROM profesionales_especialidades WHERE profesional_id=%s",
        (id,)
    )

    cur.execute(
        "DELETE FROM profesionales WHERE id=%s",
        (id,)
    )

    g.db.commit()

    flash("Profesional eliminado")

    return redirect(url_for("professionals.index"))