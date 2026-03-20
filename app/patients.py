from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, g, session

patients_bp = Blueprint('patients', __name__)

@patients_bp.route('/pacientes')
def index():
    if not session.get('user_id'):
        return redirect(url_for('main.index'))
    
    cur = g.db.cursor()
    cur.execute("SELECT id, rut, nombre, apellido, fecha_nacimiento FROM pacientes ORDER BY id DESC")
    pacs = cur.fetchall()
    cur.close()
    
    return render_template('patients.html', pacientes=pacs)

@patients_bp.route('/pacientes/verificar/<string:rut>')
def verificar_rut(rut):
    cur = g.db.cursor()
    try:
        cur.execute("SELECT id, nombre, apellido, fecha_nacimiento FROM pacientes WHERE rut = %s", (rut,))
        p = cur.fetchone()
        if p:
            return jsonify({
                "existe": True, 
                "nombre": p['nombre'], 
                "apellido": p['apellido'],
                "fecha": p['fecha_nacimiento'].strftime('%Y-%m-%d') if p['fecha_nacimiento'] else ''
            })
        return jsonify({"existe": False})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()

@patients_bp.route('/pacientes/save', methods=['POST'])
def save():
    pac_id = request.form.get('pac_id')
    rut = request.form.get('rut')
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    fecha_nac = request.form.get('fecha_nacimiento')
    
    # Si la fecha viene vacía del input date, la hacemos None para MySQL
    if not fecha_nac:
        fecha_nac = None

    cur = g.db.cursor()
    try:
        if pac_id:
            cur.execute("""
                UPDATE pacientes 
                SET rut=%s, nombre=%s, apellido=%s, fecha_nacimiento=%s 
                WHERE id=%s
            """, (rut, nombre, apellido, fecha_nac, pac_id))
            flash('Paciente actualizado correctamente.', 'success')
        else:
            cur.execute("""
                INSERT INTO pacientes (rut, nombre, apellido, fecha_nacimiento, activo) 
                VALUES (%s, %s, %s, %s, 1)
            """, (rut, nombre, apellido, fecha_nac))
            flash('Paciente registrado con éxito.', 'success')
            
        g.db.commit()
    except Exception as e:
        g.db.rollback()
        print(f"Error al guardar paciente: {e}")
        flash('Error al guardar los datos del paciente.', 'danger')
    finally:
        cur.close()
        
    return redirect(url_for('patients.index'))

@patients_bp.route('/pacientes/delete/<int:id>', methods=['POST'])
def delete(id):
    cur = g.db.cursor()
    try:
        cur.execute("DELETE FROM pacientes WHERE id = %s", (id,))
        g.db.commit()
        return jsonify({'status': 'success', 'message': 'Paciente eliminado correctamente.'})
    except Exception as e:
        g.db.rollback()
        return jsonify({'status': 'error', 'message': 'No se puede eliminar: el paciente tiene registros asociados.'})
    finally:
        cur.close()