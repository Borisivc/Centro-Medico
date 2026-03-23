from flask import Blueprint, render_template, g, request, redirect, url_for, flash, jsonify
from .utils import limpiar_rut, validar_rut

professionals_bp = Blueprint('professionals', __name__)

@professionals_bp.route('/')
def index():
    cur = g.db.cursor()
    try:
        cur.execute("""
            SELECT p.id, p.rut, p.nombre, p.apellido, e.nombre as estado_nombre, p.activo,
                   GROUP_CONCAT(esp.nombre SEPARATOR ', ') as especialidades_nombres
            FROM profesionales p
            JOIN estados_maestros e ON p.activo = e.id
            LEFT JOIN profesionales_especialidades pe ON p.id = pe.profesional_id
            LEFT JOIN especialidades esp ON pe.especialidad_id = esp.id
            GROUP BY p.id
            ORDER BY p.nombre ASC
        """)
        profesionales = cur.fetchall()
        
        cur.execute("SELECT id, nombre FROM estados_maestros WHERE categoria = 'GENERAL' ORDER BY nombre ASC")
        estados = cur.fetchall()
        
        cur.execute("SELECT id, nombre FROM especialidades ORDER BY nombre ASC")
        especialidades = cur.fetchall()
    except Exception as e:
        print(f"Error SQL Index Profesionales: {e}")
        profesionales, estados, especialidades = [], [], []
        flash("Error al cargar la lista de profesionales.", "danger")
    finally:
        cur.close()

    return render_template('professionals.html', 
                           profesionales=profesionales, 
                           estados=estados, 
                           especialidades=especialidades)

@professionals_bp.route('/verificar_rut/<string:rut>')
def verificar_rut_ajax(rut):
    rut_plano = limpiar_rut(rut)
    if not validar_rut(rut_plano):
        return jsonify({"status": "error", "message": "RUT no válido"})
    cur = g.db.cursor()
    cur.execute("SELECT id FROM profesionales WHERE rut = %s", (rut_plano,))
    if cur.fetchone():
        cur.close()
        return jsonify({"status": "duplicado", "message": "RUT ya registrado"})
    cur.close()
    return jsonify({"status": "ok"})

@professionals_bp.route('/save', methods=['POST'])
def save():
    prof_id = request.form.get('id')
    rut_raw = request.form.get('rut')
    nombre = (request.form.get('nombre') or "").strip().upper()
    apellido = (request.form.get('apellido') or "").strip().upper()
    estado_id = request.form.get('estado_id')
    esp_ids = request.form.getlist('especialidades')

    if not rut_raw or not nombre or not estado_id:
        flash("Complete los campos obligatorios", "warning")
        return redirect(url_for('professionals.index'))

    rut_plano = limpiar_rut(rut_raw)
    cur = g.db.cursor()
    try:
        if not prof_id or prof_id == "" or prof_id == "None":
            cur.execute("INSERT INTO profesionales (rut, nombre, apellido, activo) VALUES (%s, %s, %s, %s)", 
                        (rut_plano, nombre, apellido, estado_id))
            nuevo_id = cur.lastrowid
            for e_id in esp_ids:
                cur.execute("INSERT INTO profesionales_especialidades (profesional_id, especialidad_id) VALUES (%s, %s)", 
                            (nuevo_id, e_id))
            flash("Profesional registrado exitosamente", "success")
        else:
            cur.execute("UPDATE profesionales SET nombre=%s, apellido=%s, activo=%s WHERE id=%s", 
                        (nombre, apellido, estado_id, prof_id))
            cur.execute("DELETE FROM profesionales_especialidades WHERE profesional_id = %s", (prof_id,))
            for e_id in esp_ids:
                cur.execute("INSERT INTO profesionales_especialidades (profesional_id, especialidad_id) VALUES (%s, %s)", 
                            (prof_id, e_id))
            flash("Cambios guardados con éxito", "success")
        g.db.commit()
    except Exception as e:
        g.db.rollback()
        flash(f"Error al guardar: {str(e)}", "danger")
    finally:
        cur.close()
    return redirect(url_for('professionals.index'))

@professionals_bp.route('/delete/<int:id>')
def delete(id):
    cur = g.db.cursor()
    print(f"--- INICIO PROCESO ELIMINAR ID: {id} ---")
    try:
        cur.execute("SELECT COUNT(*) as total FROM agenda WHERE profesional_id = %s", (id,))
        count = cur.fetchone()['total']
        print(f"Registros encontrados en agenda: {count}")
        
        if count > 0:
            print("Resultado: BLOQUEADO (Tiene agenda)")
            flash("No se puede eliminar: El profesional tiene registros asociados en agenda. Solo se puede inactivar.", "warning")
            return redirect(url_for('professionals.index'))
        
        cur.execute("DELETE FROM profesionales_especialidades WHERE profesional_id = %s", (id,))
        cur.execute("DELETE FROM profesionales WHERE id = %s", (id,))
        g.db.commit()
        flash("Profesional eliminado del sistema.", "success")
    except Exception as e:
        g.db.rollback()
        print(f"Error crítico al eliminar: {e}")
        flash("Error de integridad al intentar eliminar.", "danger")
    finally:
        cur.close()
    return redirect(url_for('professionals.index'))