from flask import Blueprint, render_template, request, redirect, url_for, flash, g, session

states_bp = Blueprint('states', __name__)

# FIREWALL DE SEGURIDAD GLOBAL
@states_bp.before_request
def check_auth():
    if 'user_id' not in session:
        flash('Acceso denegado: Por favor, inicie sesión.', 'danger')
        return redirect(url_for('main.index'))

@states_bp.route('/')
def index():
    cur = g.db.cursor()
    cur.execute("SELECT id, nombre FROM estados_agenda ORDER BY nombre ASC")
    estados = cur.fetchall()
    cur.close()
    return render_template('states.html', estados=estados)

@states_bp.route('/save', methods=['POST'])
def save():
    s_id = request.form.get('id')
    nombre = request.form.get('nombre', '').strip().upper()
    
    cur = g.db.cursor()
    try:
        if s_id:
            cur.execute("UPDATE estados_agenda SET nombre = %s WHERE id = %s", (nombre, s_id))
            flash('Estado actualizado correctamente.', 'success')
        else:
            cur.execute("INSERT INTO estados_agenda (nombre) VALUES (%s)", (nombre,))
            flash('Estado creado exitosamente.', 'success')
        g.db.commit()
    except Exception as e:
        if hasattr(g, 'db'): g.db.rollback()
        flash(f'Error al guardar estado: {str(e)}', 'danger')
    finally:
        cur.close()
    return redirect(url_for('states.index'))

@states_bp.route('/delete/<int:id>')
def delete(id):
    cur = g.db.cursor()
    try:
        cur.execute("DELETE FROM estados_agenda WHERE id = %s", (id,))
        g.db.commit()
        flash('Estado eliminado correctamente.', 'success')
    except Exception:
        if hasattr(g, 'db'): g.db.rollback()
        flash('No se puede eliminar: existen citas de pacientes asociadas a este estado en la agenda.', 'danger')
    finally:
        cur.close()
    return redirect(url_for('states.index'))