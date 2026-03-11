from flask import Blueprint, render_template, g, request, redirect, url_for, flash
from .decorators import login_required, role_required
from MySQLdb.cursors import DictCursor

specialties_bp = Blueprint(
    "specialties",
    __name__,
    url_prefix="/specialties"
)


# ==============================
# LISTAR
# ==============================

@specialties_bp.route("/")
@login_required
@role_required("admin")
def index():

    cur = g.db.cursor(DictCursor)

    cur.execute("SELECT * FROM especialidades")

    especialidades = cur.fetchall()

    return render_template(
        "specialties.html",
        especialidades=especialidades
    )


# ==============================
# CREAR
# ==============================

@specialties_bp.route("/create", methods=["POST"])
@login_required
@role_required("admin")
def create():

    nombre = request.form["nombre"].upper()

    cur = g.db.cursor()

    cur.execute(
        "INSERT INTO especialidades (nombre) VALUES (%s)",
        (nombre,)
    )

    g.db.commit()

    flash("Especialidad creada")

    return redirect(url_for("specialties.index"))


# ==============================
# EDITAR
# ==============================

@specialties_bp.route("/edit/<int:id>", methods=["POST"])
@login_required
@role_required("admin")
def edit(id):

    nombre = request.form["nombre"].upper()

    cur = g.db.cursor()

    cur.execute(
        "UPDATE especialidades SET nombre=%s WHERE id=%s",
        (nombre,id)
    )

    g.db.commit()

    flash("Especialidad actualizada")

    return redirect(url_for("specialties.index"))


# ==============================
# ELIMINAR
# ==============================

@specialties_bp.route("/delete/<int:id>")
@login_required
@role_required("admin")
def delete(id):

    cur = g.db.cursor()

    cur.execute(
        "DELETE FROM especialidades WHERE id=%s",
        (id,)
    )

    g.db.commit()

    flash("Especialidad eliminada")

    return redirect(url_for("specialties.index"))