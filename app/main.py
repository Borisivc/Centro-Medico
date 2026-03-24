from flask import Blueprint, render_template, session, redirect, url_for, g, request, flash
from datetime import datetime
from werkzeug.security import check_password_hash

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    cur = g.db.cursor()
    try:
        cur.execute("SELECT id, nombre, password_hash FROM usuarios WHERE email = %s AND activo = 1", (email,))
        user = cur.fetchone()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_nombre'] = user['nombre']
            return redirect(url_for('main.dashboard'))
    finally:
        cur.close()
    flash("Acceso denegado", "danger")
    return redirect(url_for('main.index'))

@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))

@main_bp.route('/dashboard')
def dashboard():
    if not session.get('user_id'):
        return redirect(url_for('main.index'))
    
    hoy = datetime.now().strftime('%Y-%m-%d')
    cur = g.db.cursor()
    try:
        cur.execute("SELECT COUNT(*) as total FROM pacientes")
        p = cur.fetchone()['total']
        cur.execute("SELECT COUNT(*) as total FROM profesionales WHERE activo = 1")
        m = cur.fetchone()['total']
    except:
        p = m = 0
    finally:
        cur.close()
        
    return render_template('dashboard.html', hoy=hoy, pacientes=p, profesionales=m, citas_dia=[])