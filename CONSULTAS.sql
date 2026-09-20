-- Punto Cancha - consultas 



-- datos iniciales de prueba
USE punto_cancha;

SET SQL_SAFE_UPDATES = 0;
DELETE FROM reserva;
DELETE FROM socio;
DELETE FROM cancha;

ALTER TABLE reserva AUTO_INCREMENT = 1;
ALTER TABLE socio AUTO_INCREMENT = 1;
ALTER TABLE cancha AUTO_INCREMENT = 1;
SET SQL_SAFE_UPDATES = 1;

-- Carga de las 4 canchas (2 de Futbol 5 y 2 de Futbol 7 con descripcion y capacidad)
INSERT INTO cancha (nombre, tipo, descripcion, capacidad, estado) VALUES
('Cancha 1', 'Futbol 5', 'Techada', 10, 'Disponible'),
('Cancha 2', 'Futbol 5', 'Techada', 10, 'Disponible'),
('Cancha 3', 'Futbol 7', 'Cesped sintetico', 14, 'Disponible'),
('Cancha 4', 'Futbol 7', 'Cesped sintetico', 14, 'Disponible');

-- Carga de los 6 socios completos (solo los nombres el resto son ficticios para esta prueba)
INSERT INTO socio (nombre, apellido, dni, telefono, email) VALUES
('Candela Guadalupe', 'Aballay', '40100001', '3515550201', 'candela.aballay@mail.com'),
('Alvaro', 'Benicio', '40100002', '3515550202', 'alvaro.benicio@mail.com'),
('Brenda', 'Espeche', '40100003', '3515550203', 'brenda.espeche@mail.com'),
('Martin', 'Gaitan', '40100004', '3515550204', 'martin.gaitan@mail.com'),
('Dayana', 'Ronco', '40100005', '3515550205', 'dayana.ronco@mail.com'),
('Roxana', 'Vilchez', '40100006', '3515550206', 'roxana.vilchez@mail.com');

-- Carga de 6 reservas iniciales de prueba
INSERT INTO reserva (id_socio, id_cancha, id_modo_pago, fecha, hora_inicio, hora_fin, total) VALUES
(1, 1, 1, '2026-10-10', '18:00', '19:00', 15000),
(2, 1, 2, '2026-10-10', '19:00', '20:00', 15000),
(3, 2, 3, '2026-10-10', '20:00', '21:00', 15000),
(4, 3, 1, '2026-10-11', '18:00', '19:00', 25000),
(5, 4, 3, '2026-10-11', '21:00', '22:00', 25000),
(6, 2, 2, '2026-10-12', '19:00', '20:00', 15000);


-- Estructura (4 tablas y columnas de reserva)
USE punto_cancha;
SHOW TABLES;
DESCRIBE reserva;


-- Datos cargados (socios, canchas y modos de pago)
USE punto_cancha;
SELECT * FROM socio;
SELECT * FROM cancha;
SELECT * FROM modo_pago;


-- Reservas con nombres 
USE punto_cancha;
SELECT r.id_reserva, s.nombre, s.apellido, c.nombre AS cancha, c.tipo,
       r.fecha, r.hora_inicio, r.hora_fin, m.nombre AS modo_pago, r.total
FROM reserva r
JOIN socio s     ON s.id_socio = r.id_socio
JOIN cancha c    ON c.id_cancha = r.id_cancha
JOIN modo_pago m ON m.id_modo_pago = r.id_modo_pago
ORDER BY r.fecha, r.hora_inicio;


-- Disponibilidad el 13/10 de 18:00 a 19:00, antes de reservar (las 4 canchas libres)
USE punto_cancha;
SELECT c.id_cancha, c.nombre, c.tipo, c.descripcion, c.capacidad
FROM cancha c
WHERE c.estado = 'Disponible'
  AND NOT EXISTS (
      SELECT 1 FROM reserva r
      WHERE r.id_cancha = c.id_cancha
        AND r.fecha = '2026-10-13'
        AND '18:00' < r.hora_fin
        AND '19:00' > r.hora_inicio);


--  Crear una reserva (ejecutar una sola vez)
USE punto_cancha;
INSERT INTO reserva (id_socio, id_cancha, id_modo_pago, fecha, hora_inicio, hora_fin, total)
VALUES (5, 2, 1, '2026-10-13', '18:00', '19:00', 15000);


--  Misma consulta de disponibilidad ( quedan las Canchas 1, 3 y 4)
USE punto_cancha;
SELECT c.id_cancha, c.nombre, c.tipo, c.descripcion, c.capacidad
FROM cancha c
WHERE c.estado = 'Disponible'
  AND NOT EXISTS (
      SELECT 1 FROM reserva r
      WHERE r.id_cancha = c.id_cancha
        AND r.fecha = '2026-10-13'
        AND '18:00' < r.hora_fin
        AND '19:00' > r.hora_inicio);


-- Reserva superpuesta (falla con el error 1644 del trigger)
USE punto_cancha;
INSERT INTO reserva (id_socio, id_cancha, id_modo_pago, fecha, hora_inicio, hora_fin, total)
VALUES (4, 2, 1, '2026-10-13', '18:30', '19:30', 15000);


--  Otras restricciones ( todas van a fallar)

--  Hora de fin anterior a la de inicio (CHECK ck_reserva_horario)
USE punto_cancha;
INSERT INTO reserva (id_socio, id_cancha, id_modo_pago, fecha, hora_inicio, hora_fin, total)
VALUES (1, 1, 1, '2026-10-20', '20:00', '19:00', 1000);

--  DNI repetido (error 1062)
USE punto_cancha;
INSERT INTO socio (nombre, apellido, dni, telefono, email)
VALUES ('Test', 'Test', '40100001', '1', 'test@mail.com');

--  Borrar un socio con reservas (error 1451, clave foranea)
USE punto_cancha;
DELETE FROM socio WHERE id_socio = 1;


--  cantidad de reservas por cancha
USE punto_cancha;
SELECT c.nombre AS cancha, c.tipo, COUNT(r.id_reserva) AS cantidad_reservas
FROM cancha c
LEFT JOIN reserva r ON r.id_cancha = c.id_cancha
GROUP BY c.id_cancha, c.nombre, c.tipo;

