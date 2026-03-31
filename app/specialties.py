from flask import Blueprint, render_template, request, redirect, url_for, flash, g, session

specialties_bp = Blueprint('specialties', __name__)

# FIREWALL DE SEGURIDAD GLOBAL
@specialties_bp.before_request
def check_auth():
    if 'user_id' not in session:
        flash('Acceso denegado: Por favor, inicie sesión.', 'danger')
        return redirect(url_for('main.index'))

@specialties_bp.route('/')
def index():
    cur = g.db.cursor()
    # CORRECCIÓN: Adaptado a tu base de datos real (solo id y nombre)
    cur.execute("SELECT id, nombre FROM especialidades ORDER BY nombre ASC")
    rows = cur.fetchall()
    
    especialidades = []
    for r in rows:
        if isinstance(r, dict):
            especialidades.append({'id': r.get('id'), 'nombre': r.get('nombre')})
        else:
            especialidades.append({'id': r[0], 'nombre': r[1]})
            
    cur.close()
    return render_template('specialties.html', especialidades=especialidades)

@specialties_bp.route('/save', methods=['POST'])
def save():
    e_id = request.form.get('id')
    nombre = request.form.get('nombre', '').strip().upper()
    
    cur = g.db.cursor()
    try:
        if e_id:
            cur.execute("UPDATE especialidades SET nombre = %s WHERE id = %s", (nombre, e_id))
            flash('Especialidad actualizada correctamente.', 'success')
        else:
            cur.execute("INSERT INTO especialidades (nombre) VALUES (%s)", (nombre,))
            flash('Especialidad creada exitosamente.', 'success')
        g.db.commit()
    except Exception as e:
        if hasattr(g, 'db'): g.db.rollback()
        flash(f'Error al guardar especialidad: {str(e)}', 'danger')
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
        flash('No se puede eliminar: existen profesionales médicos asociados a esta especialidad.', 'danger')
    finally:
        cur.close()
    return redirect(url_for('specialties.index'))