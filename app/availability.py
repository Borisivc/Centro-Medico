from flask import Blueprint, render_template, g, request, redirect, url_for, flash, session

availability_bp = Blueprint('availability', __name__)

@availability_bp.route('/')
def index():
    if not session.get('user_id'):
        return redirect(url_for('main.index'))
    
    cur = g.db.cursor()
    try:
        # Consulta de disponibilidad vinculada a profesionales
        cur.execute("""
            SELECT d.id, p.nombre, p.apellido, d.dia_semana, d.hora_inicio, d.hora_fin
            FROM disponibilidad d
            JOIN profesionales p ON d.profesional_id = p.id
            ORDER BY p.nombre ASC, d.id ASC
        """)
        disponibilidades = cur.fetchall()
        
        cur.execute("SELECT id, nombre, apellido FROM profesionales WHERE estado_id = 1")
        profesionales = cur.fetchall()
    except Exception as e:
        print(f"Error Disponibilidad: {e}")
        disponibilidades, profesionales = [], []
    finally:
        cur.close()
        
    return render_template('availability.html', 
                           disponibilidades=disponibilidades, 
                           profesionales=profesionales)

@availability_bp.route('/save', methods=['POST'])
def save():
    prof_id = request.form.get('profesional_id')
    dia = request.form.get('dia_semana')
    inicio = request.form.get('hora_inicio')
    fin = request.form.get('hora_fin')

    if not prof_id or not dia or not inicio or not fin:
        flash("Todos los campos son obligatorios para la disponibilidad.", "danger")
        return redirect(url_for('availability.index'))

    cur = g.db.cursor()
    try:
        cur.execute("""
            INSERT INTO disponibilidad (profesional_id, dia_semana, hora_inicio, hora_fin)
            VALUES (%s, %s, %s, %s)
        """, (prof_id, dia, inicio, fin))
        g.db.commit()
        flash("Disponibilidad horaria registrada.", "success")
    except Exception as e:
        g.db.rollback()
        flash(f"Error: {str(e)}", "danger")
    finally:
        cur.close()
        
    return redirect(url_for('availability.index'))