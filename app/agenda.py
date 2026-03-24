from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g

agenda_bp = Blueprint('agenda', __name__)

@agenda_bp.route('/')
def index():
    cur = g.db.cursor()
    
    # 1. Obtener Citas con JOINs (Usando nombres exactos de tu tabla: observacion)
    query = """
        SELECT a.id, a.fecha, a.hora, a.observacion,
               p.nombre as pac_nom, p.apellido as pac_ape, p.rut as pac_rut,
               pr.nombre as prof_nom, pr.apellido as prof_ape,
               e.nombre as estado_nom, a.estado_id, a.paciente_id, a.profesional_id
        FROM agenda a
        JOIN pacientes p ON a.paciente_id = p.id
        JOIN profesionales pr ON a.profesional_id = pr.id
        JOIN estados_agenda e ON a.estado_id = e.id
        ORDER BY a.fecha DESC, a.hora DESC
    """
    cur.execute(query)
    rows = cur.fetchall()
    
    citas = []
    for r in rows:
        # Mapeo robusto para evitar errores de índice o diccionario
        d = r if isinstance(r, dict) else {
            'id': r[0], 'fecha': r[1], 'hora': r[2], 'observacion': r[3],
            'pac_nom': r[4], 'pac_ape': r[5], 'pac_rut': r[6],
            'prof_nom': r[7], 'prof_ape': r[8],
            'estado_nom': r[9], 'estado_id': r[10], 'paciente_id': r[11], 'profesional_id': r[12]
        }
        citas.append(d)

    # 2. Datos para los selectores del Modal
    cur.execute("SELECT id, nombre, apellido, rut FROM pacientes ORDER BY nombre ASC")
    pacientes = cur.fetchall()
    
    cur.execute("SELECT id, nombre, apellido FROM profesionales ORDER BY nombre ASC")
    profesionales = cur.fetchall()
    
    cur.execute("SELECT id, nombre FROM estados_agenda ORDER BY nombre ASC")
    estados = cur.fetchall()

    cur.close()
    return render_template('agenda.html', citas=citas, pacientes=pacientes, profesionales=profesionales, estados=estados)

@agenda_bp.route('/save', methods=['POST'])
def save():
    cita_id = request.form.get('id')
    paciente_id = request.form.get('paciente_id')
    profesional_id = request.form.get('profesional_id')
    fecha = request.form.get('fecha')
    hora = request.form.get('hora')
    estado_id = request.form.get('estado_id')
    observacion = request.form.get('observacion', '').strip().upper()

    cur = g.db.cursor()
    try:
        if cita_id:  # UPDATE
            cur.execute("""
                UPDATE agenda 
                SET paciente_id=%s, profesional_id=%s, fecha=%s, hora=%s, estado_id=%s, observacion=%s
                WHERE id=%s
            """, (paciente_id, profesional_id, fecha, hora, estado_id, observacion, cita_id))
            flash('Cita actualizada correctamente.', 'success')
        else:  # INSERT
            cur.execute("""
                INSERT INTO agenda (paciente_id, profesional_id, fecha, hora, estado_id, observacion)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (paciente_id, profesional_id, fecha, hora, estado_id, observacion))
            flash('Nueva cita agendada con éxito.', 'success')
        
        g.db.commit()
    except Exception as e:
        if hasattr(g, 'db'): g.db.rollback()
        flash(f'Error en la agenda: {str(e)}', 'danger')
    finally:
        cur.close()
    return redirect(url_for('agenda.index'))

@agenda_bp.route('/delete/<int:id>')
def delete(id):
    cur = g.db.cursor()
    try:
        cur.execute("DELETE FROM agenda WHERE id = %s", (id,))
        g.db.commit()
        flash('Cita eliminada de la agenda.', 'success')
    except Exception as e:
        if hasattr(g, 'db'): g.db.rollback()
        flash(f'No se pudo eliminar la cita: {str(e)}', 'danger')
    finally:
        cur.close()
    return redirect(url_for('agenda.index'))