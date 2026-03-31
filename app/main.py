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
        cur.execute("SELECT id, nombre, password_hash FROM usuarios WHERE email = %s AND activo = 1", (email,))
        user = cur.fetchone()
        
        u_id = user.get('id') if isinstance(user, dict) else user[0] if user else None
        u_nom = user.get('nombre') if isinstance(user, dict) else user[1] if user else None
        u_hash = user.get('password_hash') if isinstance(user, dict) else user[2] if user else None

        if user and check_password_hash(u_hash, password):
            session.clear()
            session['user_id'] = u_id
            session['user_nombre'] = u_nom
            return redirect(url_for('main.dashboard'))
    except Exception as e:
        print(f"Error Login: {e}")
    finally:
        cur.close()
    
    flash("Credenciales incorrectas o usuario inactivo.", "danger")
    return redirect(url_for('main.index'))

@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))

# ==========================================
# 3. APIS DE VALIDACIÓN Y DISPONIBILIDAD (Públicas para el agendamiento)
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

def parse_time_to_mins(t_obj):
    if isinstance(t_obj, str):
        parts = t_obj.split(':')
        return int(parts[0]) * 60 + int(parts[1])
    elif hasattr(t_obj, 'total_seconds'):
        return int(t_obj.total_seconds() // 60)
    elif hasattr(t_obj, 'seconds'):
        return int(t_obj.seconds // 60)
    return 0

@main_bp.route('/api/horarios_disponibles', methods=['GET'])
def api_horarios_disponibles():
    prof_id = request.args.get('profesional_id')
    fecha_str = request.args.get('fecha')
    is_public = request.args.get('publico', 'false') == 'true'

    if not prof_id or not fecha_str:
        return jsonify([])

    try:
        fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except Exception:
        return jsonify([])

    dia_semana = fecha_dt.weekday()
    cur = g.db.cursor()

    try:
        cur.execute("""
            SELECT hora_inicio, hora_fin, tipo 
            FROM disponibilidad_profesional 
            WHERE profesional_id = %s 
              AND dia_semana = %s 
              AND fecha_inicio <= %s 
              AND fecha_fin >= %s
        """, (prof_id, dia_semana, fecha_str, fecha_str))
        disponibilidades = cur.fetchall()

        if not disponibilidades:
            return jsonify([])

        cur.execute("""
            SELECT TIME_FORMAT(hora, '%%H:%%i') as hora, observacion 
            FROM agenda 
            WHERE profesional_id = %s AND fecha = %s
        """, (prof_id, fecha_str))
        citas_db = cur.fetchall()
        
        citas_tomadas = set()
        for c in citas_db:
            h_str = c['hora'] if isinstance(c, dict) else c[0]
            if not h_str:
                continue
            obs = (c['observacion'] if isinstance(c, dict) else c[1]) or ""
            citas_tomadas.add(h_str)
            if 'SOLICITUD WEB' in obs.upper() and h_str.endswith(':00'):
                h_base = int(h_str.split(':')[0])
                citas_tomadas.add(f"{h_base:02d}:15")
                citas_tomadas.add(f"{h_base:02d}:30")

        slots_validos = set()

        for d in disponibilidades:
            tipo = int(d['tipo'] if isinstance(d, dict) else d[2])
            if tipo == 0:
                hi = parse_time_to_mins(d['hora_inicio'] if isinstance(d, dict) else d[0])
                hf = parse_time_to_mins(d['hora_fin'] if isinstance(d, dict) else d[1])
                for m in range(hi, hf, 15):
                    slots_validos.add(f"{m//60:02d}:{m%60:02d}")
                    
        for d in disponibilidades:
            tipo = int(d['tipo'] if isinstance(d, dict) else d[2])
            if tipo == 1:
                hi = parse_time_to_mins(d['hora_inicio'] if isinstance(d, dict) else d[0])
                hf = parse_time_to_mins(d['hora_fin'] if isinstance(d, dict) else d[1])
                for m in range(hi, hf, 15):
                    bloq_str = f"{m//60:02d}:{m%60:02d}"
                    if bloq_str in slots_validos:
                        slots_validos.remove(bloq_str)

        slots_finales = []
        for slot in sorted(list(slots_validos)):
            if slot in citas_tomadas:
                continue
            if is_public:
                if slot.endswith(':00'):
                    h = int(slot.split(':')[0])
                    s1, s2, s3 = f"{h:02d}:15", f"{h:02d}:30", f"{h:02d}:45"
                    if s1 in slots_validos and s2 in slots_validos and s3 in slots_validos:
                        if s1 not in citas_tomadas and s2 not in citas_tomadas and s3 not in citas_tomadas:
                            slots_finales.append(slot)
            else:
                slots_finales.append(slot)

        return jsonify(slots_finales)
    except Exception as e:
        print(f"Error API Horarios: {e}")
        return jsonify([])
    finally:
        cur.close()

@main_bp.route('/agendar_publico', methods=['POST'])
def agendar_publico():
    rut = request.form.get('rut').replace('.', '').replace('-', '').upper()
    nom = request.form.get('nombre').upper()
    ape = request.form.get('apellido').upper()
    prof_id = request.form.get('profesional_id')
    fec = request.form.get('fecha')
    hor = request.form.get('hora')
    
    if not hor:
        flash('Error: No se seleccionó una hora válida. Por favor, intente nuevamente.', 'danger')
        return redirect(url_for('main.index'))
    
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

# ==========================================
# 4. DASHBOARD (CANDADO DE SEGURIDAD PRIVADO)
# ==========================================
@main_bp.route('/dashboard')
def dashboard():
    # CANDADO: Solo usuarios logueados pueden ver el Dashboard
    if 'user_id' not in session: 
        flash('Acceso denegado: Por favor, inicie sesión para ver el panel.', 'danger')
        return redirect(url_for('main.index'))
        
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
                               proximas_citas=proximas_citas)
    except Exception as e:
        print(f"Error Dashboard: {e}")
        return render_template('dashboard.html', hoy=hoy_dt.strftime('%d-%m-%Y'), c_hoy=0, p_count=0, m_count=0, citas_dia=[], proximas_citas=[])
    finally:
        cur.close()