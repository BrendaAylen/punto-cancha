-- ============================================================
-- Punto Cancha - Roles de acceso y usuarios (MySQL 8.0+)
-- Ejecutar con el usuario root, DESPUES de punto_cancha_ddl.sql
-- (los GRANT sobre tablas exigen que las tablas ya existan).
--
-- Principio de minimo privilegio: cada rol recibe solo lo que necesita.
--   rol_admin     -> control total sobre la base punto_cancha
--   rol_recepcion -> operacion diaria: altas, consultas y modificaciones;
--                    NO puede borrar registros (las reservas se cancelan
--                    con baja logica: UPDATE de estado)
--   rol_consulta  -> solo lectura (reportes)
--
-- Las claves de abajo son SOLO de demostracion: cambiarlas en un uso real.
-- ============================================================

-- ---------- Roles ----------
CREATE ROLE IF NOT EXISTS 'rol_admin', 'rol_recepcion', 'rol_consulta';

-- ---------- Permisos de cada rol ----------
GRANT ALL PRIVILEGES ON punto_cancha.* TO 'rol_admin';

GRANT SELECT, INSERT, UPDATE ON punto_cancha.socio   TO 'rol_recepcion';
GRANT SELECT                 ON punto_cancha.cancha  TO 'rol_recepcion';
GRANT SELECT, INSERT, UPDATE ON punto_cancha.reserva TO 'rol_recepcion';
GRANT SELECT, INSERT, UPDATE ON punto_cancha.pago    TO 'rol_recepcion';

GRANT SELECT ON punto_cancha.socio   TO 'rol_consulta';
GRANT SELECT ON punto_cancha.cancha  TO 'rol_consulta';
GRANT SELECT ON punto_cancha.reserva TO 'rol_consulta';
GRANT SELECT ON punto_cancha.pago    TO 'rol_consulta';

-- ---------- Usuarios ----------
CREATE USER IF NOT EXISTS 'admin_pc'@'localhost'     IDENTIFIED BY 'Admin_pc_2026';
CREATE USER IF NOT EXISTS 'recepcion_pc'@'localhost' IDENTIFIED BY 'Recepcion_pc_2026';
CREATE USER IF NOT EXISTS 'consulta_pc'@'localhost'  IDENTIFIED BY 'Consulta_pc_2026';

GRANT 'rol_admin'     TO 'admin_pc'@'localhost';
GRANT 'rol_recepcion' TO 'recepcion_pc'@'localhost';
GRANT 'rol_consulta'  TO 'consulta_pc'@'localhost';

-- En MySQL 8 los roles no se activan solos al conectarse: hay que
-- definirlos como rol por defecto de cada usuario.
SET DEFAULT ROLE 'rol_admin'     TO 'admin_pc'@'localhost';
SET DEFAULT ROLE 'rol_recepcion' TO 'recepcion_pc'@'localhost';
SET DEFAULT ROLE 'rol_consulta'  TO 'consulta_pc'@'localhost';

-- ---------- Verificacion (para las capturas de la entrega) ----------
-- SHOW GRANTS FOR 'rol_recepcion';
-- SHOW GRANTS FOR 'recepcion_pc'@'localhost' USING 'rol_recepcion';
-- SELECT user, host FROM mysql.user WHERE user LIKE '%_pc';
