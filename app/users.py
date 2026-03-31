from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g, session
from werkzeug.security import generate_password_hash

users_bp = Blueprint('users', __name__)

# FIREWALL DE SEGURIDAD GLOBAL
@users_bp.before_request
def check_auth():
    if 'user_id' not in session:
        flash('Acceso denegado: Por favor, inicie sesión.', 'danger')
        return redirect(url_for('main.index'))

@users_bp.route('/')
def index():
    cur = g.db.cursor()
    
    cur.execute("SELECT id, nombre FROM roles ORDER BY nombre ASC")
    roles_rows = cur.fetchall()
    
    roles_disponibles = []
    for r in roles_rows:
        if isinstance(r, dict):
            roles_disponibles.append({'id': r.get('id'), 'nombre': r.get('nombre')})
        else:
            roles_disponibles.append({'id': r[0], 'nombre': r[1]})
    
    cur.execute("SELECT id, rut, nombre, email, activo FROM usuarios ORDER BY nombre ASC")
    user_rows = cur.fetchall()
    
    cur.execute("SELECT usuario_id, rol_id FROM usuarios_roles")
    relaciones = cur.fetchall()
    
    roles_por_usuario = {}
    for rel in relaciones:
        if isinstance(rel, dict):
            u_id = rel.get('usuario_id')
            r_id = rel.get('rol_id')
        else:
            u_id = rel[0]
            r_id = rel[1]
            
        if u_id not in roles_por_usuario:
            roles_por_usuario[u_id] = []
        roles_por_usuario[u_id].append(str(r_id))
        
    usuarios = []
    for row in user_rows:
        if isinstance(row, dict):
            u_id = row.get('id')
            rut = row.get('rut')
            nombre = row.get('nombre')
            email = row.get('email')
            activo = row.get('activo')
        else:
            u_id = row[0]
            rut = row[1]
            nombre = row[2]
            email = row[3]
            activo = row[4]
        
        ids_roles = roles_por_usuario.get(u_id, [])
        nombres_roles = [r['nombre'] for r in roles_disponibles if str(r['id']) in ids_roles]
        texto_roles = ", ".join(nombres_roles) if nombres_roles else "Sin rol asignado"

        usuarios.append({
            'id': u_id,
            'rut': rut,
            'nombre': nombre,
            'email': email,
            'activo': activo,
            'roles_ids': ids_roles,
            'roles_texto': texto_roles
        })
        
    cur.close()
    return render_template('users.html', usuarios=usuarios, roles_disponibles=roles_disponibles)

@users_bp.route('/save', methods=['POST'])
def save():
    user_id = request.form.get('id')
    rut_limpio = request.form.get('rut', '').replace(".", "").replace("-", "").strip()
    nombre = request.form.get('nombre', '').strip().upper()
    email = request.form.get('email', '').strip().lower()
    password_raw = request.form.get('password', '').strip()
    activo = request.form.get('activo', 1)
    
    roles_seleccionados = request.form.getlist('roles[]')

    cur = g.db.cursor()
    try:
        if user_id: 
            if password_raw:  
                hashed_pw = generate_password_hash(password_raw)
                cur.execute("""
                    UPDATE usuarios 
                    SET nombre = %s, email = %s, password_hash = %s, activo = %s 
                    WHERE id = %s
                """, (nombre, email, hashed_pw, activo, user_id))
            else:  
                cur.execute("""
                    UPDATE usuarios 
                    SET nombre = %s, email = %s, activo = %s 
                    WHERE id = %s
                """, (nombre, email, activo, user_id))
                
            cur.execute("DELETE FROM usuarios_roles WHERE usuario_id = %s", (user_id,))
        
        else: 
            cur.execute("SELECT id FROM usuarios WHERE rut = %s", (rut_limpio,))
            if cur.fetchone():
                flash('El RUT ingresado ya pertenece a un usuario.', 'warning')
                return redirect(url_for('users.index'))
            
            hashed_pw = generate_password_hash(password_raw) if password_raw else generate_password_hash(rut_limpio)
                
            cur.execute("""
                INSERT INTO usuarios (rut, nombre, email, password_hash, activo) 
                VALUES (%s, %s, %s, %s, %s)
            """, (rut_limpio, nombre, email, hashed_pw, activo))
            user_id = cur.lastrowid

        if roles_seleccionados:
            for rol_id in roles_seleccionados:
                cur.execute("""
                    INSERT INTO usuarios_roles (usuario_id, rol_id) 
                    VALUES (%s, %s)
                """, (user_id, rol_id))
            
        g.db.commit()
        flash('Datos del usuario actualizados correctamente.', 'success')
    
    except Exception as e:
        if hasattr(g, 'db'): g.db.rollback()
        flash(f'Error al procesar la solicitud: {str(e)}', 'danger')
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
        flash('Usuario eliminado correctamente.', 'success')
    except Exception:
        if hasattr(g, 'db'): g.db.rollback()
        flash('No se puede eliminar: el usuario tiene registros asociados.', 'danger')
    finally:
        cur.close()
    return redirect(url_for('users.index'))

@users_bp.route('/verificar_rut/<rut>')
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
    cur.execute("SELECT id FROM usuarios WHERE rut = %s", (rut_busqueda[:-1] + dv_ingresado,))
    existe = cur.fetchone()
    cur.close()
    
    if existe:
        return jsonify({'status': 'duplicado', 'message': 'Este RUT ya se encuentra registrado en el sistema.'})
        
    return jsonify({'status': 'ok'})