from flask import Blueprint, render_template, request, flash
from werkzeug.security import check_password_hash
from .extensions import mysql

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT password_hash FROM usuarios WHERE email = %s",
            (email,)
        )
        user = cur.fetchone()

        if user and check_password_hash(user[0], password):
            return "Login correcto ✅"
        else:
            flash("Credenciales incorrectas")

    return render_template("login.html")