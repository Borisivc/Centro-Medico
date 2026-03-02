from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import check_password_hash

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        print("EMAIL INGRESADO:", email)

        cur = g.db.cursor()

        cur.execute("""
            SELECT id, nombre, email, password_hash
            FROM usuarios
            WHERE LOWER(TRIM(email)) = %s
        """,(email,))

        user = cur.fetchone()

        print("USUARIO DB:", user)

        if not user:
            flash("Usuario no encontrado")
            return render_template("auth/login.html")

        if not check_password_hash(user[3], password):
            flash("Contraseña incorrecta")
            return render_template("auth/login.html")

        session["user_id"] = user[0]
        session["user_name"] = user[1]

        return redirect(url_for("routes.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("auth.login"))