import MySQLdb
from flask import Blueprint, render_template, request, redirect, url_for, g, flash
from .decorators import login_required, role_required

roles_bp = Blueprint("roles", __name__, url_prefix="/roles")


# ==============================
# LISTAR ROLES
# ==============================
@roles_bp.route("/")
@login_required
@role_required("ADMIN")
def index():

    cur = g.db.cursor(MySQLdb.cursors.DictCursor)

    cur.execute("""
        SELECT id, nombre
        FROM roles
        ORDER BY id ASC
    """)

    roles = cur.fetchall()

    return render_template("roles/index.html", roles=roles)


# ==============================
# CREAR ROL
# ==============================
@roles_bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required("ADMIN")
def create():

    if request.method == "POST":

        nombre = request.form.get("nombre")

        if not nombre:
            flash("Debe ingresar un nombre de rol.")
            return redirect(url_for("roles.create"))

        cur = g.db.cursor()

        try:
            cur.execute("""
                INSERT INTO roles (nombre)
                VALUES (%s)
            """, (nombre,))

            g.db.commit()
            flash("Rol creado correctamente.")
            return redirect(url_for("roles.index"))

        except Exception:
            g.db.rollback()
            flash("Error al crear el rol (puede que ya exista).")

    return render_template("roles/create.html")


# ==============================
# EDITAR ROL
# ==============================
@roles_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
@role_required("ADMIN")
def edit(id):

    cur = g.db.cursor(MySQLdb.cursors.DictCursor)

    # Obtener rol
    cur.execute("SELECT id, nombre FROM roles WHERE id=%s", (id,))
    rol = cur.fetchone()

    if not rol:
        flash("Rol no encontrado.")
        return redirect(url_for("roles.index"))

    if request.method == "POST":

        nombre = request.form.get("nombre")

        if not nombre:
            flash("Debe ingresar un nombre.")
            return redirect(url_for("roles.edit", id=id))

        try:
            cur.execute("""
                UPDATE roles
                SET nombre=%s
                WHERE id=%s
            """, (nombre, id))

            g.db.commit()
            flash("Rol actualizado correctamente.")
            return redirect(url_for("roles.index"))

        except Exception:
            g.db.rollback()
            flash("Error al actualizar rol.")

    return render_template("roles/edit.html", rol=rol)


# ==============================
# ELIMINAR ROL (CON VALIDACIÓN)
# ==============================
@roles_bp.route("/delete/<int:id>")
@login_required
@role_required("ADMIN")
def delete(id):

    cur = g.db.cursor()

    try:
        # 🔍 VALIDAR SI TIENE USUARIOS ASIGNADOS
        cur.execute("""
            SELECT COUNT(*)
            FROM usuarios_roles
            WHERE rol_id=%s
        """, (id,))

        cantidad = cur.fetchone()[0]

        if cantidad > 0:
            flash("No se puede eliminar el rol porque tiene usuarios asignados.")
            return redirect(url_for("roles.index"))

        # Si no tiene usuarios, eliminar
        cur.execute("DELETE FROM roles WHERE id=%s", (id,))
        g.db.commit()

        flash("Rol eliminado correctamente.")

    except Exception:
        g.db.rollback()
        flash("Error inesperado al eliminar el rol.")

    return redirect(url_for("roles.index"))