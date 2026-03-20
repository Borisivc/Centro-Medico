from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    if not session.get('user_id'):
        return redirect(url_for('main.index'))

    cur = g.db.cursor()
    
    # KPIs
    cur.execute("SELECT COUNT(*) as total FROM pacientes")
    tp = cur.fetchone()['total']
    cur.execute("SELECT COUNT(*) as total FROM profesionales")
    tpro = cur.fetchone()['total']
    cur.execute("SELECT COUNT(*) as total FROM agenda")
    tc = cur.fetchone()['total']
    
    # Citas de Hoy
    hoy_dt = datetime.now()
    hoy_str = hoy_dt.strftime('%Y-%m-%d')
    cur.execute("""
        SELECT a.hora, p.nombre as paciente, pr.nombre as profesional
        FROM agenda a
        JOIN pacientes p ON a.paciente_id = p.id
        JOIN profesionales pr ON a.profesional_id = pr.id
        WHERE a.fecha = %s
        ORDER BY a.hora ASC
    """, (hoy_str,))
    citas_hoy = cur.fetchall()

    # Citas de la Semana (Lunes a Domingo)
    lunes = hoy_dt - timedelta(days=hoy_dt.weekday())
    domingo = lunes + timedelta(days=6)
    cur.execute("""
        SELECT a.fecha, a.hora, p.nombre as paciente, pr.nombre as profesional
        FROM agenda a
        JOIN pacientes p ON a.paciente_id = p.id
        JOIN profesionales pr ON a.profesional_id = pr.id
        WHERE a.fecha BETWEEN %s AND %s
        ORDER BY a.fecha ASC, a.hora ASC
    """, (lunes.strftime('%Y-%m-%d'), domingo.strftime('%Y-%m-%d')))
    citas_semana = cur.fetchall()
    
    cur.close()

    return render_template('dashboard.html', 
                           tp=tp, tpro=tpro, tc=tc, 
                           citas_hoy=citas_hoy, 
                           citas_semana=citas_semana,
                           now=hoy_dt)

@main_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('email', '').lower().strip()
    password = request.form.get('password')
    cur = g.db.cursor()
    cur.execute("SELECT id, nombre, password_hash FROM usuarios WHERE email = %s AND activo = 1", (email,))
    user = cur.fetchone()
    cur.close()

    if user and check_password_hash(user['password_hash'], password):
        session.clear()
        session['user_id'] = user['id']
        session['user_nombre'] = user['nombre']
        return redirect(url_for('main.dashboard'))
    
    flash('Credenciales incorrectas', 'danger')
    return redirect(url_for('main.index'))

@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))