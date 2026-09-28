-- ============================================================
-- Punto Cancha - Sistema de reservas de canchas de futbol
-- Script DDL FINAL (MySQL 8.0+ / MariaDB 10.5+)
-- Tablas: socio, cancha, reserva, pago
-- Alineado al Diccionario de Datos Unificado (Evidencia 5)
-- ============================================================

DROP DATABASE IF EXISTS punto_cancha;
CREATE DATABASE punto_cancha
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE punto_cancha;

-- ============================================================
-- SOCIO
-- ============================================================
CREATE TABLE socio (
    id_socio   INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre     VARCHAR(50)  NOT NULL,
    apellido   VARCHAR(50)  NOT NULL,
    dni        VARCHAR(15)  NOT NULL,
    telefono   VARCHAR(20)  NULL,
    email      VARCHAR(100) NULL,
    CONSTRAINT pk_socio       PRIMARY KEY (id_socio),
    CONSTRAINT uq_socio_dni   UNIQUE (dni),
    CONSTRAINT uq_socio_email UNIQUE (email),
    CONSTRAINT ck_socio_dni   CHECK (dni REGEXP '^[0-9]{7,8}$')
) ENGINE = InnoDB;

-- ============================================================
-- CANCHA
-- ============================================================
CREATE TABLE cancha (
    id_cancha   INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    nombre      VARCHAR(30)      NOT NULL,
    tipo        VARCHAR(20)      NOT NULL,
    descripcion VARCHAR(200)     NULL,
    capacidad   TINYINT UNSIGNED NOT NULL,
    estado      VARCHAR(20)      NOT NULL DEFAULT 'Disponible',
    CONSTRAINT pk_cancha        PRIMARY KEY (id_cancha),
    CONSTRAINT uq_cancha_nombre UNIQUE (nombre),
    CONSTRAINT ck_cancha_tipo   CHECK (tipo IN ('Futbol 5', 'Futbol 7')),
    CONSTRAINT ck_cancha_cap    CHECK (capacidad > 0),
    CONSTRAINT ck_cancha_estado CHECK (estado IN ('Disponible', 'Mantenimiento', 'Inactiva'))
) ENGINE = InnoDB;

-- ============================================================
-- RESERVA
-- Vinculo entre socio y cancha para una fecha/horario. Estado
-- distingue Reservada / Cancelada (baja logica, nunca DELETE).
-- ============================================================
CREATE TABLE reserva (
    id_reserva  INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    id_socio    INT UNSIGNED  NOT NULL,
    id_cancha   INT UNSIGNED  NOT NULL,
    fecha       DATE          NOT NULL,
    hora_inicio TIME          NOT NULL,
    hora_fin    TIME          NOT NULL,
    total       DECIMAL(8,2)  NOT NULL,
    estado      VARCHAR(20)   NOT NULL DEFAULT 'Reservada',
    CONSTRAINT pk_reserva PRIMARY KEY (id_reserva),
    CONSTRAINT fk_reserva_socio
        FOREIGN KEY (id_socio)  REFERENCES socio (id_socio)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_reserva_cancha
        FOREIGN KEY (id_cancha) REFERENCES cancha (id_cancha)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT ck_reserva_horario CHECK (hora_fin > hora_inicio),
    CONSTRAINT ck_reserva_total   CHECK (total >= 0),
    CONSTRAINT ck_reserva_estado  CHECK (estado IN ('Reservada', 'Cancelada'))
) ENGINE = InnoDB;

-- ============================================================
-- PAGO
-- Registro del pago asociado a una reserva. Como maximo un pago
-- por reserva (UNIQUE en id_reserva). Una reserva sin fila aqui
-- se considera "pendiente de pago".
-- ============================================================
CREATE TABLE pago (
    id_pago    INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_reserva INT UNSIGNED NOT NULL,
    monto      DECIMAL(8,2) NOT NULL,
    fecha_pago DATE         NOT NULL,
    medio_pago VARCHAR(20)  NOT NULL,
    CONSTRAINT pk_pago PRIMARY KEY (id_pago),
    CONSTRAINT fk_pago_reserva
        FOREIGN KEY (id_reserva) REFERENCES reserva (id_reserva)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT uq_pago_reserva   UNIQUE (id_reserva),
    CONSTRAINT ck_pago_monto     CHECK (monto > 0),
    CONSTRAINT ck_pago_medio     CHECK (medio_pago IN ('Efectivo', 'Transferencia', 'Tarjeta'))
) ENGINE = InnoDB;

-- ============================================================
-- Indices de apoyo para disponibilidad y consultas por cancha
-- ============================================================
CREATE INDEX idx_reserva_cancha_fecha
    ON reserva (id_cancha, fecha, hora_inicio, hora_fin);

CREATE INDEX idx_reserva_socio
    ON reserva (id_socio);

-- ============================================================
-- TRIGGERS: no superposicion de horarios
-- Solo se compara contra reservas vigentes (estado = 'Reservada').
-- Hay superposicion cuando inicio_nuevo < fin_existente Y
-- fin_nuevo > inicio_existente. Reservas contiguas (una termina
-- 19:00, otra empieza 19:00) se permiten.
-- Se valida tanto en INSERT como en UPDATE (RF6 permite
-- reprogramar una reserva existente).
-- ============================================================
DELIMITER $$

CREATE TRIGGER trg_reserva_sin_superposicion_ins
BEFORE INSERT ON reserva
FOR EACH ROW
BEGIN
    IF NEW.estado = 'Reservada' AND EXISTS (
        SELECT 1
        FROM reserva r
        WHERE r.id_cancha = NEW.id_cancha
          AND r.fecha = NEW.fecha
          AND r.estado = 'Reservada'
          AND NEW.hora_inicio < r.hora_fin
          AND NEW.hora_fin > r.hora_inicio
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'La cancha ya tiene una reserva superpuesta en esa fecha y horario';
    END IF;
END$$

