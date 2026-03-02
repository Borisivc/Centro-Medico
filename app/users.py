from flask import Blueprint, render_template, request, redirect, url_for, g, session, flash
from functools import wraps
from werkzeug.security import generate_password_hash
import MySQLdb

users_bp = Blueprint("users", __name__, url_prefix="/users")


# ==================================
# DECORADOR LOGIN REQUIRED
# ==================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not session.get("user_id"):
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)

    return decorated_function


# ==================================
# LISTAR USUARIOS
# ==================================
@users_bp.route("/")
@login_required
def index():

    cur = g.db.cursor()

    cur.execute("""
        SELECT id, nombre, email
        FROM usuarios
        ORDER BY id DESC
    """)

    usuarios = cur.fetchall()

    return render_template("users/index.html", usuarios=usuarios)


# ==================================
# CREAR USUARIO
# ==================================
@users_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():

    if request.method == "POST":

        nombre = request.form["nombre"]
        email = request.form["email"]
        password = request.form["password"]

        password_hash = generate_password_hash(password)

        cur = g.db.cursor()

        try:
            cur.execute("""
                INSERT INTO usuarios (nombre, email, password_hash)
                VALUES (%s, %s, %s)
            """, (nombre, email, password_hash))

            g.db.commit()

            flash("✅ Usuario creado correctamente")
            return redirect(url_for("users.index"))

        except MySQLdb.IntegrityError:
            g.db.rollback()
            flash("⚠️ El email ya existe")
            return redirect(url_for("users.create"))

        except Exception as e:
            g.db.rollback()
            print("ERROR CREAR USUARIO:", e)
            flash("⚠️ Error inesperado al crear usuario")
            return redirect(url_for("users.index"))

    return render_template("users/create.html")


# ==================================
# EDITAR USUARIO
# ==================================
@users_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):

    cur = g.db.cursor()

    # Verificar que exista
    cur.execute("SELECT id, nombre, email FROM usuarios WHERE id=%s", (id,))
    usuario = cur.fetchone()

    if not usuario:
        flash("⚠️ Usuario no encontrado")
        return redirect(url_for("users.index"))

    if request.method == "POST":

        nombre = request.form["nombre"]
        email = request.form["email"]

        try:
            cur.execute("""
                UPDATE usuarios
                SET nombre=%s, email=%s
                WHERE id=%s
            """, (nombre, email, id))

            g.db.commit()

            flash("✏ Usuario actualizado correctamente")
            return redirect(url_for("users.index"))

        except Exception as e:
            g.db.rollback()
            print("ERROR EDITAR:", e)
            flash("⚠️ Error al actualizar usuario")
            return redirect(url_for("users.index"))

    return render_template("users/edit.html", usuario=usuario)


# ==================================
# ELIMINAR USUARIO
# ==================================
@users_bp.route("/delete/<int:id>")
@login_required
def delete(id):

    cur = g.db.cursor()

    try:

        # Verificar existencia
        cur.execute("SELECT id FROM usuarios WHERE id=%s", (id,))
        usuario = cur.fetchone()

        if not usuario:
            flash("⚠️ Usuario no existe")
            return redirect(url_for("users.index"))

        # Eliminar relaciones si tabla existe
        try:
            cur.execute("DELETE FROM usuario_roles WHERE usuario_id=%s", (id,))
        except:
            pass  # si no existe tabla o no hay registros, continuar

        # Eliminar usuario
        cur.execute("DELETE FROM usuarios WHERE id=%s", (id,))

        g.db.commit()

        flash("🗑 Usuario eliminado correctamente")

    except Exception as e:
        g.db.rollback()
        print("ERROR ELIMINAR:", e)
        flash("⚠️ No se pudo eliminar el usuario")

    return redirect(url_for("users.index"))