from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g

roles_bp = Blueprint('roles', __name__)

@roles_bp.route('/')
def index():
    cur = g.db.cursor()
    cur.execute("SELECT id, nombre FROM roles ORDER BY nombre ASC")
    rows = cur.fetchall()
    
    roles = []
    for row in rows:
        if isinstance(row, dict):
            roles.append({'id': row.get('id'), 'nombre': row.get('nombre')})
        else:
            roles.append({'id': row[0], 'nombre': row[1]})
            
    cur.close()
    return render_template('roles.html', roles=roles)

@roles_bp.route('/save', methods=['POST'])
def save():
    rol_id = request.form.get('id')
    nombre = request.form.get('nombre', '').strip().upper()

    cur = g.db.cursor()
    try:
        if rol_id:  # EDICIÓN
            cur.execute("SELECT id FROM roles WHERE nombre = %s AND id != %s", (nombre, rol_id))
            if cur.fetchone():
                flash('El nombre de este rol ya existe en otro registro.', 'warning')
                return redirect(url_for('roles.index'))
                
            cur.execute("UPDATE roles SET nombre = %s WHERE id = %s", (nombre, rol_id))
            flash('Rol actualizado correctamente.', 'success')
            
        else:  # NUEVO
            cur.execute("SELECT id FROM roles WHERE nombre = %s", (nombre,))
            if cur.fetchone():
                flash('El rol ingresado ya se encuentra registrado.', 'warning')
                return redirect(url_for('roles.index'))
                
            cur.execute("INSERT INTO roles (nombre) VALUES (%s)", (nombre,))
            flash('Rol registrado exitosamente.', 'success')
            
        g.db.commit()
    except Exception as e:
        if hasattr(g, 'db'): g.db.rollback()
        flash(f'Error al procesar la solicitud: {str(e)}', 'danger')
    finally:
        cur.close()

    return redirect(url_for('roles.index'))

@roles_bp.route('/delete/<int:id>')
def delete(id):
    cur = g.db.cursor()
    try:
        # VERIFICACIÓN EXPLÍCITA DE INTEGRIDAD
        # Buscamos si existe al menos un usuario con este rol asignado
        cur.execute("SELECT usuario_id FROM usuarios_roles WHERE rol_id = %s LIMIT 1", (id,))
        en_uso = cur.fetchone()
        
        if en_uso:
            flash('Acción denegada: Existen usuarios que tienen asignado este rol.', 'danger')
            return redirect(url_for('roles.index'))
            
        # Si no está en uso, procedemos a eliminar
        cur.execute("DELETE FROM roles WHERE id = %s", (id,))
        g.db.commit()
        flash('Rol eliminado correctamente.', 'success')
        
    except Exception as e:
        if hasattr(g, 'db'): g.db.rollback()
        flash(f'Error al intentar eliminar: {str(e)}', 'danger')
    finally:
        cur.close()
        
    return redirect(url_for('roles.index'))

@roles_bp.route('/verificar_nombre/<nombre>')
def verificar_nombre_ajax(nombre):
    nombre_busqueda = nombre.strip().upper()
    cur = g.db.cursor()
    cur.execute("SELECT id FROM roles WHERE nombre = %s", (nombre_busqueda,))
    existe = cur.fetchone()
    cur.close()
    
    if existe:
        return jsonify({'status': 'duplicado', 'message': 'Este rol ya se encuentra registrado en el sistema.'})
        
    return jsonify({'status': 'ok'})