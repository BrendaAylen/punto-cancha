-- ============================================================
-- Punto Cancha - Datos de prueba (minimo 10 registros por tabla)
-- Ejecutar DESPUES de punto_cancha_ddl.sql.
-- Precios usados en los totales: Futbol 5 = 15000/h, Futbol 7 = 22000/h
-- ============================================================
SET NAMES utf8mb4;
USE punto_cancha;

INSERT INTO socio (dni, nombre, apellido, telefono, email) VALUES
    ('40111222', 'Juan',     'Pérez',     '3515551111', 'juan@email.com'),
    ('40222333', 'María',    'Gómez',     '3515552222', 'maria@email.com'),
    ('38333444', 'Lucas',    'Fernández', '3515553333', 'lucas.fernandez@email.com'),
    ('41444555', 'Sofía',    'Rodríguez', '3515554444', 'sofia.rodriguez@email.com'),
    ('36555666', 'Martín',   'López',     '3515555555', 'martin.lopez@email.com'),
    ('42666777', 'Camila',   'Díaz',      '3515556666', 'camila.diaz@email.com'),
    ('39777888', 'Nicolás',  'Sosa',      '3515557777', 'nicolas.sosa@email.com'),
    ('43888999', 'Valentina','Romero',    '3515558888', 'valentina.romero@email.com'),
    ('37999000', 'Mateo',    'Acosta',    '3515559999', 'mateo.acosta@email.com'),
    ('44100200', 'Julieta',  'Torres',    '3515550000', 'julieta.torres@email.com'),
    ('35300400', 'Federico', 'Molina',    '3515551212', 'federico.molina@email.com'),
    ('45500600', 'Agustina', 'Herrera',   '3515552323', 'agustina.herrera@email.com');

INSERT INTO cancha (id_cancha, nombre, tipo, descripcion, capacidad, estado) VALUES
    (1,  'Cancha 1',  'Futbol 5', 'Césped sintético, techada',        10, 'Disponible'),
    (2,  'Cancha 2',  'Futbol 5', 'Césped sintético, techada',        10, 'Disponible'),
    (3,  'Cancha 3',  'Futbol 7', 'Césped sintético, al aire libre',  14, 'Disponible'),
    (4,  'Cancha 4',  'Futbol 7', 'Césped sintético, al aire libre',  14, 'Disponible'),
    (5,  'Cancha 5',  'Futbol 5', 'Piso de cemento alisado',          10, 'Disponible'),
    (6,  'Cancha 6',  'Futbol 5', 'Césped sintético, con iluminación',10, 'Disponible'),
    (7,  'Cancha 7',  'Futbol 7', 'Césped natural',                   14, 'Disponible'),
    (8,  'Cancha 8',  'Futbol 7', 'Césped sintético, con tribuna',    14, 'Disponible'),
    (9,  'Cancha 9',  'Futbol 5', 'Césped sintético',                 10, 'Mantenimiento'),
    (10, 'Cancha 10', 'Futbol 7', 'Césped natural, fuera de servicio',14, 'Inactiva');

INSERT INTO reserva (id_socio, id_cancha, fecha, hora_inicio, hora_fin, total, estado) VALUES
    (1,  1, '2026-10-20', '18:00', '19:00', 15000.00, 'Reservada'),
    (2,  1, '2026-10-20', '19:00', '20:00', 15000.00, 'Reservada'),
    (3,  2, '2026-10-20', '20:00', '21:30', 22500.00, 'Reservada'),
    (4,  3, '2026-10-21', '19:00', '20:00', 22000.00, 'Reservada'),
    (5,  3, '2026-10-21', '20:00', '22:00', 44000.00, 'Reservada'),
    (6,  4, '2026-10-22', '18:00', '19:00', 22000.00, 'Reservada'),
    (7,  5, '2026-10-22', '21:00', '22:00', 15000.00, 'Reservada'),
    (8,  6, '2026-10-23', '17:00', '18:30', 22500.00, 'Reservada'),
    (9,  7, '2026-10-24', '16:00', '17:00', 22000.00, 'Reservada'),
    (10, 8, '2026-10-24', '20:00', '21:00', 22000.00, 'Reservada'),
    (11, 2, '2026-10-25', '18:00', '19:00', 15000.00, 'Cancelada'),
    (12, 1, '2026-10-26', '21:00', '22:00', 15000.00, 'Reservada');

-- 11 pagos: la reserva 12 queda "pendiente de pago" (sin fila en pago)
INSERT INTO pago (id_reserva, monto, fecha_pago, medio_pago) VALUES
    (1,  15000.00, '2026-10-13', 'Efectivo'),
    (2,  15000.00, '2026-10-13', 'Transferencia'),
    (3,  22500.00, '2026-10-14', 'Tarjeta'),
    (4,  22000.00, '2026-10-14', 'Efectivo'),
    (5,  44000.00, '2026-10-15', 'Transferencia'),
    (6,  22000.00, '2026-10-15', 'Tarjeta'),
    (7,  15000.00, '2026-10-16', 'Efectivo'),
    (8,  22500.00, '2026-10-16', 'Transferencia'),
    (9,  22000.00, '2026-10-17', 'Tarjeta'),
    (10, 22000.00, '2026-10-17', 'Efectivo'),
    (11, 15000.00, '2026-10-18', 'Efectivo');
