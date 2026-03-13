def format_rut(rut):

    if not rut:
        return ""

    rut = rut.replace(".", "").replace("-", "")

    cuerpo = rut[:-1]
    dv = rut[-1]

    cuerpo = "{:,}".format(int(cuerpo)).replace(",", ".")

    return f"{cuerpo}-{dv}"


def format_date(fecha):

    if not fecha:
        return ""

    return fecha.strftime("%d-%m-%Y")