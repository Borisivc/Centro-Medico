from flask import Blueprint, render_template, request, redirect, url_for, flash, g, session
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password')

    if not email or not password:
        flash("Credenciales incompletas.", "warning")
        return redirect(url_for('main.index'))

    cur = g.db.cursor()
    try:
        cur.execute("SELECT id, nombre, password_hash, activo FROM usuarios WHERE email = %s", (email,))
        user = cur.fetchone()

        if user:
            if user['activo'] == 0:
                flash("Cuenta inactiva. Contacte al administrador.", "danger")
            elif check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['user_nom'] = user['nombre']
                return redirect(url_for('main.dashboard'))
            else:
                flash("Contraseña incorrecta.", "danger")
        else:
            flash("Usuario no registrado.", "danger")
    except Exception as e:
        flash(f"Error de conexión: {str(e)}", "danger")
    finally:
        cur.close()
    return redirect(url_for('main.index'))

@main_bp.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada.", "success")
    return redirect(url_for('main.index'))

@main_bp.route('/dashboard')
def dashboard():
    if not session.get('user_id'):
        return redirect(url_for('main.index'))
    
    cur = g.db.cursor()
    try:
        # 1. Contadores principales (tp, tpro, tc)
        cur.execute("SELECT COUNT(*) as total FROM pacientes")
        tp = cur.fetchone()['total']
        
        cur.execute("SELECT COUNT(*) as total FROM profesionales")
        tpro = cur.fetchone()['total']
        
        cur.execute("SELECT COUNT(*) as total FROM agenda")
        tc = cur.fetchone()['total']

        # 2. Citas de hoy (citas_hoy)
        cur.execute("""
            SELECT a.hora, CONCAT(p.nombre, ' ', p.apellido) as paciente, 
                   CONCAT(pr.nombre, ' ', pr.apellido) as profesional
            FROM agenda a
            JOIN pacientes p ON a.paciente_id = p.id
            JOIN profesionales pr ON a.profesional_id = pr.id
            WHERE a.fecha = CURDATE()
            ORDER BY a.hora ASC
        """)
        citas_hoy = cur.fetchall()

        # 3. Vista Semanal (citas_semana)
        cur.execute("""
            SELECT a.fecha, a.hora, CONCAT(p.nombre, ' ', p.apellido) as paciente
            FROM agenda a
            JOIN pacientes p ON a.paciente_id = p.id
            WHERE a.fecha BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
            ORDER BY a.fecha ASC, a.hora ASC
        """)
        citas_semana = cur.fetchall()

    except Exception as e:
        print(f"Error Dashboard: {e}")
        tp = tpro = tc = 0
        citas_hoy = citas_semana = []
    finally:
        cur.close()

    return render_template('dashboard.html', 
                           tp=tp, tpro=tpro, tc=tc, 
                           citas_hoy=citas_hoy, 
                           citas_semana=citas_semana, 
                           now=datetime.now())