from flask import Blueprint, render_template, g, request, redirect, url_for, flash

# Definición limpia del Blueprint
availability_bp = Blueprint('availability', __name__)

@availability_bp.route('/')
def index():
    cur = g.db.cursor()
    # Consulta de disponibilidad
    cur.execute("""
        SELECT d.id, p.nombre as profesional, d.dia_semana, d.hora_inicio, d.hora_fin
        FROM disponibilidad d
        JOIN profesionales p ON d.profesional_id = p.id
        ORDER BY FIELD(d.dia_semana, 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo')
    """)
    horarios = cur.fetchall()
    
    cur.execute("SELECT id, nombre FROM profesionales WHERE activo = 1")
    profs = cur.fetchall()
    cur.close()
    
    return render_template('availability.html', horarios=horarios, profesionales=profs)

@availability_bp.route('/save', methods=['POST'])
def save():
    # Lógica de guardado...
    flash('Horario guardado correctamente', 'success')
    return redirect(url_for('availability.index'))