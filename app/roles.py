from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g

roles_bp = Blueprint("roles", __name__, url_prefix="/roles")


@roles_bp.route("/")
def index():

    cur = g.db.cursor()

    cur.execute("SELECT id,nombre FROM roles")

    roles = cur.fetchall()

    return render_template("roles/index.html", roles=roles)


@roles_bp.route("/create", methods=["GET","POST"])
def create():

    if request.method == "POST":

        nombre = request.form["nombre"]

        cur = g.db.cursor()

        cur.execute("INSERT INTO roles (nombre) VALUES (%s)",(nombre,))

        g.db.commit()

        return redirect(url_for("roles.index"))

    return render_template("roles/create.html")