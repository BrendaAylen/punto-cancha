# datos.py

def obtener_datos_iniciales():
    socios = [
        {
            "dni": "40111222",
            "nombre": "Juan",
            "apellido": "Pérez",
            "telefono": "3515551111",
            "email": "juan@email.com",
        },
        {
            "dni": "40222333",
            "nombre": "María",
            "apellido": "Gómez",
            "telefono": "3515552222",
            "email": "maria@email.com",
        },
    ]

    canchas = [
        {"numero": "1", "tipo": "Fútbol 5", "estado": "Disponible"},
        {"numero": "2", "tipo": "Fútbol 5", "estado": "Disponible"},
        {"numero": "3", "tipo": "Fútbol 7", "estado": "Disponible"},
        {"numero": "4", "tipo": "Fútbol 7", "estado": "Disponible"},
    ]

    reservas = [
        {
            "numero": 1,
            "dni": "40111222",
            "cancha": "1",
            "fecha": "20/09/2026",
            "inicio": "18:00",
            "fin": "19:00",
            "pago": "Efectivo",
            "estado": "Reservada",
        }
    ]

    pagos = ["Efectivo", "Transferencia", "Tarjeta"]

    return socios, canchas, reservas, pagos