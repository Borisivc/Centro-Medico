from flask import Blueprint, render_template, request, redirect, url_for, g, flash
from .decorators import login_required, role_required

patients_bp = Blueprint("patients", __name__, url_prefix="/patients")


# ==============================
# LISTAR PACIENTES
# ==============================
@patients_bp.route("/")
@login_required
@role_required("ADMIN")
def index():

    cur = g.db.cursor()
    cur.execute("""
        SELECT id, rut, nombre, apellido, email, fecha_nacimiento
        FROM pacientes
        ORDER BY id ASC
    """)

    pacientes = cur.fetchall()

    return render_template("patients/index.html", pacientes=pacientes)


# ==============================
# CREAR PACIENTE
# ==============================
@patients_bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required("ADMIN")
def create():

    if request.method == "POST":

        cur = g.db.cursor()

        cur.execute("""
            INSERT INTO pacientes
            (rut, nombre, apellido, email, fecha_nacimiento)
            VALUES (%s,%s,%s,%s,%s)
        """, (
            request.form["rut"],
            request.form["nombre"],
            request.form["apellido"],
            request.form["email"],
            request.form["fecha_nacimiento"]
        ))

        g.db.commit()
        flash("Paciente creado correctamente")
        return redirect(url_for("patients.index"))

    return render_template("patients/create.html")


# ==============================
# EDITAR PACIENTE
# ==============================
@patients_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
@role_required("ADMIN")
def edit(id):

    cur = g.db.cursor()

    if request.method == "POST":

        cur.execute("""
            UPDATE pacientes
            SET rut=%s, nombre=%s, apellido=%s,
                email=%s, fecha_nacimiento=%s
            WHERE id=%s
        """, (
            request.form["rut"],
            request.form["nombre"],
            request.form["apellido"],
            request.form["email"],
            request.form["fecha_nacimiento"],
            id
        ))

        g.db.commit()
        flash("Paciente actualizado correctamente")
        return redirect(url_for("patients.index"))

    cur.execute("""
        SELECT id, rut, nombre, apellido, email, fecha_nacimiento
        FROM pacientes
        WHERE id=%s
    """, (id,))

    paciente = cur.fetchone()

    if not paciente:
        flash("Paciente no encontrado")
        return redirect(url_for("patients.index"))

    return render_template("patients/edit.html", paciente=paciente)


# ==============================
# ELIMINAR PACIENTE
# ==============================
@patients_bp.route("/delete/<int:id>")
@login_required
@role_required("ADMIN")
def delete(id):

    cur = g.db.cursor()

    try:
        cur.execute("DELETE FROM pacientes WHERE id=%s", (id,))
        g.db.commit()
        flash("Paciente eliminado correctamente")
    except:
        g.db.rollback()
        flash("Error al eliminar paciente")

    return redirect(url_for("patients.index"))