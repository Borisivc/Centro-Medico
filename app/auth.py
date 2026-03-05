from flask import Blueprint, render_template, request, redirect, url_for, session, g, flash
from werkzeug.security import check_password_hash
from MySQLdb.cursors import DictCursor

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        cur = g.db.cursor(DictCursor)

        cur.execute("""
            SELECT id, nombre, email, password_hash
            FROM usuarios
            WHERE email=%s AND activo=1
        """,(email,))

        usuario = cur.fetchone()

        if usuario:

            if check_password_hash(usuario["password_hash"], password):

                session["user_id"] = usuario["id"]
                session["nombre"] = usuario["nombre"]

                cur.execute("""
                    SELECT r.nombre
                    FROM roles r
                    JOIN usuarios_roles ur
                    ON ur.rol_id = r.id
                    WHERE ur.usuario_id=%s
                """,(usuario["id"],))

                rol = cur.fetchone()

                if rol:
                    session["role"] = rol["nombre"]

                return redirect(url_for("main.dashboard"))

        flash("Usuario o contraseña incorrectos")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("main.dashboard"))