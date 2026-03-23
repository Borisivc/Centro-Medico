from flask import Blueprint, render_template, g, request, redirect, url_for, flash, session

specialties_bp = Blueprint('specialties', __name__)

@specialties_bp.route('/')
def index():
    if not session.get('user_id'):
        return redirect(url_for('main.index'))
    
    cur = g.db.cursor()
    try:
        cur.execute("SELECT id, nombre FROM especialidades ORDER BY nombre ASC")
        especialidades = cur.fetchall()
    except Exception as e:
        print(f"Error Especialidades: {e}")
        especialidades = []
    finally:
        cur.close()
        
    return render_template('specialties.html', especialidades=especialidades)

@specialties_bp.route('/save', methods=['POST'])
def save():
    esp_id = request.form.get('id')
    nombre = request.form.get('nombre', '').strip().upper()

    if not nombre:
        flash("El nombre de la especialidad es obligatorio.", "danger")
        return redirect(url_for('specialties.index'))

    cur = g.db.cursor()
    try:
        if not esp_id or esp_id == "": # NUEVO
            # Validar si ya existe
            cur.execute("SELECT id FROM especialidades WHERE nombre = %s", (nombre,))
            if cur.fetchone():
                flash(f"La especialidad '{nombre}' ya existe.", "warning")
            else:
                cur.execute("INSERT INTO especialidades (nombre) VALUES (%s)", (nombre,))
                flash("Especialidad creada con éxito.", "success")
        else: # EDITAR
            cur.execute("UPDATE especialidades SET nombre = %s WHERE id = %s", (nombre, esp_id))
            flash("Especialidad actualizada correctamente.", "success")
            
        g.db.commit()
    except Exception as e:
        g.db.rollback()
        flash(f"Error al guardar: {str(e)}", "danger")
    finally:
        cur.close()
        
    return redirect(url_for('specialties.index'))

@specialties_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    cur = g.db.cursor()
    try:
        # Aquí se podría validar si hay profesionales asociados antes de borrar
        cur.execute("DELETE FROM especialidades WHERE id = %s", (id,))
        g.db.commit()
        flash("Especialidad eliminada.", "warning")
    except Exception as e:
        g.db.rollback()
        flash("No se puede eliminar: existen registros asociados.", "danger")
    finally:
        cur.close()
    return redirect(url_for('specialties.index'))