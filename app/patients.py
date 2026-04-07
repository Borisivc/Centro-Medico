from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g, session

# Definición del Blueprint
patients_bp = Blueprint('patients', __name__)

# ==============================================================================
# 🛡️ FIREWALL DE SEGURIDAD GLOBAL (RBAC) PARA PACIENTES
# ==============================================================================
@patients_bp.before_request
def check_auth():
    if 'user_id' not in session:
        flash('Acceso denegado: Por favor, inicie sesión.', 'danger')
        return redirect(url_for('main.index'))
    
    # Validamos por NOMBRE de rol, como solicitaste.
    if session.get('user_rol') not in ['ADMIN', 'RECEPCION']:
        flash('No tiene los permisos necesarios (Admin/Recepción) para acceder a Gestión de Pacientes.', 'danger')
        return redirect(url_for('main.dashboard'))

@patients_bp.route('/')
def index():
    cur = g.db.cursor()
    cur.execute("SELECT id, rut, nombre, apellido, fecha_nacimiento FROM pacientes ORDER BY nombre ASC")
    rows = cur.fetchall()
    
    pacientes = []
    for row in rows:
        if isinstance(row, dict):
            pacientes.append({
                'id': row.get('id'),
                'rut': row.get('rut'),
                'nombre': row.get('nombre'),
                'apellido': row.get('apellido'),
                'fecha_nacimiento': row.get('fecha_nacimiento')
            })
        else:
            pacientes.append({
                'id': row[0],
                'rut': row[1],
                'nombre': row[2],
                'apellido': row[3],
                'fecha_nacimiento': row[4]
            })
    
    cur.close()
    return render_template('patients.html', pacientes=pacientes)

@patients_bp.route('/save', methods=['POST'])
def save():
    paciente_id = request.form.get('id')
    rut_raw = request.form.get('rut', '')
    rut_limpio = rut_raw.replace(".", "").replace("-", "").strip()
    
    nombre = request.form.get('nombre', '').strip().upper()
    apellido = request.form.get('apellido', '').strip().upper()
    fecha_nacimiento = request.form.get('fecha_nacimiento')

    cur = g.db.cursor()
    try:
        if paciente_id: 
            query = "UPDATE pacientes SET nombre = %s, apellido = %s, fecha_nacimiento = %s WHERE id = %s"
            cur.execute(query, (nombre, apellido, fecha_nacimiento, paciente_id))
            g.db.commit()
            flash('Paciente actualizado exitosamente', 'success')
        else: 
            cur.execute("SELECT id FROM pacientes WHERE rut = %s", (rut_limpio,))
            if cur.fetchone():
                flash('El RUT ya se encuentra registrado', 'warning')
            else:
                query = "INSERT INTO pacientes (rut, nombre, apellido, fecha_nacimiento) VALUES (%s, %s, %s, %s)"
                cur.execute(query, (rut_limpio, nombre, apellido, fecha_nacimiento))
                g.db.commit()
                flash('Paciente registrado exitosamente', 'success')

    except Exception as e:
        if hasattr(g, 'db'): g.db.rollback()
        flash(f'Error: {str(e)}', 'danger')
    finally:
        cur.close()

    return redirect(url_for('patients.index'))

@patients_bp.route('/delete/<int:id>')
def delete(id):
    cur = g.db.cursor()
    try:
        cur.execute("DELETE FROM pacientes WHERE id = %s", (id,))
        g.db.commit()
        flash('Paciente eliminado correctamente', 'success')
    except Exception:
        if hasattr(g, 'db'): g.db.rollback()
        flash('No se puede eliminar: existen registros asociados', 'danger')
    finally:
        cur.close()
    
    return redirect(url_for('patients.index'))

@patients_bp.route('/verificar_rut/<rut>')
def verificar_rut_ajax(rut):
    rut_busqueda = rut.replace(".", "").replace("-", "").strip()
    cur = g.db.cursor()
    cur.execute("SELECT id FROM pacientes WHERE rut = %s", (rut_busqueda,))
    existe = cur.fetchone()
    cur.close()

    if existe:
        return jsonify({'status': 'duplicado', 'message': 'RUT ya registrado.'})
    return jsonify({'status': 'ok'})