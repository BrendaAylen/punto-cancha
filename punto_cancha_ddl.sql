-- Punto Cancha - Sistema de reservas de canchas de futbol
-- Script DDL (MySQL 8.0+ / MariaDB 10.5+)
-- Tablas: socio, cancha, modo_pago, reserva

DROP DATABASE IF EXISTS punto_cancha;
CREATE DATABASE punto_cancha
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE punto_cancha;

-- SOCIO
CREATE TABLE socio (
    id_socio   INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre     VARCHAR(50)  NOT NULL,
    apellido   VARCHAR(50)  NOT NULL,
    dni        VARCHAR(8)   NOT NULL,
    telefono   VARCHAR(20)  NOT NULL,
    email      VARCHAR(100) NULL,
    CONSTRAINT pk_socio       PRIMARY KEY (id_socio),
    CONSTRAINT uq_socio_dni   UNIQUE (dni),
    CONSTRAINT uq_socio_email UNIQUE (email),
    CONSTRAINT ck_socio_dni   CHECK (dni REGEXP '^[0-9]{7,8}$')
) ENGINE = InnoDB;

-- CANCHA
CREATE TABLE cancha (
    id_cancha   INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    nombre      VARCHAR(50)      NOT NULL,
    tipo        VARCHAR(20)      NOT NULL,
    descripcion VARCHAR(255)     NULL,
    capacidad   TINYINT UNSIGNED NOT NULL,
    estado      VARCHAR(20)      NOT NULL DEFAULT 'Disponible',
    CONSTRAINT pk_cancha        PRIMARY KEY (id_cancha),
    CONSTRAINT uq_cancha_nombre UNIQUE (nombre),
    CONSTRAINT ck_cancha_cap    CHECK (capacidad > 0),
    CONSTRAINT ck_cancha_estado CHECK (estado IN ('Disponible', 'Mantenimiento', 'Inactiva'))
) ENGINE = InnoDB;

-- MODO_PAGO (catalogo)
CREATE TABLE modo_pago (
    id_modo_pago TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre       VARCHAR(30)      NOT NULL,
    CONSTRAINT pk_modo_pago        PRIMARY KEY (id_modo_pago),
    CONSTRAINT uq_modo_pago_nombre UNIQUE (nombre)
) ENGINE = InnoDB;

-- RESERVA
CREATE TABLE reserva (
    id_reserva   INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    id_socio     INT UNSIGNED     NOT NULL,
    id_cancha    INT UNSIGNED     NOT NULL,
    id_modo_pago TINYINT UNSIGNED NOT NULL,
    fecha        DATE             NOT NULL,
    hora_inicio  TIME             NOT NULL,
    hora_fin     TIME             NOT NULL,
    total        DECIMAL(10,2)    NOT NULL,
    CONSTRAINT pk_reserva PRIMARY KEY (id_reserva),
    CONSTRAINT fk_reserva_socio
        FOREIGN KEY (id_socio)     REFERENCES socio (id_socio)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_reserva_cancha
        FOREIGN KEY (id_cancha)    REFERENCES cancha (id_cancha)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_reserva_modo_pago
        FOREIGN KEY (id_modo_pago) REFERENCES modo_pago (id_modo_pago)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT ck_reserva_horario CHECK (hora_fin > hora_inicio),
    CONSTRAINT ck_reserva_total   CHECK (total >= 0)
) ENGINE = InnoDB;

-- Indice para las consultas de disponibilidad y de reservas por cancha
CREATE INDEX idx_reserva_cancha_fecha
    ON reserva (id_cancha, fecha, hora_inicio, hora_fin);

-- Regla de negocio: no superposicion de reservas.
-- Misma cancha y misma fecha con horarios que se pisan => se rechaza.
-- Hay superposicion cuando inicio_nuevo < fin_existente Y fin_nuevo > inicio_existente.
-- Las reservas contiguas (una termina a las 19:00 y otra empieza a las 19:00) se permiten.
DELIMITER $$

CREATE TRIGGER trg_reserva_sin_superposicion_ins
BEFORE INSERT ON reserva
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1
        FROM reserva r
        WHERE r.id_cancha = NEW.id_cancha
          AND r.fecha = NEW.fecha
          AND NEW.hora_inicio < r.hora_fin
          AND NEW.hora_fin > r.hora_inicio
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'La cancha ya tiene una reserva superpuesta en esa fecha y horario';
    END IF;
END$$

CREATE TRIGGER trg_reserva_sin_superposicion_upd
BEFORE UPDATE ON reserva
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1
        FROM reserva r
        WHERE r.id_cancha = NEW.id_cancha
          AND r.fecha = NEW.fecha
          AND r.id_reserva <> NEW.id_reserva
          AND NEW.hora_inicio < r.hora_fin
          AND NEW.hora_fin > r.hora_inicio
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'La cancha ya tiene una reserva superpuesta en esa fecha y horario';
    END IF;
END$$

DELIMITER ;

-- Datos iniciales del catalogo
INSERT INTO modo_pago (nombre) VALUES
    ('Efectivo'),
    ('Transferencia'),
    ('Tarjeta');
