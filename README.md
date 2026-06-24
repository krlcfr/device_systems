# device_systems

API REST construida con FastAPI, SQLAlchemy y Alembic para gestionar usuarios, dispositivos
y prestamos en el sistema device_systems. Esta es la version 4.0 del proyecto, donde se
agregaron relaciones entre modelos, migraciones controladas con Alembic y consultas
avanzadas con joins y filtros.

---

## Que hace este proyecto

device_systems permite administrar tres recursos relacionados entre si: usuarios, dispositivos
tecnologicos y los prestamos que los conectan. Un usuario puede solicitar el prestamo de un
dispositivo disponible, y al devolverlo el dispositivo vuelve a quedar libre para otro prestamo.
La API valida automaticamente los datos, aplica reglas de negocio sobre disponibilidad y permite
consultar la informacion combinada entre las tres tablas mediante joins.

---

## Tecnologias utilizadas

- Python 3.13
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic v2
- SQLite
- Uvicorn
- uv como gestor de paquetes

---

## Como instalarlo

```bash
git clone <url-del-repositorio>
cd device_systems
git checkout device_systems_alembic_relaciones
uv sync
```

Las dependencias del proyecto estan definidas en `pyproject.toml`, gestionadas con `uv`.

---

## Como correr el servidor

```bash
uv run uvicorn main:app --reload
```

Una vez corriendo lo encuentras en:

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## Estructura del proyecto

```
device_systems/
├── app/
│   ├── database/
│   │   └── connection.py        # Engine, SessionLocal y Base declarativa
│   ├── dependencies/
│   │   └── database_dependency.py
│   ├── models/
│   │   ├── user_model.py        # Modelo User, relacion con Loan
│   │   ├── device_model.py      # Modelo Device, relacion con Loan
│   │   └── loan_model.py        # Modelo Loan, relacion con User y Device
│   ├── schemas/
│   │   ├── user_schema.py
│   │   ├── device_schema.py
│   │   └── loan_schema.py       # Incluye LoanDetailResponse para joins
│   ├── routes/
│   │   ├── user_routes.py
│   │   ├── device_routes.py
│   │   └── loan_routes.py
│   └── services/
│       ├── user_service.py
│       ├── device_service.py
│       └── loan_service.py      # Logica de negocio y consultas con joins
├── alembic/
│   ├── versions/                # Migraciones generadas
│   └── env.py                   # Configurado para reconocer los 3 modelos
├── alembic.ini
├── main.py
├── pyproject.toml
├── device_systems.db
└── README.md
```

---

## Modelo de datos y relaciones

```
User (1) ----< (N) Loan (N) >---- (1) Device
```

Un usuario puede tener muchos prestamos. Un dispositivo puede aparecer en muchos prestamos
historicos. Cada prestamo pertenece exactamente a un usuario y a un dispositivo.

Las relaciones se definen con `ForeignKey()` para las columnas reales en la base de datos,
y con `relationship()` mas `back_populates` para navegar entre objetos en Python sin
escribir consultas manuales:

```python
usuario.loans          # todos los prestamos de ese usuario
dispositivo.loans      # todos los prestamos de ese dispositivo
prestamo.user.name      # nombre del usuario del prestamo
prestamo.device.name    # nombre del dispositivo del prestamo
```

![Diagrama de relaciones](image/relaciones.png)

---

## Migraciones con Alembic

### Inicializacion

```bash
uv run alembic init alembic
```

![alembic init](image/alembic_init.png)

### Configuracion

Se edito `alembic.ini` para apuntar a la base de datos del proyecto:

```ini
sqlalchemy.url = sqlite:///./device_systems.db
```

Y `alembic/env.py` para reconocer la Base declarativa y los tres modelos:

```python
from app.database.connection import Base
from app.models.user_model import User
from app.models.device_model import Device
from app.models.loan_model import Loan

target_metadata = Base.metadata
```

### Migracion inicial (baseline)

Como la tabla `users` ya existia antes de instalar Alembic, se genero una migracion base
y se marco como aplicada sin ejecutarla, para sincronizar el historial sin tocar los datos:

```bash
uv run alembic revision --autogenerate -m "baseline users table"
uv run alembic stamp head
```

### Migracion de las tablas nuevas

```bash
uv run alembic revision --autogenerate -m "create devices and loans tables"
```

![alembic revision](image/alembic_revision.png)

```bash
uv run alembic upgrade head
```

![alembic upgrade](image/alembic_upgrade.png)

### Historial de migraciones

```bash
uv run alembic history
```

![alembic history](image/alembic_history.png)

```
<base> -> f9b3ea0a77a4, baseline users table
f9b3ea0a77a4 -> d9a68d1c2c56 (head), create devices and loans tables
```

---

## Estructura de tablas generadas

![Tablas en la base de datos](image/database_tables.png)

---

## Endpoints disponibles

### Users

| Metodo | Ruta                  | Que hace                                  |
|--------|-----------------------|--------------------------------------------|
| GET    | /users                | Lista usuarios con filtros                  |
| GET    | /users/{user_id}      | Consulta un usuario por ID                  |
| POST   | /users                | Crea un usuario                             |
| PUT    | /users/{user_id}      | Reemplaza un usuario completo               |
| PATCH  | /users/{user_id}      | Modifica campos especificos                 |
| DELETE | /users/{user_id}      | Elimina un usuario                          |
| GET    | /users/{user_id}/loans| Historial de prestamos de ese usuario       |

### Devices

| Metodo | Ruta                      | Que hace                              |
|--------|---------------------------|----------------------------------------|
| GET    | /devices                  | Lista dispositivos con filtros          |
| GET    | /devices/{device_id}      | Consulta un dispositivo por ID          |
| POST   | /devices                  | Crea un dispositivo                     |
| PUT    | /devices/{device_id}      | Reemplaza un dispositivo completo       |
| PATCH  | /devices/{device_id}      | Modifica campos especificos             |
| DELETE | /devices/{device_id}      | Elimina un dispositivo                  |
| GET    | /devices/{device_id}/loans| Historial de prestamos de ese dispositivo |

Filtros disponibles en `/devices`:
- `?device_type=laptop`
- `?is_available=true`
- `?brand=lenovo`
- `?search=thinkpad` (busca en nombre, serial y marca)

### Loans

| Metodo | Ruta                    | Que hace                                          |
|--------|--------------------------|----------------------------------------------------|
| GET    | /loans                   | Lista prestamos con filtros                         |
| GET    | /loans/details           | Lista prestamos con datos de usuario y dispositivo  |
| GET    | /loans/{loan_id}         | Consulta un prestamo por ID                         |
| POST   | /loans                   | Crea un prestamo, valida usuario y disponibilidad   |
| PATCH  | /loans/{loan_id}/return  | Marca el prestamo como devuelto y libera el equipo  |

Filtros disponibles:
- `/loans?status=active`
- `/loans?user_id=1`
- `/loans?device_id=3`
- `/loans/details?status=active`
- `/loans/details?user_email=ana@mail.com`
- `/loans/details?device_type=laptop`

---

## Codigos de estado usados

| Codigo | Cuando ocurre                                              |
|--------|-------------------------------------------------------------|
| 200    | Operacion exitosa                                            |
| 201    | Registro creado exitosamente                                 |
| 204    | Eliminacion exitosa, sin cuerpo de respuesta                |
| 400    | Dato duplicado (email o numero de serie) o PATCH vacio      |
| 404    | Usuario, dispositivo o prestamo no encontrado                |
| 409    | Dispositivo no disponible, o prestamo ya devuelto            |
| 422    | Datos invalidos o filtro con valor fuera de lo permitido     |

---

## Flujo completo de un prestamo

### 1. Crear usuario y dispositivo

![Crear usuario](image/create_user.png)
![Crear dispositivo](image/create_device.png)

### 2. Crear el prestamo

```json
{
  "user_id": 1,
  "device_id": 1
}
```

![Crear prestamo](image/create_loan.png)

### 3. Verificar que el dispositivo quedo ocupado

`GET /devices/1` debe mostrar `"is_available": false`.

![Dispositivo ocupado](image/device_unavailable.png)

### 4. Intentar prestar el mismo dispositivo otra vez (409)

```json
{
  "detail": "El dispositivo no esta disponible para prestamo"
}
```

![Error 409 dispositivo no disponible](image/error_409_device.png)

### 5. Devolver el dispositivo

`PATCH /loans/1/return`

![Devolver prestamo](image/return_loan.png)

### 6. Verificar que el dispositivo quedo libre otra vez

`GET /devices/1` debe mostrar `"is_available": true`.

![Dispositivo disponible](image/device_available.png)

### 7. Intentar devolver un prestamo ya devuelto (409)

```json
{
  "detail": "Este prestamo ya fue devuelto"
}
```

![Error 409 prestamo ya devuelto](image/error_409_loan.png)

---

## Consultas con joins

### Prestamos con informacion de usuario y dispositivo

`GET /loans/details`

```json
[
  {
    "id": 1,
    "status": "returned",
    "loan_date": "2024-01-15T10:30:00",
    "return_date": "2024-01-20T15:00:00",
    "user": {
      "id": 1,
      "name": "Ana Perez",
      "email": "ana@mail.com"
    },
    "device": {
      "id": 1,
      "name": "Laptop Lenovo ThinkPad",
      "serial_number": "LEN-2024-001",
      "device_type": "laptop"
    }
  }
]
```

![GET loans details](image/loans_details.png)

### Filtrar prestamos por estado

`GET /loans/details?status=active`

![Filtro por estado](image/loans_filter_status.png)

### Filtrar prestamos por tipo de dispositivo

`GET /loans/details?device_type=laptop`

![Filtro por tipo de dispositivo](image/loans_filter_device_type.png)

### Consultar prestamos de un usuario

`GET /users/1/loans`

![Prestamos de un usuario](image/user_loans.png)

### Consultar historial de un dispositivo

`GET /devices/1/loans`

![Historial de un dispositivo](image/device_loans.png)

---

## Filtro invalido (422)

`GET /loans?status=inventado`

```json
{
  "detail": [
    {
      "type": "enum",
      "loc": ["query", "status"],
      "msg": "Input should be 'active', 'returned' or 'overdue'"
    }
  ]
}
```

![Error 422 filtro invalido](image/error_422_filter.png)

---

## Capturas de Swagger UI

![Swagger UI](image/swagger_ui.png)

Los endpoints estan organizados por tags: **Users**, **Devices** y **Loans**.

---

## Como funcionan los joins en este proyecto

Las consultas con joins usan tres herramientas principales de SQLAlchemy:

`joinedload()` precarga las relaciones `user` y `device` de cada prestamo en la misma
consulta SQL, evitando que se dispare una query adicional cada vez que se accede a
`loan.user` o `loan.device`.

```python
query = db.query(Loan).options(joinedload(Loan.user), joinedload(Loan.device))
```

`.join()` conecta explicitamente las tablas para poder filtrar por columnas de `User`
o `Device` dentro de la misma consulta de `Loan`.

```python
query = query.join(User, Loan.user_id == User.id).join(Device, Loan.device_id == Device.id)
```

`and_()` combina varias condiciones de filtro de forma dinamica, solo se agregan las
condiciones que el cliente realmente envio.

```python
if conditions:
    query = query.where(and_(*conditions))
```

`ilike()` permite busquedas de texto parcial sin importar mayusculas o minusculas,
usado tanto en el filtro de dispositivos como en el filtro por email de usuario.

---

## Reglas de negocio en prestamos

El endpoint `POST /loans` valida en cadena: que el usuario exista, que el dispositivo
exista, y que el dispositivo este disponible. Si todo pasa, crea el prestamo y marca
el dispositivo como no disponible, todo en la misma transaccion.

El endpoint `PATCH /loans/{loan_id}/return` valida que el prestamo no haya sido
devuelto previamente. Si pasa, marca el estado como `returned`, asigna la fecha de
devolucion y libera el dispositivo.

El codigo 409 se usa especificamente para estos casos porque la peticion en si es
valida, el conflicto esta en el estado actual del recurso, no en los datos enviados.

---

## Reflexion

Pasar de un CRUD simple de usuarios a un sistema con tres entidades relacionadas cambia
por completo la complejidad del proyecto. Las migraciones con Alembic resuelven un
problema real: sin ellas, cualquier cambio en los modelos significa borrar la base de
datos y perder los datos, algo inaceptable en un entorno real. Versionar los cambios
permite evolucionar el esquema sin perder informacion y sin que distintos entornos
queden desincronizados.

Las relaciones con `relationship()` y `back_populates` simplifican mucho el acceso a
datos conectados, evitando escribir joins manuales en cada consulta. Y cuando si se
necesita un join explicito, como en las consultas con filtros avanzados, SQLAlchemy
ofrece herramientas claras y expresivas con `join()`, `where()`, `and_()` e `ilike()`.

La regla de negocio de disponibilidad de dispositivos fue el reto mas interesante:
entender por que un 409 es mas correcto que un 400 para un conflicto de estado, y
como una sola transaccion puede actualizar dos tablas relacionadas de forma consistente,
fue clave para construir una API que se comporta de forma predecible.

