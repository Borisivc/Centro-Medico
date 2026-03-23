from flask import Blueprint, render_template, g, request, redirect, url_for, flash, session

roles_bp = Blueprint('roles', __name__)

@roles_bp.route('/')
def index():
    if not session.get('user_id'):
        return redirect(url_for('main.index'))
    
    cur = g.db.cursor()
    try:
        cur.execute("SELECT id, nombre FROM roles ORDER BY nombre ASC")
        roles = cur.fetchall()
    except Exception as e:
        print(f"Error Roles Index: {e}")
        roles = []
    finally:
        cur.close()
        
    return render_template('roles.html', roles=roles)

@roles_bp.route('/save', methods=['POST'])
def save():
    rol_id = request.form.get('id')
    nombre = request.form.get('nombre', '').strip().upper()

    if not nombre:
        flash("El nombre del rol es obligatorio.", "danger")
        return redirect(url_for('roles.index'))

    cur = g.db.cursor()
    try:
        if not rol_id or rol_id == "": # NUEVO
            cur.execute("SELECT id FROM roles WHERE nombre = %s", (nombre,))
            if cur.fetchone():
                flash(f"El rol '{nombre}' ya existe.", "warning")
            else:
                cur.execute("INSERT INTO roles (nombre) VALUES (%s)", (nombre,))
                flash("Rol creado exitosamente.", "success")
        else: # EDITAR
            cur.execute("UPDATE roles SET nombre = %s WHERE id = %s", (nombre, rol_id))
            flash("Rol actualizado correctamente.", "success")
            
        g.db.commit()
    except Exception as e:
        g.db.rollback()
        flash(f"Error al guardar: {str(e)}", "danger")
    finally:
        cur.close()
        
    return redirect(url_for('roles.index'))

@roles_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    cur = g.db.cursor()
    try:
        cur.execute("DELETE FROM roles WHERE id = %s", (id,))
        g.db.commit()
        flash("Rol eliminado correctamente.", "warning")
    except Exception as e:
        g.db.rollback()
        flash("No se puede eliminar: el rol está asignado a usuarios.", "danger")
    finally:
        cur.close()
    return redirect(url_for('roles.index'))