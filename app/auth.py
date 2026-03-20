from flask import Blueprint, request, redirect, url_for, session, flash, g
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    cur = g.db.cursor()
    cur.execute("SELECT id, nombre, password_hash FROM usuarios WHERE email = %s AND activo = 1", (email,))
    user = cur.fetchone()
    cur.close()

    if user and check_password_hash(user['password_hash'], password):
        session.clear()
        session['user_id'] = user['id']
        session['user_nom'] = user['nombre']
        return redirect(url_for('main.dashboard'))
    else:
        flash("Credenciales incorrectas.", "danger")
        return redirect(url_for('main.index'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))