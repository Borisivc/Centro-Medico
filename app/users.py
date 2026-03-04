import MySQLdb
from flask import Blueprint, render_template, request, redirect, url_for, g, flash
from werkzeug.security import generate_password_hash
from .decorators import login_required, role_required

# 🔹 EL BLUEPRINT SIEMPRE VA ARRIBA
users_bp = Blueprint("users", __name__, url_prefix="/users")


# ==============================
# LISTAR USUARIOS
# ==============================
@users_bp.route("/")
@login_required
@role_required("ADMIN")
def index():

    cur = g.db.cursor(MySQLdb.cursors.DictCursor)

    cur.execute("""
        SELECT id, nombre, email
        FROM usuarios
        ORDER BY id ASC
    """)

    usuarios = cur.fetchall()

    return render_template("users/index.html", usuarios=usuarios)


# ==============================
# CREAR USUARIO
# ==============================
@users_bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required("ADMIN")
def create():

    cur = g.db.cursor(MySQLdb.cursors.DictCursor)

    # Obtener roles disponibles
    cur.execute("SELECT id, nombre FROM roles ORDER BY nombre ASC")
    roles = cur.fetchall()

    if request.method == "POST":

        nombre = request.form["nombre"]
        email = request.form["email"]
        password = request.form["password"]
        roles_seleccionados = request.form.getlist("roles")

        password_hash = generate_password_hash(password)

        try:
            cur.execute("""
                INSERT INTO usuarios (nombre, email, password_hash)
                VALUES (%s,%s,%s)
            """, (nombre, email, password_hash))

            usuario_id = cur.lastrowid

            for rol_id in roles_seleccionados:
                cur.execute("""
                    INSERT INTO usuarios_roles (usuario_id, rol_id)
                    VALUES (%s,%s)
                """, (usuario_id, rol_id))

            g.db.commit()
            flash("Usuario creado correctamente")
            return redirect(url_for("users.index"))

        except Exception:
            g.db.rollback()
            flash("Error al crear usuario")

    return render_template("users/create.html", roles=roles)


# ==============================
# EDITAR USUARIO
# ==============================
@users_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
@role_required("ADMIN")
def edit(id):

    cur = g.db.cursor(MySQLdb.cursors.DictCursor)

    # Obtener usuario
    cur.execute("""
        SELECT id, nombre, email
        FROM usuarios
        WHERE id=%s
    """, (id,))

    usuario = cur.fetchone()

    if not usuario:
        flash("Usuario no encontrado")
        return redirect(url_for("users.index"))

    # Obtener todos los roles
    cur.execute("SELECT id, nombre FROM roles ORDER BY nombre ASC")
    roles = cur.fetchall()

    # Obtener roles actuales del usuario
    cur.execute("""
        SELECT rol_id
        FROM usuarios_roles
        WHERE usuario_id=%s
    """, (id,))

    roles_usuario = [r["rol_id"] for r in cur.fetchall()]

    if request.method == "POST":

        nombre = request.form["nombre"]
        email = request.form["email"]
        roles_seleccionados = request.form.getlist("roles")

        try:
            cur.execute("""
                UPDATE usuarios
                SET nombre=%s, email=%s
                WHERE id=%s
            """, (nombre, email, id))

            cur.execute("""
                DELETE FROM usuarios_roles
                WHERE usuario_id=%s
            """, (id,))

            for rol_id in roles_seleccionados:
                cur.execute("""
                    INSERT INTO usuarios_roles (usuario_id, rol_id)
                    VALUES (%s,%s)
                """, (id, rol_id))

            g.db.commit()
            flash("Usuario actualizado correctamente")
            return redirect(url_for("users.index"))

        except Exception:
            g.db.rollback()
            flash("Error al actualizar usuario")

    return render_template(
        "users/edit.html",
        usuario=usuario,
        roles=roles,
        roles_usuario=roles_usuario
    )


# ==============================
# ELIMINAR USUARIO
# ==============================
@users_bp.route("/delete/<int:id>")
@login_required
@role_required("ADMIN")
def delete(id):

    cur = g.db.cursor()

    try:
        cur.execute("DELETE FROM usuarios_roles WHERE usuario_id=%s", (id,))
        cur.execute("DELETE FROM usuarios WHERE id=%s", (id,))
        g.db.commit()
        flash("Usuario eliminado correctamente")

    except Exception:
        g.db.rollback()
        flash("Error al eliminar usuario")

    return redirect(url_for("users.index"))