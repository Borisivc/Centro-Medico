from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g

states_bp = Blueprint('states', __name__)

@states_bp.route('/')
def index():
    cur = g.db.cursor()
    # Apuntando a la tabla correcta: estados_agenda
    cur.execute("SELECT id, nombre FROM estados_agenda ORDER BY nombre ASC")
    rows = cur.fetchall()
    
    estados = []
    for row in rows:
        if isinstance(row, dict):
            estados.append({'id': row.get('id'), 'nombre': row.get('nombre')})
        else:
            estados.append({'id': row[0], 'nombre': row[1]})
            
    cur.close()
    return render_template('states.html', estados=estados)

@states_bp.route('/save', methods=['POST'])
def save():
    estado_id = request.form.get('id')
    nombre = request.form.get('nombre', '').strip().upper()

    cur = g.db.cursor()
    try:
        if estado_id:  # EDICIÓN
            cur.execute("SELECT id FROM estados_agenda WHERE nombre = %s AND id != %s", (nombre, estado_id))
            if cur.fetchone():
                flash('El nombre de este estado ya existe en otro registro.', 'warning')
                return redirect(url_for('states.index'))
                
            cur.execute("UPDATE estados_agenda SET nombre = %s WHERE id = %s", (nombre, estado_id))
            flash('Estado actualizado correctamente.', 'success')
            
        else:  # NUEVO
            cur.execute("SELECT id FROM estados_agenda WHERE nombre = %s", (nombre,))
            if cur.fetchone():
                flash('El estado ingresado ya se encuentra registrado.', 'warning')
                return redirect(url_for('states.index'))
                
            cur.execute("INSERT INTO estados_agenda (nombre) VALUES (%s)", (nombre,))
            flash('Estado registrado exitosamente.', 'success')
            
        g.db.commit()
    except Exception as e:
        if hasattr(g, 'db'): g.db.rollback()
        flash(f'Error al procesar la solicitud: {str(e)}', 'danger')
    finally:
        cur.close()

    return redirect(url_for('states.index'))

@states_bp.route('/delete/<int:id>')
def delete(id):
    cur = g.db.cursor()
    try:
        # VERIFICACIÓN EXPLÍCITA DE INTEGRIDAD (Asumiendo que agenda usa estado_id)
        try:
            cur.execute("SELECT id FROM agenda WHERE estado_id = %s LIMIT 1", (id,))
            en_uso = cur.fetchone()
            if en_uso:
                flash('Acción denegada: Existen citas en la agenda que utilizan este estado.', 'danger')
                return redirect(url_for('states.index'))
        except Exception:
            # Si la columna en agenda no se llama estado_id, el error se captura silenciosamente 
            # y se deja que la base de datos decida si permite el DELETE o no.
            pass

        cur.execute("DELETE FROM estados_agenda WHERE id = %s", (id,))
        g.db.commit()
        flash('Estado eliminado correctamente.', 'success')
    except Exception:
        if hasattr(g, 'db'): g.db.rollback()
        flash('No se puede eliminar: Existen registros en el sistema vinculados a este estado.', 'danger')
    finally:
        cur.close()
    return redirect(url_for('states.index'))

@states_bp.route('/verificar_nombre/<nombre>')
def verificar_nombre_ajax(nombre):
    nombre_busqueda = nombre.strip().upper()
    cur = g.db.cursor()
    cur.execute("SELECT id FROM estados_agenda WHERE nombre = %s", (nombre_busqueda,))
    existe = cur.fetchone()
    cur.close()
    
    if existe:
        return jsonify({'status': 'duplicado', 'message': 'Este estado ya se encuentra registrado en el sistema.'})
        
    return jsonify({'status': 'ok'})