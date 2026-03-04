import MySQLdb
from flask import Blueprint, render_template, request, redirect, url_for, g, flash
from .decorators import login_required, role_required

professionals_bp = Blueprint("professionals", __name__, url_prefix="/professionals")


# ===============================
# LISTAR PROFESIONALES
# ===============================
@professionals_bp.route("/")
@login_required
@role_required("ADMIN")
def index():

    cur = g.db.cursor(MySQLdb.cursors.DictCursor)

    cur.execute("""
        SELECT id, rut, nombre, apellido, especialidad, email, telefono
        FROM profesionales
        ORDER BY id ASC
    """)

    profesionales = cur.fetchall()

    return render_template(
        "professionals/index.html",
        profesionales=profesionales
    )


# ===============================
# CREAR PROFESIONAL
# ===============================
@professionals_bp.route("/create", methods=["GET","POST"])
@login_required
@role_required("ADMIN")
def create():

    if request.method == "POST":

        rut = request.form["rut"]
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        especialidad = request.form["especialidad"]
        email = request.form["email"]
        telefono = request.form["telefono"]

        cur = g.db.cursor()

        try:

            cur.execute("""
                INSERT INTO profesionales
                (rut, nombre, apellido, especialidad, email, telefono)
                VALUES (%s,%s,%s,%s,%s,%s)
            """,(rut,nombre,apellido,especialidad,email,telefono))

            g.db.commit()

            flash("Profesional creado correctamente")

            return redirect(url_for("professionals.index"))

        except MySQLdb.IntegrityError:

            flash("El RUT ya existe en el sistema")

    return render_template("professionals/create.html")


# ===============================
# EDITAR PROFESIONAL
# ===============================
@professionals_bp.route("/edit/<int:id>", methods=["GET","POST"])
@login_required
@role_required("ADMIN")
def edit(id):

    cur = g.db.cursor(MySQLdb.cursors.DictCursor)

    # Buscar profesional
    cur.execute("""
        SELECT id, rut, nombre, apellido, especialidad, email, telefono
        FROM profesionales
        WHERE id=%s
    """,(id,))

    profesional = cur.fetchone()

    if not profesional:

        flash("Profesional no encontrado")

        return redirect(url_for("professionals.index"))


    if request.method == "POST":

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
        """,(rut,nombre,apellido,especialidad,email,telefono,id))

        g.db.commit()

        flash("Profesional actualizado correctamente")

        return redirect(url_for("professionals.index"))

    return render_template(
        "professionals/edit.html",
        profesional=profesional
    )


# ===============================
# ELIMINAR PROFESIONAL
# ===============================
@professionals_bp.route("/delete/<int:id>")
@login_required
@role_required("ADMIN")
def delete(id):

    cur = g.db.cursor()

    cur.execute("""
        DELETE FROM profesionales
        WHERE id=%s
    """,(id,))

    g.db.commit()

    flash("Profesional eliminado correctamente")

    return redirect(url_for("professionals.index"))