from flask import Blueprint, render_template, g, request, redirect, url_for, flash
from .decorators import login_required, role_required
from MySQLdb.cursors import DictCursor

roles_bp = Blueprint(
    "roles",
    __name__,
    url_prefix="/roles"
)


# ==============================
# LISTAR
# ==============================

@roles_bp.route("/")
@login_required
@role_required("ADMIN")
def index():

    cur = g.db.cursor(DictCursor)

    cur.execute("SELECT * FROM roles ORDER BY nombre")

    roles = cur.fetchall()

    return render_template(
        "roles.html",
        roles=roles
    )


# ==============================
# CREAR
# ==============================

@roles_bp.route("/create", methods=["POST"])
@login_required
@role_required("ADMIN")
def create():

    nombre = request.form["nombre"].strip().upper()

    cur = g.db.cursor()

    cur.execute(
        "INSERT INTO roles (nombre) VALUES (%s)",
        (nombre,)
    )

    g.db.commit()

    flash("Rol creado correctamente")

    return redirect(url_for("roles.index"))


# ==============================
# EDITAR
# ==============================

@roles_bp.route("/edit/<int:id>", methods=["POST"])
@login_required
@role_required("ADMIN")
def edit(id):

    nombre = request.form["nombre"].strip().upper()

    cur = g.db.cursor()

    cur.execute(
        "UPDATE roles SET nombre=%s WHERE id=%s",
        (nombre, id)
    )

    g.db.commit()

    flash("Rol actualizado")

    return redirect(url_for("roles.index"))


# ==============================
# ELIMINAR
# ==============================

@roles_bp.route("/delete/<int:id>")
@login_required
@role_required("ADMIN")
def delete(id):

    cur = g.db.cursor()

    cur.execute(
        "DELETE FROM roles WHERE id=%s",
        (id,)
    )

    g.db.commit()

    flash("Rol eliminado")

    return redirect(url_for("roles.index"))