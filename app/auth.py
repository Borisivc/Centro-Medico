from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import check_password_hash

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        cur = g.db.cursor()

        cur.execute(
            """
            SELECT id, nombre, password_hash
            FROM usuarios
            WHERE email = %s
            """,
            (email,)
        )

        user = cur.fetchone()

        if user and check_password_hash(user[2], password):

            session["user_id"] = user[0]
            session["user_name"] = user[1]

            return redirect(url_for("routes.dashboard"))

        else:
            flash("Credenciales incorrectas")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("auth.login"))