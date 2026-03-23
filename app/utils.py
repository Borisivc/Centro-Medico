import re

def limpiar_rut(rut):
    """Deja el RUT en formato 12345678K para la base de datos."""
    if not rut: return ""
    return re.sub(r'[^0-9Kk]', '', str(rut)).upper()

def validar_rut(rut):
    """Algoritmo Módulo 11 para validar RUT Chileno."""
    rut = limpiar_rut(rut)
    if len(rut) < 8: return False
    cuerpo = rut[:-1]
    dv = rut[-1]
    try:
        suma = 0
        multiplo = 2
        for c in reversed(cuerpo):
            suma += int(c) * multiplo
            multiplo = multiplo + 1 if multiplo < 7 else 2
        dv_esperado = 11 - (suma % 11)
        dv_real = "0" if dv_esperado == 11 else "K" if dv_esperado == 10 else str(dv_esperado)
        return dv_real == dv
    except:
        return False

def formatear_rut(rut):
    """Devuelve formato XX.XXX.XXX-X para la interfaz."""
    rut = limpiar_rut(rut)
    if len(rut) < 2: return rut
    cuerpo = rut[:-1]
    dv = rut[-1]
    cuerpo_puntos = "{:,}".format(int(cuerpo)).replace(",", ".")
    return f"{cuerpo_puntos}-{dv}"