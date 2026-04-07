from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from datetime import datetime

# Definición del Blueprint para el módulo clínico
clinical_bp = Blueprint('clinical', __name__)

# ==============================================================================
# 🛡️ CANDADO DE SEGURIDAD (FIREWALL DEL BLUEPRINT)
# ==============================================================================
@clinical_bp.before_request
def proteger_rutas_clinicas():
    """
    Esta función se ejecuta automáticamente ANTES de cualquier ruta dentro de este archivo.
    Si el usuario no tiene una sesión activa, lo patea de vuelta al inicio.
    ¡Garantiza que nadie entre por URL directa!
    """
    if 'user_id' not in session:
        flash('Acceso restringido. Debe iniciar sesión de forma segura para continuar.', 'danger')
        return redirect(url_for('main.index'))

# ==============================================================================
# 1. SALA DE ESPERA (Pacientes del día)
# ==============================================================================
@clinical_bp.route('/')
def index():
    # Ya no necesitamos validar la sesión aquí, el candado de arriba lo hace por nosotros.
    
    # Aquí iría tu consulta a la base de datos para obtener las citas de hoy
    citas_hoy = [] 
    
    return render_template('clinical.html', citas_hoy=citas_hoy)

# ==============================================================================
# 2. ESPACIO DE TRABAJO MÉDICO (Atención)
# ==============================================================================
@clinical_bp.route('/workspace/<int:agenda_id>')
def workspace(agenda_id):
    # Aquí irían tus consultas a la base de datos para:
    # 1. Obtener los datos de la cita actual
    # 2. Obtener el historial previo del paciente
    # 3. Obtener los documentos adjuntos
    cita = {}
    historial = []
    adjuntos = {}
    now = datetime.now()
    
    return render_template('clinical_workspace.html', 
                           cita=cita, 
                           historial=historial, 
                           adjuntos=adjuntos, 
                           now=now)

# ==============================================================================
# 3. GUARDAR ATENCIÓN MÉDICA
# ==============================================================================
@clinical_bp.route('/save', methods=['POST'])
def save():
    if request.method == 'POST':
        # Aquí recibes los datos del formulario:
        # motivo = request.form.get('motivo_consulta')
        # diagnostico = request.form.get('diagnostico')
        # etc...
        # Y haces el INSERT a tu base de datos
        
        flash('Atención médica guardada correctamente', 'success')
        return redirect(url_for('clinical.index'))

# ==============================================================================
# 4. BUSCADOR DE HISTORIAL MAESTRO
# ==============================================================================
@clinical_bp.route('/historial')
def historial():
    # Capturar el parámetro de búsqueda ('q' viene del input del formulario HTML)
    q = request.args.get('q', '').strip()
    
    # Variables iniciales vacías para enviar a la vista
    paciente = None
    historial_datos = []
    adjuntos_datos = {}

    if q:
        # =========================================================
        # AQUÍ DEBES CONECTAR TU LÓGICA DE BASE DE DATOS REAL
        # =========================================================
        # Ejemplo:
        # cursor.execute("SELECT * FROM pacientes WHERE rut LIKE %s", (f"%{q}%",))
        # paciente = cursor.fetchone()
        pass

    # Renderizar la vista
    return render_template('clinical_history.html',
                           paciente=paciente,
                           historial=historial_datos,
                           adjuntos=adjuntos_datos)