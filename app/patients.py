from flask import Blueprint, render_template, request, redirect, url_for, g, session, flash
from functools import wraps
import MySQLdb

# Blueprint
bp = Blueprint("patients", __name__, url_prefix="/patients")


# -------------------------
# Decorador login requerido
# -------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not session.get("user_id"):
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)

    return decorated_function


# -------------------------
# LISTAR PACIENTES
# -------------------------
@bp.route("/")
@login_required
def index():

    cur = g.db.cursor()

    cur.execute("""
        SELECT id, rut, nombre, apellido, email, fecha_nacimiento
        FROM pacientes
        ORDER BY id DESC
    """)

    pacientes = cur.fetchall()

    return render_template("patients/index.html", pacientes=pacientes)


# -------------------------
# CREAR PACIENTE
# -------------------------
@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():

    if request.method == "POST":

        rut = request.form["rut"]
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        email = request.form.get("email")
        fecha_nacimiento = request.form["fecha_nacimiento"]

        cur = g.db.cursor()

        try:

            cur.execute("""
                INSERT INTO pacientes
                (rut, nombre, apellido, email, fecha_nacimiento)
                VALUES (%s, %s, %s, %s, %s)
            """, (rut, nombre, apellido, email, fecha_nacimiento))

            g.db.commit()

            flash("Paciente creado correctamente", "success")

            return redirect(url_for("patients.index"))

        except MySQLdb.IntegrityError:

            flash("⚠️ El RUT ya existe en el sistema", "error")

            return redirect(url_for("patients.create"))

    return render_template("patients/create.html")


# -------------------------
# EDITAR PACIENTE
# -------------------------
@bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):

    cur = g.db.cursor()

    if request.method == "POST":

        rut = request.form["rut"]
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        email = request.form.get("email")
        fecha_nacimiento = request.form["fecha_nacimiento"]

        try:

            cur.execute("""
                UPDATE pacientes
                SET rut=%s,
                    nombre=%s,
                    apellido=%s,
                    email=%s,
                    fecha_nacimiento=%s
                WHERE id=%s
            """, (rut, nombre, apellido, email, fecha_nacimiento, id))

            g.db.commit()

            flash("Paciente actualizado correctamente", "success")

            return redirect(url_for("patients.index"))

        except MySQLdb.IntegrityError:

            flash("⚠️ El RUT ya pertenece a otro paciente", "error")

            return redirect(url_for("patients.edit", id=id))

    cur.execute("""
        SELECT id, rut, nombre, apellido, email, fecha_nacimiento
        FROM pacientes
        WHERE id=%s
    """, (id,))

    paciente = cur.fetchone()

    return render_template("patients/edit.html", paciente=paciente)


# -------------------------
# ELIMINAR PACIENTE
# -------------------------
@bp.route("/delete/<int:id>")
@login_required
def delete(id):

    cur = g.db.cursor()

    cur.execute("DELETE FROM pacientes WHERE id=%s", (id,))

    g.db.commit()

    flash("Paciente eliminado correctamente", "success")

    return redirect(url_for("patients.index"))