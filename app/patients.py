from flask import Blueprint, render_template, request, redirect, url_for, g, session, flash
from functools import wraps
import MySQLdb

bp = Blueprint("patients", __name__, url_prefix="/patients")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not session.get("user_id"):
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)

    return decorated_function


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


@bp.route("/create", methods=["GET","POST"])
@login_required
def create():

    if request.method == "POST":

        rut = request.form.get("rut")
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        email = request.form.get("email")
        fecha_nacimiento = request.form.get("fecha_nacimiento")

        if not rut or not nombre or not apellido or not fecha_nacimiento:
            flash("Debe completar los campos obligatorios")
            return redirect(url_for("patients.create"))

        cur = g.db.cursor()

        try:

            cur.execute("""
                INSERT INTO pacientes
                (rut, nombre, apellido, email, fecha_nacimiento)
                VALUES (%s,%s,%s,%s,%s)
            """,(rut,nombre,apellido,email,fecha_nacimiento))

            g.db.commit()

            flash("Paciente creado correctamente")

            return redirect(url_for("patients.index"))

        except MySQLdb.IntegrityError:

            flash("El RUT ya existe en el sistema")

            return redirect(url_for("patients.create"))

    return render_template("patients/create.html")


@bp.route("/edit/<int:id>", methods=["GET","POST"])
@login_required
def edit(id):

    cur = g.db.cursor()

    if request.method == "POST":

        rut = request.form.get("rut")
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        email = request.form.get("email")
        fecha_nacimiento = request.form.get("fecha_nacimiento")

        cur.execute("""
            UPDATE pacientes
            SET rut=%s,
                nombre=%s,
                apellido=%s,
                email=%s,
                fecha_nacimiento=%s
            WHERE id=%s
        """,(rut,nombre,apellido,email,fecha_nacimiento,id))

        g.db.commit()

        flash("Paciente actualizado")

        return redirect(url_for("patients.index"))

    cur.execute("""
        SELECT id,rut,nombre,apellido,email,fecha_nacimiento
        FROM pacientes
        WHERE id=%s
    """,(id,))

    paciente = cur.fetchone()

    return render_template("patients/edit.html", paciente=paciente)


@bp.route("/delete/<int:id>")
@login_required
def delete(id):

    cur = g.db.cursor()

    cur.execute("DELETE FROM pacientes WHERE id=%s",(id,))

    g.db.commit()

    flash("Paciente eliminado")

    return redirect(url_for("patients.index"))