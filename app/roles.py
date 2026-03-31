from flask import Blueprint, render_template, request, redirect, url_for, flash, g, session

roles_bp = Blueprint('roles', __name__)

# FIREWALL DE SEGURIDAD GLOBAL
@roles_bp.before_request
def check_auth():
    if 'user_id' not in session:
        flash('Acceso denegado: Por favor, inicie sesión.', 'danger')
        return redirect(url_for('main.index'))

@roles_bp.route('/')
def index():
    cur = g.db.cursor()
    cur.execute("SELECT id, nombre FROM roles ORDER BY nombre ASC")
    roles = cur.fetchall()
    cur.close()
    return render_template('roles.html', roles=roles)

@roles_bp.route('/save', methods=['POST'])
def save():
    r_id = request.form.get('id')
    nombre = request.form.get('nombre', '').strip().upper()
    
    cur = g.db.cursor()
    try:
        if r_id:
            cur.execute("UPDATE roles SET nombre = %s WHERE id = %s", (nombre, r_id))
            flash('Rol actualizado exitosamente.', 'success')
        else:
            cur.execute("INSERT INTO roles (nombre) VALUES (%s)", (nombre,))
            flash('Rol creado exitosamente.', 'success')
        g.db.commit()
    except Exception as e:
        if hasattr(g, 'db'): g.db.rollback()
        flash(f'Error al guardar rol: {str(e)}', 'danger')
    finally:
        cur.close()
    return redirect(url_for('roles.index'))

@roles_bp.route('/delete/<int:id>')
def delete(id):
    cur = g.db.cursor()
    try:
        cur.execute("DELETE FROM roles WHERE id = %s", (id,))
        g.db.commit()
        flash('Rol eliminado correctamente.', 'success')
    except Exception:
        if hasattr(g, 'db'): g.db.rollback()
        flash('No se puede eliminar: existen usuarios asociados a este rol en el sistema.', 'danger')
    finally:
        cur.close()
    return redirect(url_for('roles.index'))