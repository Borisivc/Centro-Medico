from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, g, session

agenda_bp = Blueprint('agenda', __name__)

@agenda_bp.route('/agenda')
def index():
    if not session.get('user_id'):
        return redirect(url_for('main.index'))
        
    cur = g.db.cursor()
    
    cur.execute("""
        SELECT a.id, a.fecha, a.hora, 
               p.id as pac_id, p.nombre as pac_nom, p.apellido as pac_ape, p.rut as pac_rut,
               pr.id as prof_id, pr.nombre as prof_nom, pr.apellido as prof_ape,
               e.nombre as estado
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
        cur.execute("SELECT id, nombre, apellido FROM pacientes WHERE rut = %s", (rut,))
        paciente = cur.fetchone()
        
        if paciente:
            return jsonify({"existe": True, "nombre": paciente['nombre'], "apellido": paciente['apellido']})
        return jsonify({"existe": False})
    except Exception as e:
        return jsonify({"existe": False, "error": str(e)})
    finally:
        cur.close()

@agenda_bp.route('/agenda/save', methods=['POST'])
def save():
    cur = g.db.cursor()
    try:
        ag_id = request.form.get('ag_id')
        paciente_id = request.form.get('paciente_id')
        profesional_id = request.form.get('profesional_id')
        fecha_str = request.form.get('fecha')
        hora_str = request.form.get('hora')
        estado_id = request.form.get('estado_id') or 1 

        rut = request.form.get('rut')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')

        if not paciente_id and rut:
            cur.execute("SELECT id FROM pacientes WHERE rut = %s", (rut,))
            pac = cur.fetchone()
            if not pac:
                cur.execute("INSERT INTO pacientes (rut, nombre, apellido, activo) VALUES (%s, %s, %s, 1)", (rut, nombre, apellido))
                paciente_id = cur.lastrowid
            else:
                paciente_id = pac['id']

        if ag_id:
            cur.execute("""
                UPDATE agenda 
                SET paciente_id=%s, profesional_id=%s, fecha=%s, hora=%s, estado_id=%s
                WHERE id=%s
            """, (paciente_id, profesional_id, fecha_str, hora_str, estado_id, ag_id))
            flash('Cita actualizada exitosamente.', 'success')
        else:
            cur.execute("""
                INSERT INTO agenda (paciente_id, profesional_id, fecha, hora, estado_id) 
                VALUES (%s, %s, %s, %s, %s)
            """, (paciente_id, profesional_id, fecha_str, hora_str, estado_id))
            flash('Cita agendada con éxito.', 'success')
            
        g.db.commit()
    except Exception as e:
        g.db.rollback()
        print(f"Error al guardar: {e}")
        flash('Ocurrió un error al guardar los datos.', 'danger')
    finally:
        cur.close()

    if session.get('user_id'):
        return redirect(url_for('agenda.index'))
    return redirect(url_for('main.index'))

# NUEVA RUTA DE ELIMINACIÓN
@agenda_bp.route('/agenda/delete/<int:id>', methods=['POST'])
def delete(id):
    cur = g.db.cursor()
    try:
        cur.execute("DELETE FROM agenda WHERE id = %s", (id,))
        g.db.commit()
        return jsonify({'status': 'success', 'message': 'Cita eliminada correctamente.'})
    except Exception as e:
        g.db.rollback()
        return jsonify({'status': 'error', 'message': 'No se pudo eliminar la cita.'})
    finally:
        cur.close()