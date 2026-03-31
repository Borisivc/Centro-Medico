from flask import Blueprint, render_template, request, redirect, url_for, flash, g, session

availability_bp = Blueprint('availability', __name__)

# FIREWALL DE SEGURIDAD GLOBAL
@availability_bp.before_request
def check_auth():
    if 'user_id' not in session:
        flash('Acceso denegado: Por favor, inicie sesión.', 'danger')
        return redirect(url_for('main.index'))

@availability_bp.route('/')
def index():
    cur = g.db.cursor()
    cur.execute("SELECT id, nombre, apellido FROM profesionales WHERE activo = 1 ORDER BY nombre ASC")
    profesionales = cur.fetchall()

    cur.execute("""
        SELECT d.id, d.profesional_id, d.dia_semana, 
               TIME_FORMAT(d.hora_inicio, '%H:%i') as hi, 
               TIME_FORMAT(d.hora_fin, '%H:%i') as hf, 
               DATE_FORMAT(d.fecha_inicio, '%d-%m-%Y') as fi_es, 
               DATE_FORMAT(d.fecha_fin, '%d-%m-%Y') as ff_es,
               d.fecha_inicio as fi_iso, d.fecha_fin as ff_iso,
               d.duracion_cita, d.tipo,
               CONCAT(p.nombre, ' ', p.apellido) as profesional
        FROM disponibilidad_profesional d
        JOIN profesionales p ON d.profesional_id = p.id
        ORDER BY p.nombre ASC, d.dia_semana ASC, d.hora_inicio ASC
    """)
    disponibilidades = cur.fetchall()
    cur.close()
    return render_template('availability.html', profesionales=profesionales, disponibilidades=disponibilidades)

@availability_bp.route('/save', methods=['POST'])
def save():
    d_id = request.form.get('id')
    prof_id = request.form.get('profesional_id')
    tipo = request.form.get('tipo', 0)
    dias_semana = request.form.getlist('dias_semana')
    hora_inicio = request.form.get('hora_inicio')
    hora_fin = request.form.get('hora_fin')
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')
    duracion_cita = request.form.get('duracion_cita', 15)

    cur = g.db.cursor()
    try:
        if d_id:
            dia_edit = dias_semana[0] if isinstance(dias_semana, list) and len(dias_semana) > 0 else request.form.get('dias_semana')
                
            cur.execute("""
                UPDATE disponibilidad_profesional 
                SET profesional_id=%s, dia_semana=%s, hora_inicio=%s, hora_fin=%s, 
                    fecha_inicio=%s, fecha_fin=%s, duracion_cita=%s, tipo=%s
                WHERE id=%s
            """, (prof_id, dia_edit, hora_inicio, hora_fin, fecha_inicio, fecha_fin, duracion_cita, tipo, d_id))
            flash('Horario actualizado exitosamente.', 'success')
        else:
            if not dias_semana:
                flash('Debe seleccionar al menos un día de la semana.', 'warning')
                return redirect(url_for('availability.index'))
                
            for dia in dias_semana:
                cur.execute("""
                    INSERT INTO disponibilidad_profesional 
                    (profesional_id, dia_semana, hora_inicio, hora_fin, fecha_inicio, fecha_fin, duracion_cita, tipo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (prof_id, dia, hora_inicio, hora_fin, fecha_inicio, fecha_fin, duracion_cita, tipo))
            flash('Horarios registrados exitosamente.', 'success')
        g.db.commit()
    except Exception as e:
        if hasattr(g, 'db'): g.db.rollback()
        flash(f'Error al guardar horario: {str(e)}', 'danger')
    finally:
        cur.close()
    return redirect(url_for('availability.index'))

@availability_bp.route('/delete/<int:id>')
def delete(id):
    cur = g.db.cursor()
    try:
        cur.execute("DELETE FROM disponibilidad_profesional WHERE id = %s", (id,))
        g.db.commit()
        flash('Horario eliminado.', 'success')
    except Exception as e:
        if hasattr(g, 'db'): g.db.rollback()
        flash(f'Error al eliminar: {str(e)}', 'danger')
    finally:
        cur.close()
    return redirect(url_for('availability.index'))