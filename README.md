# punto-cancha
Sistema de gestión de reservas para el club Punto Cancha (2 canchas de fútbol 5 y 2 de fútbol 7). Proyecto ABP - Módulo programador, base de datos, Tecnicatura Superior en Desarrollo de Software - ISPC 2026

## Integrantes
- Aballay, Candela Guadalupe
- Benicio, Alvaro Reinaldo
- Espeche, Brenda Aylen
- Gaitán, Martín Eduarno
- Ronco, Dayana Agustina
- Vilchez, Roxana

## Reparto de tareas
- Documentación, proyecto y Git: Espeche, Brenda y Ronco, Dayana
- Base de datos (E-R, Normalización y DDL): Benicio, Alvaro y Vilchez, Roxana
- Desarrollo de Interfaz Gráfica: Gaitán, Martín y Aballay, Candela

## Tecnologías
- Python 3.10 o superior con Tkinter (interfaz)
- MySQL 8.0 (base de datos)
- mysql-connector-python (conexión entre Python y MySQL)

## Estado actual
- Base de datos implementada en MySQL: 4 tablas con claves, restricciones e integridad, triggers, datos de prueba y roles de acceso.
- Aplicación Tkinter conectada a la base: altas, consultas, modificaciones y bajas con confirmación, más consultas con JOIN.
- Documentación: diccionario de datos y manual de usuario (`Manual Punto Cancha.pdf`).
- En curso: informe final y bitácora.

## Estructura del repositorio
| Archivo | Contenido |
|---|---|
| `main.py` | Punto de entrada: verifica la conexión y abre la aplicación |
| `interfaz.py` | Pantallas Tkinter |
| `funciones.py` | Lógica de negocio y sentencias SQL propias |
| `db.py` | Conexión a MySQL y manejo de errores |
| `punto_cancha_ddl.sql` | Esquema: tablas, restricciones, índices y triggers |
| `datos_iniciales.sql` | Datos de prueba (10 o más registros por tabla) |
| `roles_acceso.sql` | Roles y usuarios de la base de datos |
| `CONSULTAS.sql` | Consultas SQL del proyecto |
| `requirements.txt` | Dependencias de Python |
| `DICCIONARIO PUNTO CANCHA .docx` | Diccionario de datos |
| `Manual Punto Cancha.pdf` | Manual de usuario |

## Modelo de datos
Tablas: `socio`, `cancha`, `reserva` y `pago`. El modo de pago es una columna de `pago` (`Efectivo`, `Transferencia` o `Tarjeta`).

Integridad definida en el DDL:
- Claves primarias y foráneas (`ON DELETE RESTRICT`).
- `UNIQUE` en DNI y email del socio, nombre de cancha y un único pago por reserva.
- `CHECK` en DNI (7 u 8 dígitos), tipo y estado de cancha, horario, total, monto y medio de pago.
- Triggers que impiden reservas superpuestas y reservas en canchas que no están disponibles.
- Las reservas no se borran: se cancelan (baja lógica).

## Datos de prueba
`datos_iniciales.sql` carga 12 socios, 10 canchas, 12 reservas y 11 pagos. Las canchas 1 a 4 corresponden al club real; **las canchas 5 a 10 son ficticias** y se agregaron solo para cumplir el mínimo de 10 registros de prueba por tabla.

## Roles de acceso
Definidos en `roles_acceso.sql` (las claves de demostración están en ese archivo):

| Rol | Usuario | Permisos |
|---|---|---|
| `rol_admin` | `admin_pc` | Control total sobre la base `punto_cancha` |
| `rol_recepcion` | `recepcion_pc` | Consultar, dar de alta y modificar. No puede eliminar registros |
| `rol_consulta` | `consulta_pc` | Solo lectura |

## Cómo ejecutar el proyecto
1. Instalar Python 3.10 o superior y MySQL 8.0 (con MySQL Workbench).
2. Instalar la dependencia:
   ```
   python -m pip install -r requirements.txt
   ```
3. En MySQL Workbench, abrir y ejecutar con el usuario `root`, **en este orden**:
   1. `punto_cancha_ddl.sql` (borra y recrea la base `punto_cancha`)
   2. `datos_iniciales.sql`
   3. `roles_acceso.sql`
4. En la consola, dentro de la carpeta del proyecto, indicar la clave del usuario de recepción (`recepcion_pc`, el usuario por defecto de `db.py`) (en Windows):
   ```
   set "PC_DB_PASSWORD=<clave del usuario>"
   python main.py
   ```
   Para las bajas usar el usuario `admin_pc` (`set "PC_DB_USER=admin_pc"`). En Linux o macOS, usar `export` en lugar de `set`.

Los datos de conexión (servidor, puerto, usuario, clave y base) se leen de variables de entorno y se pueden ver en `db.py`. No se guardan claves reales en el repositorio.

## Funcionalidades
- **Socios y canchas:** alta, consulta, modificación y baja con confirmación.
- **Reservas:** alta (con su pago), modificación, cancelación con confirmación, filtros y detalle de cada reserva.
- **Disponibilidad:** valida que la cancha esté habilitada y sin horarios superpuestos.
- **Reservas por cancha:** cantidad de reservas vigentes de cada cancha.
- **Consultas con JOIN:** detalle de reservas (socio, cancha y pago), reservas pendientes de pago y resumen por socio. Incluye un botón para ver la sentencia SQL.

## Colaboración
Cada integrante trabaja en su propia rama (`feature/...`, `fix/...`, `docs/...`) y sube sus cambios mediante Pull Request a `main`.
