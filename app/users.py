from flask import Blueprint, render_template, g, request, redirect, url_for, flash
from .decorators import login_required, role_required
from MySQLdb.cursors import DictCursor
from werkzeug.security import generate_password_hash

users_bp = Blueprint(
    "users",
    __name__,
    url_prefix="/users"
)

# ==============================
# LISTAR USUARIOS
# ==============================

@users_bp.route("/")
@login_required
@role_required("admin")
def index():

    cur = g.db.cursor(DictCursor)

    cur.execute("SELECT * FROM usuarios")

    usuarios = cur.fetchall()

    return render_template(
        "users.html",
        usuarios=usuarios
    )


# ==============================
# CREAR USUARIO
# ==============================

@users_bp.route("/create", methods=["POST"])
@login_required
@role_required("admin")
def create():

    nombre = request.form["nombre"]
    email = request.form["email"]
    password = request.form["password"]

    cur = g.db.cursor(DictCursor)

    cur.execute(
        "SELECT id FROM usuarios WHERE email=%s",
        (email,)
    )

    existe = cur.fetchone()

    if existe:
        flash("⚠ El email ya está registrado")
        return redirect(url_for("users.index"))

    password_hash = generate_password_hash(password)

    cur = g.db.cursor()

    cur.execute("""
        INSERT INTO usuarios
        (nombre,email,password_hash,activo)
        VALUES (%s,%s,%s,1)
    """,(
        nombre,
        email,
        password_hash
    ))

    g.db.commit()

    flash("✔ Usuario creado correctamente")

    return redirect(url_for("users.index"))


# ==============================
# EDITAR USUARIO
# ==============================

@users_bp.route("/edit/<int:id>", methods=["POST"])
@login_required
@role_required("admin")
def edit(id):

    nombre = request.form["nombre"]
    email = request.form["email"]

    cur = g.db.cursor()

    cur.execute("""
        UPDATE usuarios
        SET nombre=%s,
            email=%s
        WHERE id=%s
    """,(
        nombre,
        email,
        id
    ))

    g.db.commit()

    flash("✔ Usuario actualizado correctamente")

    return redirect(url_for("users.index"))


# ==============================
# ELIMINAR USUARIO
# ==============================

@users_bp.route("/delete/<int:id>")
@login_required
@role_required("admin")
def delete(id):

    cur = g.db.cursor()

    cur.execute(
        "DELETE FROM usuarios WHERE id=%s",
        (id,)
    )

    g.db.commit()

    flash("✔ Usuario eliminado")

    return redirect(url_for("users.index"))