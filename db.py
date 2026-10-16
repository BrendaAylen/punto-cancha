# db.py
"""Conexión a la base de datos MySQL/MariaDB de Punto Cancha.

Los datos de conexión se leen de variables de entorno (así la contraseña
no queda escrita en el código ni se sube a GitHub). Si no están definidas,
se usan los valores por defecto de abajo: ajustá PC_DB_PASSWORD.
"""
import os
from contextlib import contextmanager

import mysql.connector
from mysql.connector import Error as MySQLError

CONFIG = {
    "host": os.getenv("PC_DB_HOST", "localhost"),
    "port": int(os.getenv("PC_DB_PORT", "3306")),
    "user": os.getenv("PC_DB_USER", "root"),
    "password": os.getenv("PC_DB_PASSWORD", ""),
    "database": os.getenv("PC_DB_NAME", "punto_cancha"),
    "charset": "utf8mb4",
}


class ErrorBD(Exception):
    """Error de base de datos con un mensaje apto para mostrar al usuario."""


def _traducir(e):
    """Convierte un error de MySQL en un mensaje entendible."""
    msg = getattr(e, "msg", None) or str(e)
    errno = getattr(e, "errno", None)
    sqlstate = getattr(e, "sqlstate", None)

    if sqlstate == "45000":  # SIGNAL de los triggers del DDL
        return msg
    if errno == 1062:
        if "dni" in msg.lower():
            return "Ya existe un socio con ese DNI."
        if "email" in msg.lower():
            return "Ya existe un socio con ese email."
        if "nombre" in msg.lower():
            return "Ya existe una cancha con ese nombre."
        if "PRIMARY" in msg:
            return "Ya existe un registro con ese número."
        if "pago_reserva" in msg:
            return "Esa reserva ya tiene un pago registrado."
        return "Ya existe un registro con esos datos."
    if errno == 1451:
        return (
            "No se puede eliminar: el registro tiene reservas asociadas. "
            "Si es una reserva, cancélela; si es una cancha, márquela como Inactiva."
        )
    if errno == 1452:
        return "El socio o la cancha indicados no existen."
    if errno in (1044, 1142, 1143, 1370):  # permisos insuficientes (roles)
        return "Su usuario de base de datos no tiene permiso para realizar esta operación."
    if errno in (3819, 4025):  # CHECK constraint (MySQL / MariaDB)
        return "Algún dato no cumple las reglas de la base (DNI, horario, estado, etc.)."
    if errno in (2003, 2002, 1045, 1049):
        return (
            "No se pudo conectar a la base de datos. Verifique que MySQL esté "
            "encendido y los datos de conexión (db.py)."
        )
    return f"Error de base de datos: {msg}"


@contextmanager
def transaccion():
    """Abre una conexión, entrega un cursor y confirma (commit) al final.

    Si algo falla hace rollback y lanza ErrorBD.
    """
    try:
        conn = mysql.connector.connect(**CONFIG)
    except MySQLError as e:
        raise ErrorBD(_traducir(e)) from e

    cur = conn.cursor(dictionary=True)
    try:
        yield cur
        conn.commit()
    except MySQLError as e:
        conn.rollback()
        raise ErrorBD(_traducir(e)) from e
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def consultar(sql, params=()):
    """Ejecuta un SELECT y devuelve una lista de diccionarios."""
    with transaccion() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def ejecutar(sql, params=()):
    """Ejecuta un INSERT/UPDATE/DELETE. Devuelve (id_insertado, filas_afectadas)."""
    with transaccion() as cur:
        cur.execute(sql, params)
        return cur.lastrowid, cur.rowcount


def probar_conexion():
    """Lanza ErrorBD si no se puede conectar."""
    consultar("SELECT 1")
