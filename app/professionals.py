from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g, session

professionals_bp = Blueprint('professionals', __name__)

# FIREWALL DE SEGURIDAD GLOBAL
@professionals_bp.before_request
def check_auth():
    if 'user_id' not in session:
        flash('Acceso denegado: Por favor, inicie sesión.', 'danger')
        return redirect(url_for('main.index'))

@professionals_bp.route('/')
def index():
    cur = g.db.cursor()
    
    cur.execute("SELECT id, nombre FROM especialidades ORDER BY nombre ASC")
    esp_rows = cur.fetchall()
    
    especialidades_disponibles = []
    for r in esp_rows:
        if isinstance(r, dict):
            especialidades_disponibles.append({'id': r.get('id'), 'nombre': r.get('nombre')})
        else:
            especialidades_disponibles.append({'id': r[0], 'nombre': r[1]})
    
    cur.execute("SELECT id, rut, nombre, apellido, email, activo FROM profesionales ORDER BY nombre ASC")
    prof_rows = cur.fetchall()
    
    cur.execute("SELECT profesional_id, especialidad_id FROM profesionales_especialidades")
    relaciones = cur.fetchall()
    
    esp_por_prof = {}
    for rel in relaciones:
        if isinstance(rel, dict):
            prof_id = rel.get('profesional_id')
            esp_id = rel.get('especialidad_id')
        else:
            prof_id = rel[0]
            esp_id = rel[1]
            
        if prof_id not in esp_por_prof:
            esp_por_prof[prof_id] = []
        esp_por_prof[prof_id].append(str(esp_id))
        
    profesionales = []
    for row in prof_rows:
        if isinstance(row, dict):
            p_id = row.get('id')
            rut = row.get('rut')
            nombre = row.get('nombre')
            apellido = row.get('apellido')
            email = row.get('email')
            activo = row.get('activo')
        else:
            p_id = row[0]
            rut = row[1]
            nombre = row[2]
            apellido = row[3]
            email = row[4]
            activo = row[5]
        
        ids_esp = esp_por_prof.get(p_id, [])
        nombres_esp = [e['nombre'] for e in especialidades_disponibles if str(e['id']) in ids_esp]
        texto_especialidades = ", ".join(nombres_esp) if nombres_esp else "Sin especialidad"

        profesionales.append({
            'id': p_id,
            'rut': rut,
            'nombre': nombre,
            'apellido': apellido,
            'email': email,
            'activo': activo,
            'especialidades_ids': ids_esp,
            'especialidades_texto': texto_especialidades
        })
        
    cur.close()
    return render_template('professionals.html', profesionales=profesionales, especialidades_disponibles=especialidades_disponibles)

@professionals_bp.route('/save', methods=['POST'])
def save():
    prof_id = request.form.get('id')
    rut_limpio = request.form.get('rut', '').replace(".", "").replace("-", "").strip()
    nombre = request.form.get('nombre', '').strip().upper()
    apellido = request.form.get('apellido', '').strip().upper()
    email = request.form.get('email', '').strip().lower()
    activo = request.form.get('activo', 1)
    
    especialidades_seleccionadas = request.form.getlist('especialidades[]')

    cur = g.db.cursor()
    try:
        if prof_id:
            cur.execute("""
                UPDATE profesionales 
                SET nombre = %s, apellido = %s, email = %s, activo = %s 
                WHERE id = %s
            """, (nombre, apellido, email, activo, prof_id))
            cur.execute("DELETE FROM profesionales_especialidades WHERE profesional_id = %s", (prof_id,))
        
        else:
            cur.execute("SELECT id FROM profesionales WHERE rut = %s", (rut_limpio,))
            if cur.fetchone():
                flash('El RUT ingresado ya pertenece a un profesional.', 'warning')
                return redirect(url_for('professionals.index'))
                
            cur.execute("""
                INSERT INTO profesionales (rut, nombre, apellido, email, activo) 
                VALUES (%s, %s, %s, %s, %s)
            """, (rut_limpio, nombre, apellido, email, activo))
            prof_id = cur.lastrowid

        if especialidades_seleccionadas:
            for esp_id in especialidades_seleccionadas:
                cur.execute("""
                    INSERT INTO profesionales_especialidades (profesional_id, especialidad_id) 
                    VALUES (%s, %s)
                """, (prof_id, esp_id))
            
        g.db.commit()
        flash('Datos del profesional actualizados correctamente.', 'success')
    
    except Exception as e:
        if hasattr(g, 'db'): g.db.rollback()
        flash(f'Error al procesar la solicitud: {str(e)}', 'danger')
    finally:
        cur.close()

    return redirect(url_for('professionals.index'))

@professionals_bp.route('/delete/<int:id>')
def delete(id):
    cur = g.db.cursor()
    try:
        cur.execute("DELETE FROM profesionales_especialidades WHERE profesional_id = %s", (id,))
        cur.execute("DELETE FROM profesionales WHERE id = %s", (id,))
        g.db.commit()
        flash('Profesional y sus especialidades eliminados correctamente.', 'success')
    except Exception as e:
        if hasattr(g, 'db'): g.db.rollback()
        flash('No se puede eliminar: el profesional tiene registros críticos asociados (ej: agenda activa).', 'danger')
    finally:
        cur.close()
    return redirect(url_for('professionals.index'))

@professionals_bp.route('/verificar_rut/<rut>')
def verificar_rut_ajax(rut):
    rut_busqueda = rut.replace(".", "").replace("-", "").strip().upper()
    
    if len(rut_busqueda) < 8:
        return jsonify({'status': 'invalido', 'message': 'El RUT ingresado es demasiado corto.'})
        
    cuerpo = rut_busqueda[:-1]
    dv_ingresado = rut_busqueda[-1]
    
    if not cuerpo.isdigit():
        return jsonify({'status': 'invalido', 'message': 'Formato de RUT incorrecto.'})
        
    suma = 0
    multiplo = 2
    for r in reversed(cuerpo):
        suma += int(r) * multiplo
        multiplo += 1
        if multiplo == 8:
            multiplo = 2
    
    dv_esperado = 11 - (suma % 11)
    dv_esperado = '0' if dv_esperado == 11 else 'K' if dv_esperado == 10 else str(dv_esperado)
    
    if dv_esperado != dv_ingresado:
        return jsonify({'status': 'invalido', 'message': 'El RUT ingresado no es válido (Dígito verificador incorrecto).'})

    cur = g.db.cursor()
    cur.execute("SELECT id FROM profesionales WHERE rut = %s", (rut_busqueda[:-1] + dv_ingresado,))
    existe = cur.fetchone()
    cur.close()
    
    if existe:
        return jsonify({'status': 'duplicado', 'message': 'Este RUT ya se encuentra registrado en el sistema.'})
        
    return jsonify({'status': 'ok'})