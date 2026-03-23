from flask import Blueprint, render_template, g, request, redirect, url_for, flash, session

states_bp = Blueprint('states', __name__)

@states_bp.route('/')
def index():
    if not session.get('user_id'):
        return redirect(url_for('main.index'))
    
    cur = g.db.cursor()
    try:
        cur.execute("SELECT id, nombre FROM estados ORDER BY nombre ASC")
        estados = cur.fetchall()
    except Exception as e:
        print(f"Error Estados Index: {e}")
        estados = []
    finally:
        cur.close()
        
    return render_template('states.html', estados=estados)

@states_bp.route('/save', methods=['POST'])
def save():
    est_id = request.form.get('id')
    nombre = request.form.get('nombre', '').strip().upper()

    if not nombre:
        flash("El nombre del estado es obligatorio.", "danger")
        return redirect(url_for('states.index'))

    cur = g.db.cursor()
    try:
        if not est_id or est_id == "": # NUEVO
            cur.execute("SELECT id FROM estados WHERE nombre = %s", (nombre,))
            if cur.fetchone():
                flash(f"El estado '{nombre}' ya existe.", "warning")
            else:
                cur.execute("INSERT INTO estados (nombre) VALUES (%s)", (nombre,))
                flash("Estado registrado correctamente.", "success")
        else: # EDITAR
            cur.execute("UPDATE estados SET nombre = %s WHERE id = %s", (nombre, est_id))
            flash("Estado actualizado correctamente.", "success")
            
        g.db.commit()
    except Exception as e:
        g.db.rollback()
        flash(f"Error al guardar: {str(e)}", "danger")
    finally:
        cur.close()
        
    return redirect(url_for('states.index'))

@states_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    cur = g.db.cursor()
    try:
        cur.execute("DELETE FROM estados WHERE id = %s", (id,))
        g.db.commit()
        flash("Estado eliminado del sistema.", "warning")
    except Exception as e:
        g.db.rollback()
        flash("No se puede eliminar: el estado está siendo utilizado por otros registros.", "danger")
    finally:
        cur.close()
    return redirect(url_for('states.index'))