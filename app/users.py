from flask import Blueprint, render_template, g, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash

users_bp = Blueprint('users', __name__)

@users_bp.route('/')
def index():
    cur = g.db.cursor()
    try:
        cur.execute("""
            SELECT u.id, u.nombre, u.email, u.activo,
                   GROUP_CONCAT(r.nombre SEPARATOR ', ') as roles_nombres,
                   GROUP_CONCAT(r.id SEPARATOR ',') as roles_ids
            FROM usuarios u
            LEFT JOIN usuarios_roles ur ON u.id = ur.usuario_id
            LEFT JOIN roles r ON ur.rol_id = r.id
            GROUP BY u.id
            ORDER BY u.nombre ASC
        """)
        usuarios = cur.fetchall()
        cur.execute("SELECT id, nombre FROM roles ORDER BY nombre ASC")
        roles = cur.fetchall()
    except Exception as e:
        print(f"Error Index Usuarios: {e}")
        usuarios, roles = [], []
    finally:
        cur.close()
    return render_template('users.html', usuarios=usuarios, roles=roles)

@users_bp.route('/save', methods=['POST'])
def save():
    user_id = request.form.get('user_id')
    nombre = request.form.get('nombre')
    email = request.form.get('email', '').lower().strip()
    rol_id = request.form.get('rol_id')
    password = request.form.get('password')
    activo = request.form.get('activo', 1)

    cur = g.db.cursor()
    try:
        if user_id:
            if password:
                pw_hash = generate_password_hash(password)
                cur.execute("UPDATE usuarios SET nombre=%s, email=%s, activo=%s, password_hash=%s WHERE id=%s", 
                            (nombre, email, activo, pw_hash, user_id))
            else:
                cur.execute("UPDATE usuarios SET nombre=%s, email=%s, activo=%s WHERE id=%s", 
                            (nombre, email, activo, user_id))
            cur.execute("DELETE FROM usuarios_roles WHERE usuario_id = %s", (user_id,))
            cur.execute("INSERT INTO usuarios_roles (usuario_id, rol_id) VALUES (%s, %s)", (user_id, rol_id))
            flash('Usuario actualizado correctamente', 'success')
        else:
            pw_hash = generate_password_hash(password)
            cur.execute("INSERT INTO usuarios (nombre, email, activo, password_hash) VALUES (%s, %s, %s, %s)", 
                        (nombre, email, activo, pw_hash))
            nuevo_id = cur.lastrowid
            cur.execute("INSERT INTO usuarios_roles (usuario_id, rol_id) VALUES (%s, %s)", (nuevo_id, rol_id))
            flash('Usuario creado con éxito', 'success')
        g.db.commit()
    except Exception as e:
        g.db.rollback()
        flash(f'Error: {str(e)}', 'danger')
    finally:
        cur.close()
    return redirect(url_for('users.index'))

@users_bp.route('/delete/<int:id>')
def delete(id):
    cur = g.db.cursor()
    try:
        cur.execute("DELETE FROM usuarios_roles WHERE usuario_id = %s", (id,))
        cur.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        g.db.commit()
        flash('Usuario eliminado', 'warning')
    except Exception as e:
        g.db.rollback()
        flash(f'Error: {str(e)}', 'danger')
    finally:
        cur.close()
    return redirect(url_for('users.index'))