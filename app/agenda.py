from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, g, session
from .utils import limpiar_rut, validar_rut

agenda_bp = Blueprint('agenda', __name__)

@agenda_bp.route('/')
def index():
    if not session.get('user_id'):
        return redirect(url_for('main.index'))
        
    cur = g.db.cursor()
    # Mantenemos tus consultas originales para no romper funcionalidad
    cur.execute("""
        SELECT a.id, a.fecha, a.hora, 
               p.id as pac_id, p.nombre as pac_nom, p.apellido as pac_ape, p.rut as pac_rut,
               pr.id as prof_id, pr.nombre as prof_nom, pr.apellido as prof_ape,
               e.nombre as estado, a.estado_id
        FROM agenda a
        JOIN pacientes p ON a.paciente_id = p.id
        JOIN profesionales pr ON a.profesional_id = pr.id
        JOIN estados_agenda e ON a.estado_id = e.id
        ORDER BY a.fecha ASC, a.hora ASC
    """)
    citas = cur.fetchall()
    
    cur.execute("SELECT id, nombre, apellido, rut FROM pacientes ORDER BY nombre ASC")
    pacientes = cur.fetchall()
    
    cur.execute("SELECT id, nombre, apellido FROM profesionales ORDER BY nombre ASC")
    profesionales = cur.fetchall()
    
    cur.execute("SELECT id, nombre FROM estados_agenda ORDER BY id ASC")
    estados = cur.fetchall()
    
    cur.close()
    return render_template('agenda.html', citas=citas, pacientes=pacientes, profesionales=profesionales, estados=estados)

@agenda_bp.route('/buscar_paciente/<string:rut>')
def buscar_paciente(rut):
    cur = g.db.cursor()
    try:
        rut_limpio = limpiar_rut(rut)
        cur.execute("SELECT id, nombre, apellido FROM pacientes WHERE rut = %s", (rut_limpio,))
        # Usamos fetchone y validamos si es tupla o dict según tu config de MySQL
        paciente = cur.fetchone()
        if paciente:
            # Intentamos acceder por nombre de columna si usas DictCursor, o por índice si no.
            try:
                return jsonify({"existe": True, "nombre": paciente['nombre'], "apellido": paciente['apellido']})
            except:
                return jsonify({"existe": True, "nombre": paciente[1], "apellido": paciente[2]})
        return jsonify({"existe": False})
    except Exception as e:
        return jsonify({"existe": False, "error": str(e)})
    finally:
        cur.close()

@agenda_bp.route('/save', methods=['POST'])
def save():
    cur = g.db.cursor()
    try:
        ag_id = request.form.get('ag_id')
        paciente_id = request.form.get('paciente_id')
        profesional_id = request.form.get('profesional_id')
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        estado_id = request.form.get('estado_id') or 1 

        rut = request.form.get('rut')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')

        # Usamos el limpiador antes de buscar/insertar
        rut_plano = limpiar_rut(rut)

        if not paciente_id and rut:
            cur.execute("SELECT id FROM pacientes WHERE rut = %s", (rut_plano,))
            pac = cur.fetchone()
            if not pac:
                cur.execute("INSERT INTO pacientes (rut, nombre, apellido, activo) VALUES (%s, %s, %s, 1)", 
                            (rut_plano, nombre, apellido))
                paciente_id = cur.lastrowid
            else:
                try: paciente_id = pac['id']
                except: paciente_id = pac[0]

        if ag_id and ag_id != "":
            cur.execute("""
                UPDATE agenda 
                SET paciente_id=%s, profesional_id=%s, fecha=%s, hora=%s, estado_id=%s
                WHERE id=%s
            """, (paciente_id, profesional_id, fecha, hora, estado_id, ag_id))
            flash('Cita actualizada exitosamente.', 'success')
        else:
            cur.execute("""
                INSERT INTO agenda (paciente_id, profesional_id, fecha, hora, estado_id) 
                VALUES (%s, %s, %s, %s, %s)
            """, (paciente_id, profesional_id, fecha, hora, estado_id))
            flash('Cita agendada con éxito.', 'success')
            
        g.db.commit()
    except Exception as e:
        g.db.rollback()
        flash(f'Error al guardar: {str(e)}', 'danger')
    finally:
        cur.close()

    return redirect(url_for('agenda.index'))