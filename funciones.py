# funciones.py
import re
from datos import obtener_datos_iniciales

# Instancias compartidas
socios, canchas, reservas, pagos = obtener_datos_iniciales()


def validar_fecha(fecha_str):
    """Valida el formato DD/MM/AAAA."""
    patron = r"^\d{2}/\d{2}/\d{4}$"
    return bool(re.match(patron, fecha_str.strip()))


def socio_nombre(dni):
    for s in socios:
        if s["dni"] == dni:
            return f"{s['nombre']} {s['apellido']}"
    return dni


def minutos(hora):
    try:
        h, m = map(int, hora.split(":"))
        return h * 60 + m
    except ValueError:
        return None


def disponible(cancha, fecha, inicio, fin, excluir=None):
    a = minutos(inicio)
    b = minutos(fin)

    if a is None or b is None or b <= a:
        return False

    for r in reservas:
        if r["numero"] == excluir:
            continue
        if (
            r["cancha"] == cancha
            and r["fecha"] == fecha
            and r.get("estado") == "Reservada"
        ):
            x = minutos(r["inicio"])
            y = minutos(r["fin"])
            if a < y and x < b:
                return False
    return True


def combo_socios():
    return [f"{s['dni']} - {s['nombre']} {s['apellido']}" for s in socios]


def combo_canchas():
    return [f"{c['numero']} - {c['tipo']}" for c in canchas]