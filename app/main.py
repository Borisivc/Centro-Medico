from flask import Blueprint, render_template, session, redirect, url_for, g, request, flash, jsonify
from datetime import datetime
from werkzeug.security import check_password_hash

main_bp = Blueprint('main', __name__)

# ==========================================
# 1. ACCESO PÚBLICO E INDEX
# ==========================================
@main_bp.route('/')
def index():
    cur = g.db.cursor()
    especialidades = []
    profesionales = []
    try:
        cur.execute("SELECT id, nombre FROM especialidades ORDER BY nombre ASC")
        especialidades = cur.fetchall()
        
        cur.execute("""
            SELECT p.id, p.nombre, p.apellido, pe.especialidad_id 
            FROM profesionales p
            JOIN profesionales_especialidades pe ON p.id = pe.profesional_id
            WHERE p.activo = 1 
            ORDER BY p.nombre ASC
        """)
        profesionales = cur.fetchall()
    except Exception as e:
        print(f"Error cargando index: {e}")
    finally:
        cur.close()
    return render_template('index.html', especialidades=especialidades, profesionales=profesionales)

# ==========================================
# 2. AUTENTICACIÓN (LOGIN / LOGOUT)
# ==========================================
@main_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    cur = g.db.cursor()
    try:
        cur.execute("SELECT id, nombre, password_hash FROM usuarios WHERE email = %s", (email,))
        user = cur.fetchone()
        
        u_id = user.get('id') if isinstance(user, dict) else user[0] if user else None
        u_nom = user.get('nombre') if isinstance(user, dict) else user[1] if user else None
        u_hash = user.get('password_hash') if isinstance(user, dict) else user[2] if user else None

        if user and check_password_hash(u_hash, password):
            session['user_id'] = u_id
            session['user_nombre'] = u_nom
            return redirect(url_for('main.dashboard'))
    except Exception as e:
        print(f"Error Login: {e}")
    finally:
        cur.close()
    
    flash("Credenciales incorrectas.", "danger")
    return redirect(url_for('main.index'))

@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))

# ==========================================
# 3. APIS DE VALIDACIÓN EN TIEMPO REAL
# ==========================================
@main_bp.route('/api/validar_rut/<rut>', methods=['GET'])
def api_validar_rut(rut):
    cur = g.db.cursor()
    try:
        rut_l = rut.replace('.', '').replace('-', '').upper()
        cur.execute("SELECT nombre, apellido FROM pacientes WHERE rut = %s", (rut_l,))
        p = cur.fetchone()
        if p:
            return jsonify({
                "existe": True,
                "nombre": p.get('nombre') if isinstance(p, dict) else p[0],
                "apellido": p.get('apellido') if isinstance(p, dict) else p[1]
            })
        return jsonify({"existe": False})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()

@main_bp.route('/api/validar_rut_profesional/<rut>', methods=['GET'])
def api_validar_rut_prof(rut):
    cur = g.db.cursor()
    try:
        rut_l = rut.replace('.', '').replace('-', '').upper()
        cur.execute("SELECT id FROM profesionales WHERE rut = %s", (rut_l,))
        p = cur.fetchone()
        if p:
            return jsonify({"existe": True})
        return jsonify({"existe": False})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()

# ==========================================
# 4. AGENDAMIENTO PÚBLICO Y DASHBOARD
# ==========================================
@main_bp.route('/agendar_publico', methods=['POST'])
def agendar_publico():
    rut = request.form.get('rut').replace('.', '').replace('-', '').upper()
    nom = request.form.get('nombre').upper()
    ape = request.form.get('apellido').upper()
    prof_id = request.form.get('profesional_id')
    fec = request.form.get('fecha')
    hor = request.form.get('hora')
    
    cur = g.db.cursor()
    try:
        cur.execute("SELECT id FROM pacientes WHERE rut = %s", (rut,))
        res = cur.fetchone()
        paciente_id = (res.get('id') if isinstance(res, dict) else res[0]) if res else None
        
        if not paciente_id:
            cur.execute("INSERT INTO pacientes (rut, nombre, apellido, email, telefono) VALUES (%s, %s, %s, '', '')", (rut, nom, ape))
            cur.execute("SELECT LAST_INSERT_ID()")
            last = cur.fetchone()
            paciente_id = last.get('LAST_INSERT_ID()') if isinstance(last, dict) else last[0]

        cur.execute("""
            INSERT INTO agenda (paciente_id, profesional_id, fecha, hora, estado_id, observacion) 
            VALUES (%s, %s, %s, %s, 1, 'SOLICITUD WEB')
        """, (paciente_id, prof_id, fec, hor))
        g.db.commit()
        flash('Cita agendada exitosamente.', 'success')
    except Exception as e:
        if hasattr(g, 'db'): g.db.rollback()
        flash(f'Error al agendar: {e}', 'danger')
    finally:
        cur.close()
    return redirect(url_for('main.index'))

@main_bp.route('/dashboard')
def dashboard():
    if not session.get('user_id'): return redirect(url_for('main.index'))
    hoy_dt = datetime.now()
    cur = g.db.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM agenda WHERE fecha = CURDATE()")
        res_c = cur.fetchone()
        c_hoy = list(res_c.values())[0] if isinstance(res_c, dict) else res_c[0]
        
        cur.execute("SELECT COUNT(*) FROM pacientes")
        res_p = cur.fetchone()
        p_count = list(res_p.values())[0] if isinstance(res_p, dict) else res_p[0]
        
        cur.execute("SELECT COUNT(*) FROM profesionales")
        res_m = cur.fetchone()
        m_count = list(res_m.values())[0] if isinstance(res_m, dict) else res_m[0]

        # 1. Citas de HOY
        cur.execute("""
            SELECT TIME_FORMAT(a.hora, '%H:%i') as hora, CONCAT(p.nombre, ' ', p.apellido) as paciente, 
                   pr.nombre as profesional, e.nombre as estado
            FROM agenda a
            JOIN pacientes p ON a.paciente_id = p.id
            JOIN profesionales pr ON a.profesional_id = pr.id
            JOIN estados_agenda e ON a.estado_id = e.id
            WHERE a.fecha = CURDATE() ORDER BY a.hora ASC
        """)
        citas_dia = cur.fetchall()

        # 2. INYECCIÓN DE PRECISIÓN: Citas de los PRÓXIMOS 7 DÍAS
        cur.execute("""
            SELECT DATE_FORMAT(a.fecha, '%d-%m-%Y') as fecha, 
                   TIME_FORMAT(a.hora, '%H:%i') as hora,
                   p.apellido as apellido, 
                   pr.nombre as prof
            FROM agenda a
            JOIN pacientes p ON a.paciente_id = p.id
            JOIN profesionales pr ON a.profesional_id = pr.id
            WHERE a.fecha > CURDATE() AND a.fecha <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
            ORDER BY a.fecha ASC, a.hora ASC
            LIMIT 5
        """)
        rows_proximas = cur.fetchall()
        
        # Mapeo robusto anti-diccionarios/tuplas
        proximas_citas = []
        for r in rows_proximas:
            if isinstance(r, dict):
                proximas_citas.append(r)
            else:
                proximas_citas.append({
                    'fecha': r[0], 'hora': r[1], 'apellido': r[2], 'prof': r[3]
                })

        return render_template('dashboard.html', 
                               hoy=hoy_dt.strftime('%d-%m-%Y'), 
                               c_hoy=c_hoy, 
                               p_count=p_count, 
                               m_count=m_count, 
                               citas_dia=citas_dia,
                               proximas_citas=proximas_citas) # Variable enviada al HTML
    except Exception as e:
        print(f"Error Dashboard: {e}")
        return render_template('dashboard.html', hoy=hoy_dt.strftime('%d-%m-%Y'), c_hoy=0, p_count=0, m_count=0, citas_dia=[], proximas_citas=[])
    finally:
        cur.close()