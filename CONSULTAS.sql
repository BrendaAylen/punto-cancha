-- ============================================================
-- SCRIPT COMPLETO PARA MYSQL: PUNTO CANCHA
-- ============================================================

-- 1. CREACIÓN Y SELECCIÓN DE BASE DE DATOS
CREATE DATABASE IF NOT EXISTS punto_cancha;
USE punto_cancha;

-- 2. DDL - ESTRUCTURA DE TABLAS (SI NO EXISTEN)
CREATE TABLE IF NOT EXISTS modo_pago (
    id_modo_pago INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS socio (
    id_socio INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    dni VARCHAR(20) NOT NULL UNIQUE,
    telefono VARCHAR(20),
    email VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS cancha (
    id_cancha INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255),
    capacidad INT NOT NULL,
    estado VARCHAR(20) DEFAULT 'Disponible'
);

CREATE TABLE IF NOT EXISTS reserva (
    id_reserva INT AUTO_INCREMENT PRIMARY KEY,
    id_socio INT NOT NULL,
    id_cancha INT NOT NULL,
    id_modo_pago INT NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    CONSTRAINT ck_reserva_horario CHECK (hora_fin > hora_inicio),
    CONSTRAINT fk_reserva_socio FOREIGN KEY (id_socio) REFERENCES socio(id_socio),
    CONSTRAINT fk_reserva_cancha FOREIGN KEY (id_cancha) REFERENCES cancha(id_cancha),
    CONSTRAINT fk_reserva_modo_pago FOREIGN KEY (id_modo_pago) REFERENCES modo_pago(id_modo_pago)
);

-- 3. TRIGGER PARA VERIFICAR SUPERPOSICIÓN DE RESERVAS (ERROR 1644)
DELIMITER //
CREATE TRIGGER trg_validar_superposicion_reserva
BEFORE INSERT ON reserva
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1 FROM reserva r
        WHERE r.id_cancha = NEW.id_cancha
          AND r.fecha = NEW.fecha
          AND NEW.hora_inicio < r.hora_fin
          AND NEW.hora_fin > r.hora_inicio
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error 1644: La cancha ya se encuentra reservada en el horario seleccionado.',
            MYSQL_ERRNO = 1644;
    END IF;
END//
DELIMITER ;

-- 4. LIMPIEZA E INICIALIZACIÓN DE DATOS PRUEBA
SET SQL_SAFE_UPDATES = 0;

DELETE FROM reserva;
DELETE FROM socio;
DELETE FROM cancha;
DELETE FROM modo_pago;

ALTER TABLE reserva AUTO_INCREMENT = 1;
ALTER TABLE socio AUTO_INCREMENT = 1;
ALTER TABLE cancha AUTO_INCREMENT = 1;
ALTER TABLE modo_pago AUTO_INCREMENT = 1;

SET SQL_SAFE_UPDATES = 1;

-- Carga de Modos de Pago
INSERT INTO modo_pago (nombre) VALUES 
('Efectivo'), 
('Tarjeta de Débito'), 
('Transferencia');

-- Carga de las 4 canchas (2 de Fútbol 5 y 2 de Fútbol 7)
INSERT INTO cancha (nombre, tipo, descripcion, capacidad, estado) VALUES
('Cancha 1', 'Futbol 5', 'Techada', 10, 'Disponible'),
('Cancha 2', 'Futbol 5', 'Techada', 10, 'Disponible'),
('Cancha 3', 'Futbol 7', 'Cesped sintetico', 14, 'Disponible'),
('Cancha 4', 'Futbol 7', 'Cesped sintetico', 14, 'Disponible');

-- Carga de los 6 socios completos
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


-- 5. CONSULTAS DE VERIFICACIÓN
SHOW TABLES;
DESCRIBE reserva;

SELECT * FROM socio;
SELECT * FROM cancha;
SELECT * FROM modo_pago;

-- Reservas con nombres completos
SELECT r.id_reserva, s.nombre, s.apellido, c.nombre AS cancha, c.tipo,
       r.fecha, r.hora_inicio, r.hora_fin, m.nombre AS modo_pago, r.total
FROM reserva r
JOIN socio s     ON s.id_socio = r.id_socio
JOIN cancha c    ON c.id_cancha = r.id_cancha
JOIN modo_pago m ON m.id_modo_pago = r.id_modo_pago
ORDER BY r.fecha, r.hora_inicio;

-- Disponibilidad el 13/10 de 18:00 a 19:00 (las 4 canchas libres)
SELECT c.id_cancha, c.nombre, c.tipo, c.descripcion, c.capacidad
FROM cancha c
WHERE c.estado = 'Disponible'
  AND NOT EXISTS (
      SELECT 1 FROM reserva r
      WHERE r.id_cancha = c.id_cancha
        AND r.fecha = '2026-10-13'
        AND '18:00' < r.hora_fin
        AND '19:00' > r.hora_inicio);

-- Crear una reserva
INSERT INTO reserva (id_socio, id_cancha, id_modo_pago, fecha, hora_inicio, hora_fin, total)
VALUES (5, 2, 1, '2026-10-13', '18:00', '19:00', 15000);

-- Misma consulta de disponibilidad (quedan las Canchas 1, 3 y 4)
SELECT c.id_cancha, c.nombre, c.tipo, c.descripcion, c.capacidad
FROM cancha c
WHERE c.estado = 'Disponible'
  AND NOT EXISTS (
      SELECT 1 FROM reserva r
      WHERE r.id_cancha = c.id_cancha
        AND r.fecha = '2026-10-13'
        AND '18:00' < r.hora_fin
        AND '19:00' > r.hora_inicio);

-- Cantidad de reservas por cancha
SELECT c.nombre AS cancha, c.tipo, COUNT(r.id_reserva) AS cantidad_reservas
FROM cancha c
LEFT JOIN reserva r ON r.id_cancha = c.id_cancha
GROUP BY c.id_cancha, c.nombre, c.tipo;


-- 6. PRUEBAS DE RESTRICCIONES (EJECUTAR INDIVIDUALMENTE - ARROJAN ERROR ESPERADO)

-- Reserva superpuesta (Falla con Error 1644 del Trigger)
-- INSERT INTO reserva (id_socio, id_cancha, id_modo_pago, fecha, hora_inicio, hora_fin, total)
-- VALUES (4, 2, 1, '2026-10-13', '18:30', '19:30', 15000);

-- Hora de fin anterior a inicio (Falla con CHECK ck_reserva_horario)
-- INSERT INTO reserva (id_socio, id_cancha, id_modo_pago, fecha, hora_inicio, hora_fin, total)
-- VALUES (1, 1, 1, '2026-10-20', '20:00', '19:00', 1000);

-- DNI repetido (Falla con Error 1062 - Clave duplicada)
-- INSERT INTO socio (nombre, apellido, dni, telefono, email)
-- VALUES ('Test', 'Test', '40100001', '1', 'test@mail.com');

-- Borrar socio con reservas activas (Falla con Error 1451 - Key constraint)
-- DELETE FROM socio WHERE id_socio = 1;