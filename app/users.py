from flask import Blueprint, render_template, g, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash
from .utils import limpiar_rut, validar_rut

users_bp = Blueprint('users', __name__)

@users_bp.route('/')
def index():
    cur = g.db.cursor()
    # Consulta con roles y estados maestros
    cur.execute("""
        SELECT u.id, u.rut, u.nombre, u.email, r.nombre as rol_nombre, e.nombre as estado_nombre, u.activo, u.rol_id
        FROM usuarios u
        JOIN roles r ON u.rol_id = r.id
        JOIN estados_maestros e ON u.activo = e.id
        ORDER BY u.nombre ASC
    """)
    usuarios = cur.fetchall()
    
    cur.execute("SELECT id, nombre FROM roles ORDER BY nombre ASC")
    roles = cur.fetchall()
    
    cur.execute("SELECT id, nombre FROM estados_maestros WHERE categoria = 'GENERAL' ORDER BY nombre ASC")
    estados = cur.fetchall()
    
    cur.close()
    return render_template('users.html', usuarios=usuarios, roles=roles, estados=estados)

@users_bp.route('/save', methods=['POST'])
def save():
    user_id = request.form.get('id')
    rut_raw = request.form.get('rut')
    nombre = request.form.get('nombre', '').strip().upper()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password')
    rol_id = request.form.get('rol_id')
    estado_id = request.form.get('estado_id')

    if not rut_raw or not nombre or not email or not rol_id:
        flash("Complete los campos obligatorios", "warning")
        return redirect(url_for('users.index'))

    rut_plano = limpiar_rut(rut_raw)
    cur = g.db.cursor()
    
    try:
        if not user_id or user_id == "":
            # NUEVO USUARIO
            if not password:
                flash("La contraseña es obligatoria para nuevos usuarios", "warning")
                return redirect(url_for('users.index'))
            
            pass_hash = generate_password_hash(password)
            cur.execute("""
                INSERT INTO usuarios (rut, nombre, email, password, rol_id, activo) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (rut_plano, nombre, email, pass_hash, rol_id, estado_id))
            flash("Usuario creado exitosamente", "success")
        else:
            # EDITAR USUARIO
            if password:
                pass_hash = generate_password_hash(password)
                cur.execute("""
                    UPDATE usuarios SET nombre=%s, email=%s, password=%s, rol_id=%s, activo=%s 
                    WHERE id=%s
                """, (nombre, email, pass_hash, rol_id, estado_id, user_id))
            else:
                cur.execute("""
                    UPDATE usuarios SET nombre=%s, email=%s, rol_id=%s, activo=%s 
                    WHERE id=%s
                """, (nombre, email, rol_id, estado_id, user_id))
            flash("Usuario actualizado correctamente", "success")
        
        g.db.commit()
    except Exception as e:
        g.db.rollback()
        flash(f"Error al procesar usuario: {str(e)}", "danger")
    finally:
        cur.close()
    return redirect(url_for('users.index'))

@users_bp.route('/delete/<int:id>')
def delete(id):
    cur = g.db.cursor()
    try:
        # Validación: No permitir que un usuario se elimine a sí mismo si fuera necesario
        cur.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        g.db.commit()
        flash("Usuario eliminado del sistema", "warning")
    except:
        g.db.rollback()
        flash("No se puede eliminar: El usuario tiene registros vinculados", "danger")
    finally:
        cur.close()
    return redirect(url_for('users.index'))