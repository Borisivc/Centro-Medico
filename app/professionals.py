from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, g, session

professionals_bp = Blueprint('professionals', __name__)

@professionals_bp.route('/profesionales')
def index():
    if not session.get('user_id'):
        return redirect(url_for('main.index'))
    
    cur = g.db.cursor()
    try:
        # Consulta con estados relacionales y concatenación de especialidades
        cur.execute("""
            SELECT p.id, p.rut, p.nombre, p.apellido, p.activo as estado_id, est.nombre as estado_nombre,
                   GROUP_CONCAT(e.nombre SEPARATOR ', ') as especialidades_nombres,
                   GROUP_CONCAT(e.id SEPARATOR ',') as especialidades_ids
            FROM profesionales p
            LEFT JOIN profesionales_especialidades pe ON p.id = pe.profesional_id
            LEFT JOIN especialidades e ON pe.especialidad_id = e.id
            LEFT JOIN estados_maestros est ON p.activo = est.id
            GROUP BY p.id
            ORDER BY p.id DESC
        """)
        profs = cur.fetchall()
    except Exception as e:
        print(f"Error Index Profesionales: {e}")
        profs = []

    # Datos para los selectores del modal
    cur.execute("SELECT id, nombre FROM especialidades ORDER BY nombre ASC")
    todas_especialidades = cur.fetchall()
    
    cur.execute("SELECT id, nombre FROM estados_maestros WHERE categoria = 'GENERAL' ORDER BY id ASC")
    estados_disponibles = cur.fetchall()
    
    cur.close()
    return render_template('professionals.html', profesionales=profs, todas_especialidades=todas_especialidades, estados=estados_disponibles)

@professionals_bp.route('/profesionales/save', methods=['POST'])
def save():
    prof_id = request.form.get('prof_id')
    rut = request.form.get('rut')
    nombre = request.form.get('nombre').upper()
    apellido = request.form.get('apellido').upper()
    estado_id = request.form.get('activo')
    especialidades_seleccionadas = request.form.getlist('especialidades')

    cur = g.db.cursor()
    try:
        if prof_id and prof_id.strip() != '':
            # UPDATE
            cur.execute("""
                UPDATE profesionales SET rut=%s, nombre=%s, apellido=%s, activo=%s WHERE id=%s
            """, (rut, nombre, apellido, estado_id, prof_id))
            cur.execute("DELETE FROM profesionales_especialidades WHERE profesional_id=%s", (prof_id,))
            id_final = prof_id
        else:
            # INSERT
            cur.execute("""
                INSERT INTO profesionales (rut, nombre, apellido, activo) VALUES (%s, %s, %s, %s)
            """, (rut, nombre, apellido, estado_id))
            id_final = cur.lastrowid
        
        for esp_id in especialidades_seleccionadas:
            cur.execute("INSERT INTO profesionales_especialidades (profesional_id, especialidad_id) VALUES (%s, %s)", (id_final, esp_id))

        g.db.commit()
        flash('Datos guardados correctamente', 'success')
    except Exception as e:
        g.db.rollback()
        print(f"Error Save Prof: {e}")
        flash('Error al guardar el profesional', 'danger')
    finally:
        cur.close()
    return redirect(url_for('professionals.index'))

@professionals_bp.route('/profesionales/delete/<int:id>', methods=['POST'])
def delete(id):
    cur = g.db.cursor()
    try:
        cur.execute("DELETE FROM profesionales_especialidades WHERE profesional_id = %s", (id,))
        cur.execute("DELETE FROM profesionales WHERE id = %s", (id,))
        g.db.commit()
        return jsonify({'status': 'success'})
    except:
        g.db.rollback()
        return jsonify({'status': 'error'})
    finally: cur.close()

@professionals_bp.route('/profesionales/verificar/<string:rut>')
def verificar_rut(rut):
    cur = g.db.cursor()
    cur.execute("SELECT nombre FROM profesionales WHERE rut = %s", (rut,))
    p = cur.fetchone()
    cur.close()
    return jsonify({"existe": True}) if p else jsonify({"existe": False})