import os
from datetime import datetime
from dotenv import load_dotenv
from app import create_app

# Cargar .env antes de importar la app
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = create_app()

# ==========================================================
# REGISTRO DE FILTROS PERSONALIZADOS PARA JINJA2
# ==========================================================

@app.template_filter('formatear_fecha')
def formatear_fecha(value):
    """Convierte una fecha YYYY-MM-DD al formato visual DD-MM-YYYY"""
    if not value:
        return ""
    try:
        # Si el valor viene como string desde la base de datos
        if isinstance(value, str):
            fecha_obj = datetime.strptime(value, '%Y-%m-%d')
        else:
            fecha_obj = value
        return fecha_obj.strftime('%d-%m-%Y')
    except Exception:
        return value

@app.template_filter('formatear_rut')
def formatear_rut(rut):
    """Formatea un RUT string a formato X.XXX.XXX-X"""
    if not rut:
        return ""
    # Limpiar caracteres previos por si acaso
    rut = rut.replace(".", "").replace("-", "")
    if len(rut) < 2:
        return rut
    cuerpo = rut[:-1]
    dv = rut[-1]
    
    cuerpo_formateado = ""
    while len(cuerpo) > 3:
        cuerpo_formateado = "." + cuerpo[-3:] + cuerpo_formateado
        cuerpo = cuerpo[:-3]
    return cuerpo + cuerpo_formateado + "-" + dv

# ==========================================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )