# funciones.py
"""Lógica de negocio de Punto Cancha, conectada a MySQL.

La interfaz (interfaz.py) llama a estas funciones; ninguna lista en memoria
guarda datos: todo se lee y se escribe en la base `punto_cancha`.
"""
import re
from datetime import date, datetime, timedelta
from decimal import Decimal

from db import consultar, ejecutar, transaccion, ErrorBD

# ---------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------
MODOS_PAGO = ["Efectivo", "Transferencia", "Tarjeta"]
pagos = MODOS_PAGO  # nombre que usa la interfaz

# La interfaz muestra "Fútbol 5" (con tilde); la base guarda "Futbol 5".
TIPO_UI_A_DB = {"Fútbol 5": "Futbol 5", "Fútbol 7": "Futbol 7"}
TIPO_DB_A_UI = {v: k for k, v in TIPO_UI_A_DB.items()}

# La tabla cancha exige capacidad (NOT NULL): se deduce del tipo.
CAPACIDAD = {"Futbol 5": 10, "Futbol 7": 14}

# La tabla reserva exige total (NOT NULL): precio por hora según el tipo.
# >>> AJUSTAR estos valores a los precios reales del club <<<
PRECIO_HORA = {"Futbol 5": Decimal("15000"), "Futbol 7": Decimal("22000")}


# ---------------------------------------------------------------
# Validaciones y conversiones de formato
# ---------------------------------------------------------------
def validar_fecha(fecha_str):
    """Valida que sea una fecha real en formato DD/MM/AAAA."""
    try:
        datetime.strptime(fecha_str.strip(), "%d/%m/%Y")
        return True
    except ValueError:
        return False


def validar_dni(dni):
    """El DDL exige 7 u 8 dígitos."""
    return bool(re.fullmatch(r"\d{7,8}", dni.strip()))


def fecha_a_sql(fecha_ui):
    """'20/09/2026' -> '2026-09-20'."""
    return datetime.strptime(fecha_ui.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")


def fecha_a_ui(valor):
    """date -> '20/09/2026'."""
    if isinstance(valor, (date, datetime)):
        return valor.strftime("%d/%m/%Y")
    return str(valor)


def hora_a_ui(valor):
    """timedelta (como devuelve MySQL para TIME) -> 'HH:MM'."""
    if isinstance(valor, timedelta):
        total = int(valor.total_seconds())
        return f"{total // 3600:02d}:{(total % 3600) // 60:02d}"
    return str(valor)[:5]


def minutos(hora):
    try:
        h, m = map(int, hora.split(":"))
        if not (0 <= h <= 23 and 0 <= m <= 59):
            return None
        return h * 60 + m
    except (ValueError, AttributeError):
        return None


# ---------------------------------------------------------------
# SOCIOS
# ---------------------------------------------------------------
def _socio_ui(f):
    return {
        "dni": f["dni"],
        "nombre": f["nombre"],
        "apellido": f["apellido"],
        "telefono": f["telefono"] or "",
        "email": f["email"] or "",
    }


def listar_socios():
    filas = consultar(
        "SELECT dni, nombre, apellido, telefono, email FROM socio "
        "ORDER BY apellido, nombre"
    )
    return [_socio_ui(f) for f in filas]


def obtener_socio(dni):
    filas = consultar(
        "SELECT dni, nombre, apellido, telefono, email FROM socio WHERE dni = %s",
        (dni,),
    )
    return _socio_ui(filas[0]) if filas else None


def crear_socio(dni, nombre, apellido, telefono, email):
    ejecutar(
        "INSERT INTO socio (dni, nombre, apellido, telefono, email) "
        "VALUES (%s, %s, %s, %s, %s)",
        (dni, nombre, apellido, telefono or None, email or None),
    )


def modificar_socio(dni_actual, dni, nombre, apellido, telefono, email):
    ejecutar(
        "UPDATE socio SET dni=%s, nombre=%s, apellido=%s, telefono=%s, email=%s "
        "WHERE dni=%s",
        (dni, nombre, apellido, telefono or None, email or None, dni_actual),
    )


def eliminar_socio(dni):
    """Falla con ErrorBD si el socio tiene reservas (FK ON DELETE RESTRICT)."""
    ejecutar("DELETE FROM socio WHERE dni = %s", (dni,))


def socio_nombre(dni):
    s = obtener_socio(dni)
    return f"{s['nombre']} {s['apellido']}" if s else dni


def combo_socios():
    return [f"{s['dni']} - {s['nombre']} {s['apellido']}" for s in listar_socios()]


# ---------------------------------------------------------------
# CANCHAS  (en la interfaz "numero" == id_cancha)
# ---------------------------------------------------------------
def _cancha_ui(f):
    return {
        "numero": str(f["id_cancha"]),
        "tipo": TIPO_DB_A_UI.get(f["tipo"], f["tipo"]),
        "estado": f["estado"],
    }


def listar_canchas():
    filas = consultar(
        "SELECT id_cancha, tipo, estado FROM cancha ORDER BY id_cancha"
    )
    return [_cancha_ui(f) for f in filas]


def crear_cancha(numero, tipo_ui, estado):
    tipo = TIPO_UI_A_DB[tipo_ui]
    ejecutar(
        "INSERT INTO cancha (id_cancha, nombre, tipo, capacidad, estado) "
        "VALUES (%s, %s, %s, %s, %s)",
        (int(numero), f"Cancha {int(numero)}", tipo, CAPACIDAD[tipo], estado),
    )


def modificar_cancha(numero_actual, numero, tipo_ui, estado):
    tipo = TIPO_UI_A_DB[tipo_ui]
    ejecutar(
        "UPDATE cancha SET id_cancha=%s, nombre=%s, tipo=%s, capacidad=%s, estado=%s "
        "WHERE id_cancha=%s",
        (
            int(numero),
            f"Cancha {int(numero)}",
            tipo,
            CAPACIDAD[tipo],
            estado,
            int(numero_actual),
        ),
    )


def eliminar_cancha(numero):
    """Falla con ErrorBD si la cancha tiene reservas (FK ON DELETE RESTRICT)."""
    ejecutar("DELETE FROM cancha WHERE id_cancha = %s", (int(numero),))


def combo_canchas():
    return [f"{c['numero']} - {c['tipo']}" for c in listar_canchas()]


# ---------------------------------------------------------------
# RESERVAS
# ---------------------------------------------------------------
_SQL_RESERVAS = """
    SELECT r.id_reserva, s.dni, CONCAT(s.nombre, ' ', s.apellido) AS socio,
           r.id_cancha, r.fecha, r.hora_inicio, r.hora_fin, r.total,
           r.estado, p.medio_pago
    FROM reserva r
    JOIN socio s ON s.id_socio = r.id_socio
    LEFT JOIN pago p ON p.id_reserva = r.id_reserva
"""


def _reserva_ui(f):
    return {
        "numero": f["id_reserva"],
        "dni": f["dni"],
        "socio": f["socio"],
        "cancha": str(f["id_cancha"]),
        "fecha": fecha_a_ui(f["fecha"]),
        "inicio": hora_a_ui(f["hora_inicio"]),
        "fin": hora_a_ui(f["hora_fin"]),
        "total": f["total"],
        "pago": f["medio_pago"] or "Pendiente",
        "estado": f["estado"],
    }


def listar_reservas(dni=None, cancha=None, fecha=None):
    """Lista reservas. Los filtros son opcionales.

    dni: coincidencia parcial; cancha: número; fecha: 'DD/MM/AAAA'.
    """
    sql = _SQL_RESERVAS + " WHERE 1=1"
    params = []
    if dni:
        sql += " AND s.dni LIKE %s"
        params.append(f"%{dni}%")
    if cancha:
        sql += " AND r.id_cancha = %s"
        params.append(int(cancha))
    if fecha:
        sql += " AND r.fecha = %s"
        params.append(fecha_a_sql(fecha))
    sql += " ORDER BY r.fecha, r.hora_inicio, r.id_reserva"
    return [_reserva_ui(f) for f in consultar(sql, tuple(params))]


def obtener_reserva(numero):
    filas = consultar(_SQL_RESERVAS + " WHERE r.id_reserva = %s", (int(numero),))
    return _reserva_ui(filas[0]) if filas else None


def disponible(cancha, fecha, inicio, fin, excluir=None):
    """True si la cancha está habilitada y sin reservas vigentes superpuestas."""
    a = minutos(inicio)
    b = minutos(fin)
    if a is None or b is None or b <= a or not validar_fecha(fecha):
        return False

    estado = consultar(
        "SELECT estado FROM cancha WHERE id_cancha = %s", (int(cancha),)
    )
    if not estado or estado[0]["estado"] != "Disponible":
        return False

    # Misma regla que los triggers del DDL: inicio_nuevo < fin_existente
    # y fin_nuevo > inicio_existente (reservas contiguas están permitidas).
    filas = consultar(
        "SELECT COUNT(*) AS n FROM reserva "
        "WHERE id_cancha = %s AND fecha = %s AND estado = 'Reservada' "
        "AND id_reserva <> %s AND %s < hora_fin AND %s > hora_inicio",
        (int(cancha), fecha_a_sql(fecha), excluir or 0, inicio, fin),
    )
    return filas[0]["n"] == 0


def calcular_total(cur, id_cancha, inicio, fin):
    cur.execute("SELECT tipo FROM cancha WHERE id_cancha = %s", (id_cancha,))
    fila = cur.fetchone()
    if not fila:
        raise ErrorBD("La cancha indicada no existe.")
    horas = Decimal(minutos(fin) - minutos(inicio)) / Decimal(60)
    return (PRECIO_HORA[fila["tipo"]] * horas).quantize(Decimal("0.01"))


def _id_socio(cur, dni):
    cur.execute("SELECT id_socio FROM socio WHERE dni = %s", (dni,))
    fila = cur.fetchone()
    if not fila:
        raise ErrorBD("El socio indicado no existe.")
    return fila["id_socio"]


def crear_reserva(dni, cancha, fecha, inicio, fin, medio_pago):
    """Inserta la reserva y su pago en una sola transacción. Devuelve el N°."""
    with transaccion() as cur:
        id_socio = _id_socio(cur, dni)
        total = calcular_total(cur, int(cancha), inicio, fin)
        cur.execute(
            "INSERT INTO reserva (id_socio, id_cancha, fecha, hora_inicio, hora_fin, total) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (id_socio, int(cancha), fecha_a_sql(fecha), inicio, fin, total),
        )
        id_reserva = cur.lastrowid
        cur.execute(
            "INSERT INTO pago (id_reserva, monto, fecha_pago, medio_pago) "
            "VALUES (%s, %s, %s, %s)",
            (id_reserva, total, date.today(), medio_pago),
        )
        return id_reserva


def modificar_reserva(numero, dni, cancha, fecha, inicio, fin, medio_pago):
    with transaccion() as cur:
        id_socio = _id_socio(cur, dni)
        total = calcular_total(cur, int(cancha), inicio, fin)
        cur.execute(
            "UPDATE reserva SET id_socio=%s, id_cancha=%s, fecha=%s, "
            "hora_inicio=%s, hora_fin=%s, total=%s WHERE id_reserva=%s",
            (id_socio, int(cancha), fecha_a_sql(fecha), inicio, fin, total, int(numero)),
        )
        cur.execute("SELECT id_pago FROM pago WHERE id_reserva = %s", (int(numero),))
        if cur.fetchone():
            cur.execute(
                "UPDATE pago SET monto=%s, medio_pago=%s WHERE id_reserva=%s",
                (total, medio_pago, int(numero)),
            )
        else:
            cur.execute(
                "INSERT INTO pago (id_reserva, monto, fecha_pago, medio_pago) "
                "VALUES (%s, %s, %s, %s)",
                (int(numero), total, date.today(), medio_pago),
            )


def cancelar_reserva(numero):
    """Baja lógica: nunca se borra la reserva (ver DDL)."""
    ejecutar(
        "UPDATE reserva SET estado = 'Cancelada' WHERE id_reserva = %s",
        (int(numero),),
    )


def reservas_por_cancha():
    """Cantidad de reservas vigentes por cancha (RF10)."""
    filas = consultar(
        "SELECT c.id_cancha, c.tipo, c.estado, COUNT(r.id_reserva) AS cantidad "
        "FROM cancha c "
        "LEFT JOIN reserva r ON r.id_cancha = c.id_cancha AND r.estado = 'Reservada' "
        "GROUP BY c.id_cancha, c.tipo, c.estado ORDER BY c.id_cancha"
    )
    return [
        {
            "numero": str(f["id_cancha"]),
            "tipo": TIPO_DB_A_UI.get(f["tipo"], f["tipo"]),
            "estado": f["estado"],
            "cantidad": f["cantidad"],
        }
        for f in filas
    ]


# ---------------------------------------------------------------
# CONSULTAS CON JOIN (pantalla "Consultas con JOIN")
# Cada reporte guarda su SQL para ejecutarlo y para mostrarlo en la interfaz.
# ---------------------------------------------------------------
SQL_DETALLE_RESERVAS = """
SELECT r.id_reserva,
       CONCAT(s.apellido, ', ', s.nombre) AS socio,
       s.dni,
       c.nombre AS cancha,
       c.tipo,
       r.fecha, r.hora_inicio, r.hora_fin,
       r.total,
       r.estado,
       COALESCE(p.medio_pago, 'Pendiente') AS pago
FROM reserva r
JOIN socio  s ON s.id_socio  = r.id_socio
JOIN cancha c ON c.id_cancha = r.id_cancha
LEFT JOIN pago p ON p.id_reserva = r.id_reserva
ORDER BY r.fecha, r.hora_inicio, r.id_reserva
""".strip()

SQL_PENDIENTES_PAGO = """
SELECT r.id_reserva,
       CONCAT(s.apellido, ', ', s.nombre) AS socio,
       s.telefono,
       c.nombre AS cancha,
       r.fecha, r.hora_inicio, r.hora_fin,
       r.total
FROM reserva r
JOIN socio  s ON s.id_socio  = r.id_socio
JOIN cancha c ON c.id_cancha = r.id_cancha
LEFT JOIN pago p ON p.id_reserva = r.id_reserva
WHERE r.estado = 'Reservada'
  AND p.id_pago IS NULL
ORDER BY r.fecha, r.hora_inicio
""".strip()

SQL_RESUMEN_SOCIOS = """
SELECT s.dni,
       CONCAT(s.apellido, ', ', s.nombre) AS socio,
       COUNT(r.id_reserva)  AS reservas_vigentes,
       COALESCE(SUM(p.monto), 0) AS total_pagado
FROM socio s
LEFT JOIN reserva r ON r.id_socio = s.id_socio AND r.estado = 'Reservada'
LEFT JOIN pago    p ON p.id_reserva = r.id_reserva
GROUP BY s.id_socio, s.dni, s.apellido, s.nombre
ORDER BY total_pagado DESC, socio
""".strip()


def _dinero(valor):
    return f"${Decimal(valor):.2f}"


def _fila_detalle(f):
    return (
        f["id_reserva"],
        f["socio"],
        f["dni"],
        f["cancha"],
        TIPO_DB_A_UI.get(f["tipo"], f["tipo"]),
        fecha_a_ui(f["fecha"]),
        f"{hora_a_ui(f['hora_inicio'])} - {hora_a_ui(f['hora_fin'])}",
        _dinero(f["total"]),
        f["pago"],
        f["estado"],
    )


def _fila_pendiente(f):
    return (
        f["id_reserva"],
        f["socio"],
        f["telefono"] or "",
        f["cancha"],
        fecha_a_ui(f["fecha"]),
        f"{hora_a_ui(f['hora_inicio'])} - {hora_a_ui(f['hora_fin'])}",
        _dinero(f["total"]),
    )


def _fila_resumen(f):
    return (
        f["dni"],
        f["socio"],
        f["reservas_vigentes"],
        _dinero(f["total_pagado"]),
    )


REPORTES = {
    "detalle": {
        "titulo": "Detalle de reservas",
        "descripcion": "JOIN de reserva + socio + cancha + pago (LEFT JOIN).",
        "sql": SQL_DETALLE_RESERVAS,
        "fila": _fila_detalle,
        "columnas": [
            ("n", "N°", 45),
            ("socio", "Socio", 170),
            ("dni", "DNI", 90),
            ("cancha", "Cancha", 80),
            ("tipo", "Tipo", 80),
            ("fecha", "Fecha", 90),
            ("horario", "Horario", 110),
            ("total", "Total", 90),
            ("pago", "Pago", 100),
            ("estado", "Estado", 90),
        ],
    },
    "pendientes": {
        "titulo": "Pendientes de pago",
        "descripcion": "Reservas vigentes sin pago: LEFT JOIN con pago y filtro IS NULL.",
        "sql": SQL_PENDIENTES_PAGO,
        "fila": _fila_pendiente,
        "columnas": [
            ("n", "N°", 45),
            ("socio", "Socio", 190),
            ("tel", "Teléfono", 110),
            ("cancha", "Cancha", 90),
            ("fecha", "Fecha", 100),
            ("horario", "Horario", 120),
            ("total", "Total a cobrar", 120),
        ],
    },
    "socios": {
        "titulo": "Resumen por socio",
        "descripcion": "JOIN con GROUP BY: reservas vigentes y total pagado por cada socio.",
        "sql": SQL_RESUMEN_SOCIOS,
        "fila": _fila_resumen,
        "columnas": [
            ("dni", "DNI", 110),
            ("socio", "Socio", 220),
            ("cant", "Reservas vigentes", 150),
            ("pagado", "Total pagado", 140),
        ],
    },
}


def ejecutar_reporte(clave):
    """Ejecuta el SQL del reporte y devuelve filas listas para mostrar."""
    rep = REPORTES[clave]
    return [rep["fila"](f) for f in consultar(rep["sql"])]
