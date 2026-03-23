from flask import Blueprint, render_template, g, request, redirect, url_for, flash, jsonify
from .utils import limpiar_rut, validar_rut

patients_bp = Blueprint('patients', __name__)

@patients_bp.route('/')
def index():
    cur = g.db.cursor()
    # Obtenemos los datos. Usamos DictCursor para acceder por nombre de columna
    cur.execute("SELECT id, rut, nombre, apellido, fecha_nacimiento FROM pacientes ORDER BY nombre ASC")
    pacientes = cur.fetchall()
    cur.close()
    return render_template('patients.html', pacientes=pacientes)

@patients_bp.route('/verificar_rut/<string:rut>')
def verificar_rut_ajax(rut):
    """Valida RUT real y disponibilidad en base de datos."""
    rut_plano = limpiar_rut(rut)
    
    if not validar_rut(rut_plano):
        return jsonify({"status": "error", "message": "RUT no válido"})
    
    cur = g.db.cursor()
    cur.execute("SELECT id FROM pacientes WHERE rut = %s", (rut_plano,))
    existe = cur.fetchone()
    cur.close()
    
    if existe:
        return jsonify({"status": "duplicado", "message": "RUT ya registrado"})
    
    return jsonify({"status": "ok"})

@patients_bp.route('/save', methods=['POST'])
def save():
    pac_id = request.form.get('id')
    rut_raw = request.form.get('rut')
    nombre = request.form.get('nombre', '').strip().upper()
    apellido = request.form.get('apellido', '').strip().upper()
    fecha = request.form.get('fecha_nacimiento')

    if not rut_raw or not nombre or not apellido or not fecha:
        flash("Complete todos los campos", "warning")
        return redirect(url_for('patients.index'))

    rut_plano = limpiar_rut(rut_raw)
    cur = g.db.cursor()
    
    try:
        # Lógica para Nuevo Registro
        if not pac_id or pac_id == "" or pac_id == "None":
            cur.execute("SELECT id FROM pacientes WHERE rut = %s", (rut_plano,))
            if cur.fetchone():
                flash("RUT ya registrado", "warning")
            else:
                cur.execute("""
                    INSERT INTO pacientes (rut, nombre, apellido, fecha_nacimiento) 
                    VALUES (%s, %s, %s, %s)
                """, (rut_plano, nombre, apellido, fecha))
                flash('Paciente registrado', 'success')
        
        # Lógica para Actualización (Edición)
        else:
            cur.execute("""
                UPDATE pacientes 
                SET nombre=%s, apellido=%s, fecha_nacimiento=%s 
                WHERE id=%s
            """, (nombre, apellido, fecha, pac_id))
            flash('Cambios guardados', 'success')
            
        g.db.commit()
    except Exception as e:
        g.db.rollback()
        flash(f'Error al procesar: {str(e)}', 'danger')
    finally:
        cur.close()
        
    return redirect(url_for('patients.index'))

@patients_bp.route('/delete/<int:id>')
def delete(id):
    cur = g.db.cursor()
    try:
        cur.execute("DELETE FROM pacientes WHERE id = %s", (id,))
        g.db.commit()
        flash('Registro eliminado', 'warning')
    except:
        g.db.rollback()
        flash('No se pudo eliminar el registro', 'danger')
    finally:
        cur.close()
    return redirect(url_for('patients.index'))