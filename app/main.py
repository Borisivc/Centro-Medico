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
        cur.execute("SELECT id, nombre, password_hash FROM usuarios WHERE email = %s", (email,))
        user = cur.fetchone()
        
        u_id = user['id'] if isinstance(user, dict) else user[0] if user else None
        u_nom = user['nombre'] if isinstance(user, dict) else user[1] if user else None
        u_hash = user['password_hash'] if isinstance(user, dict) else user[2] if user else None

        if user and check_password_hash(u_hash, password):
            session['user_id'] = u_id
            session['user_nombre'] = u_nom
            return redirect(url_for('main.dashboard'))
    except Exception as e:
        print(f"Error Login: {e}")
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
    
    hoy_display = datetime.now().strftime('%d-%m-%Y') 
    cur = g.db.cursor()
    
    try:
        # 1. Indicadores (Hoy, Pacientes, Médicos)
        cur.execute("SELECT COUNT(*) as total FROM agenda WHERE fecha = CURDATE()")
        res_h = cur.fetchone()
        c_hoy = (res_h['total'] if isinstance(res_h, dict) else res_h[0]) if res_h else 0

        cur.execute("SELECT COUNT(*) as total FROM pacientes")
        res_p = cur.fetchone()
        p_count = (res_p['total'] if isinstance(res_p, dict) else res_p[0]) if res_p else 0

        cur.execute("SELECT COUNT(*) as total FROM profesionales")
        res_m = cur.fetchone()
        m_count = (res_m['total'] if isinstance(res_m, dict) else res_m[0]) if res_m else 0

        # 2. Citas del Día (Detallado)
        query_hoy = """
            SELECT a.hora, CONCAT(p.nombre, ' ', p.apellido) as paciente, 
                   pr.nombre as profesional, e.nombre as estado
            FROM agenda a
            JOIN pacientes p ON a.paciente_id = p.id
            JOIN profesionales pr ON a.profesional_id = pr.id
            JOIN estados_agenda e ON a.estado_id = e.id
            WHERE a.fecha = CURDATE()
            ORDER BY a.hora ASC
        """
        cur.execute(query_hoy)
        rows_hoy = cur.fetchall()
        citas_dia = []
        for r in rows_hoy:
            if isinstance(r, dict):
                citas_dia.append(r)
            else:
                citas_dia.append({'hora': r[0], 'paciente': r[1], 'profesional': r[2], 'estado': r[3]})

        # 3. Vista Previa Semanal (Resumida - Próximas 6 citas excluyendo hoy)
        query_semana = """
            SELECT a.fecha, a.hora, p.apellido, pr.nombre as prof
            FROM agenda a
            JOIN pacientes p ON a.paciente_id = p.id
            JOIN profesionales pr ON a.profesional_id = pr.id
            WHERE a.fecha > CURDATE() AND a.fecha <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
            ORDER BY a.fecha ASC, a.hora ASC
            LIMIT 6
        """
        cur.execute(query_semana)
        rows_sem = cur.fetchall()
        proximas_citas = []
        for r in rows_sem:
            if isinstance(r, dict):
                proximas_citas.append(r)
            else:
                proximas_citas.append({'fecha': r[0], 'hora': r[1], 'apellido': r[2], 'prof': r[3]})

    except Exception as e:
        print(f"Error Dashboard: {e}")
        c_hoy = p_count = m_count = 0
        citas_dia = []
        proximas_citas = []
    finally:
        cur.close()
        
    return render_template('dashboard.html', 
                           hoy=hoy_display, 
                           c_hoy=c_hoy, 
                           p_count=p_count, 
                           m_count=m_count,
                           citas_dia=citas_dia,
                           proximas_citas=proximas_citas)