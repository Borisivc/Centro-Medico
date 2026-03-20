from flask import Blueprint, render_template, g, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash

users_bp = Blueprint('users', __name__)

@users_bp.route('/usuarios')
def index():
    cur = g.db.cursor()
    
    # Consulta robusta: Traemos los datos básicos del usuario y su rol
    # Si 'rol_id' no está en 'usuarios', lo buscamos en la tabla 'usuarios_roles'
    try:
        cur.execute("""
            SELECT 
                u.id, 
                u.nombre, 
                u.email, 
                u.activo as estado_id,
                CASE WHEN u.activo = 1 THEN 'ACTIVO' ELSE 'INACTIVO' END as estado_nombre,
                r.id as rol_id,
                r.nombre as rol_nombre
            FROM usuarios u
            LEFT JOIN usuarios_roles ur ON u.id = ur.usuario_id
            LEFT JOIN roles r ON ur.rol_id = r.id
        """)
        usuarios = cur.fetchall()
    except Exception:
        # Fallback si tu estructura es directa (rol_id en tabla usuarios)
        cur.execute("""
            SELECT 
                u.id, u.nombre, u.email, u.activo as estado_id,
                CASE WHEN u.activo = 1 THEN 'ACTIVO' ELSE 'INACTIVO' END as estado_nombre,
                u.rol_id, r.nombre as rol_nombre
            FROM usuarios u
            LEFT JOIN roles r ON u.rol_id = r.id
        """)
        usuarios = cur.fetchall()

    # Traemos los roles para los selects del modal
    cur.execute("SELECT id, nombre FROM roles")
    roles = cur.fetchall()
    
    # Listado de estados para el modal
    estados = [
        {'id': 1, 'nombre': 'ACTIVO'},
        {'id': 0, 'nombre': 'INACTIVO'}
    ]
    
    cur.close()
    return render_template('users.html', usuarios=usuarios, roles=roles, estados=estados)

@users_bp.route('/usuarios/save', methods=['POST'])
def save():
    user_id = request.form.get('user_id')
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    rol_id = request.form.get('rol_id')
    activo = request.form.get('activo')
    password = request.form.get('password')

    cur = g.db.cursor()
    try:
        if user_id:
            # ACTUALIZACIÓN
            if password:
                hash_pass = generate_password_hash(password)
                cur.execute("""
                    UPDATE usuarios SET nombre=%s, email=%s, activo=%s, password_hash=%s 
                    WHERE id=%s
                """, (nombre, email, activo, hash_pass, user_id))
            else:
                cur.execute("""
                    UPDATE usuarios SET nombre=%s, email=%s, activo=%s 
                    WHERE id=%s
                """, (nombre, email, activo, user_id))
            
            # Actualizar Rol en tabla intermedia
            cur.execute("DELETE FROM usuarios_roles WHERE usuario_id=%s", (user_id,))
            cur.execute("INSERT INTO usuarios_roles (usuario_id, rol_id) VALUES (%s, %s)", (user_id, rol_id))
        else:
            # INSERCIÓN NUEVA
            hash_pass = generate_password_hash(password)
            cur.execute("""
                INSERT INTO usuarios (nombre, email, password_hash, activo) 
                VALUES (%s, %s, %s, %s)
            """, (nombre, email, hash_pass, activo))
            new_id = cur.lastrowid
            cur.execute("INSERT INTO usuarios_roles (usuario_id, rol_id) VALUES (%s, %s)", (new_id, rol_id))
        
        g.db.commit()
        flash('Usuario procesado correctamente', 'success')
    except Exception as e:
        g.db.rollback()
        flash(f'Error: {str(e)}', 'danger')
    finally:
        cur.close()
    
    return redirect(url_for('users.index'))