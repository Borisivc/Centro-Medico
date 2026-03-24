from flask import Blueprint, render_template, request, redirect, url_for, flash, g

availability_bp = Blueprint('availability', __name__)

@availability_bp.route('/')
def index():
    cur = g.db.cursor()
    query = """
        SELECT d.id, d.profesional_id, CONCAT(p.nombre, ' ', p.apellido) as profesional,
               TIME_FORMAT(d.hora_inicio, '%H:%i') as hi, 
               TIME_FORMAT(d.hora_fin, '%H:%i') as hf,
               DATE_FORMAT(d.fecha_inicio, '%d-%m-%Y') as fi_es, 
               DATE_FORMAT(d.fecha_inicio, '%Y-%m-%d') as fi_iso,
               DATE_FORMAT(d.fecha_fin, '%d-%m-%Y') as ff_es, 
               DATE_FORMAT(d.fecha_fin, '%Y-%m-%d') as ff_iso,
               d.dia_semana, d.duracion_cita, d.tipo
        FROM disponibilidad_profesional d
        JOIN profesionales p ON d.profesional_id = p.id
        ORDER BY profesional ASC, d.dia_semana ASC
    """
    cur.execute(query)
    disponibilidades = cur.fetchall()
    
    cur.execute("SELECT id, nombre, apellido FROM profesionales WHERE activo = 1 ORDER BY nombre ASC")
    profesionales = cur.fetchall()
    
    cur.close()
    return render_template('availability.html', disponibilidades=disponibilidades, profesionales=profesionales)

@availability_bp.route('/save', methods=['POST'])
def save():
    disp_id = request.form.get('id')
    prof_id = request.form.get('profesional_id')
    h_ini = request.form.get('hora_inicio')
    h_fin = request.form.get('hora_fin')
    f_ini = request.form.get('fecha_inicio')
    f_fin = request.form.get('fecha_fin')
    dur = request.form.get('duracion_cita')
    tipo = request.form.get('tipo', 0)
    dias = request.form.getlist('dias_semana')

    cur = g.db.cursor()
    try:
        if disp_id:
            cur.execute("""
                UPDATE disponibilidad_profesional 
                SET profesional_id=%s, hora_inicio=%s, hora_fin=%s, fecha_inicio=%s, fecha_fin=%s, 
                    dia_semana=%s, duracion_cita=%s, tipo=%s 
                WHERE id=%s
            """, (prof_id, h_ini, h_fin, f_ini, f_fin, dias[0] if dias else 0, dur, tipo, disp_id))
        else:
            for dia in dias:
                cur.execute("""
                    INSERT INTO disponibilidad_profesional 
                    (profesional_id, hora_inicio, hora_fin, fecha_inicio, fecha_fin, dia_semana, duracion_cita, tipo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (prof_id, h_ini, h_fin, f_ini, f_fin, dia, dur, tipo))
        g.db.commit()
        flash('Disponibilidad guardada con éxito.', 'success')
    except Exception as e:
        if hasattr(g, 'db'): g.db.rollback()
        flash(f'Error al guardar: {str(e)}', 'danger')
    finally:
        cur.close()
    return redirect(url_for('availability.index'))

@availability_bp.route('/delete/<int:id>')
def delete(id):
    cur = g.db.cursor()
    try:
        cur.execute("DELETE FROM disponibilidad_profesional WHERE id = %s", (id,))
        g.db.commit()
        flash('Registro de disponibilidad eliminado.', 'success')
    except Exception as e:
        if hasattr(g, 'db'): g.db.rollback()
        flash(f'Error al eliminar: {str(e)}', 'danger')
    finally:
        cur.close()
    return redirect(url_for('availability.index'))