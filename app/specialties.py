from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g

specialties_bp = Blueprint('specialties', __name__)

@specialties_bp.route('/')
def index():
    cur = g.db.cursor()
    
    # Obtener todas las especialidades
    cur.execute("SELECT id, nombre FROM especialidades ORDER BY nombre ASC")
    rows = cur.fetchall()
    
    # Mapeo robusto anti-KeyError
    especialidades = []
    for row in rows:
        if isinstance(row, dict):
            especialidades.append({
                'id': row.get('id'),
                'nombre': row.get('nombre')
            })
        else:
            especialidades.append({
                'id': row[0],
                'nombre': row[1]
            })
            
    cur.close()
    return render_template('specialties.html', especialidades=especialidades)

@specialties_bp.route('/save', methods=['POST'])
def save():
    esp_id = request.form.get('id')
    nombre = request.form.get('nombre', '').strip().upper()

    cur = g.db.cursor()
    try:
        if esp_id:  # MODO EDICIÓN
            # Verificar que al editar no estemos usando el nombre de OTRA especialidad
            cur.execute("SELECT id FROM especialidades WHERE nombre = %s AND id != %s", (nombre, esp_id))
            if cur.fetchone():
                flash('El nombre de esta especialidad ya existe en otro registro.', 'warning')
                return redirect(url_for('specialties.index'))
                
            cur.execute("UPDATE especialidades SET nombre = %s WHERE id = %s", (nombre, esp_id))
            flash('Especialidad actualizada correctamente.', 'success')
            
        else:  # MODO NUEVO
            # Verificar duplicado antes de insertar
            cur.execute("SELECT id FROM especialidades WHERE nombre = %s", (nombre,))
            if cur.fetchone():
                flash('La especialidad ingresada ya se encuentra registrada.', 'warning')
                return redirect(url_for('specialties.index'))
                
            cur.execute("INSERT INTO especialidades (nombre) VALUES (%s)", (nombre,))
            flash('Especialidad registrada exitosamente.', 'success')
            
        g.db.commit()
    
    except Exception as e:
        if hasattr(g, 'db'): g.db.rollback()
        flash(f'Error al procesar la solicitud: {str(e)}', 'danger')
    finally:
        cur.close()

    return redirect(url_for('specialties.index'))

@specialties_bp.route('/delete/<int:id>')
def delete(id):
    cur = g.db.cursor()
    try:
        cur.execute("DELETE FROM especialidades WHERE id = %s", (id,))
        g.db.commit()
        flash('Especialidad eliminada correctamente.', 'success')
    except Exception:
        if hasattr(g, 'db'): g.db.rollback()
        # Si explota el DELETE es porque hay registros en la tabla profesionales_especialidades
        flash('No se puede eliminar: Existen profesionales asociados a esta especialidad médica.', 'danger')
    finally:
        cur.close()
    return redirect(url_for('specialties.index'))

@specialties_bp.route('/verificar_nombre/<nombre>')
def verificar_nombre_ajax(nombre):
    nombre_busqueda = nombre.strip().upper()
    cur = g.db.cursor()
    cur.execute("SELECT id FROM especialidades WHERE nombre = %s", (nombre_busqueda,))
    existe = cur.fetchone()
    cur.close()
    
    if existe:
        return jsonify({'status': 'duplicado', 'message': 'Esta especialidad ya se encuentra registrada en el sistema.'})
        
    return jsonify({'status': 'ok'})