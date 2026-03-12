from flask import Blueprint, request, redirect, url_for, session, g, flash
from werkzeug.security import check_password_hash
from MySQLdb.cursors import DictCursor

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


# ======================================
# LOGIN
# ======================================

@auth_bp.route("/login", methods=["POST"])
def login():

    email = request.form["email"].strip().lower()
    password = request.form["password"]

    cur = g.db.cursor(DictCursor)

    cur.execute("""
        SELECT id,nombre,email,password_hash
        FROM usuarios
        WHERE email=%s AND activo=1
    """, (email,))

    usuario = cur.fetchone()

    if usuario and check_password_hash(usuario["password_hash"], password):

        session.clear()

        session["user_id"] = usuario["id"]
        session["nombre"] = usuario["nombre"]

        cur.execute("""
            SELECT r.nombre
            FROM roles r
            JOIN usuarios_roles ur
            ON ur.rol_id = r.id
            WHERE ur.usuario_id=%s
        """, (usuario["id"],))

        roles = [r["nombre"].upper() for r in cur.fetchall()]

        session["roles"] = roles

        return redirect(url_for("main.dashboard"))

    flash(
        "Usuario o contraseña incorrectos. Si su cuenta está bloqueada contacte al administrador.",
        "login_error"
    )

    return redirect(url_for("main.dashboard"))


# ======================================
# LOGOUT
# ======================================

@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("main.dashboard"))