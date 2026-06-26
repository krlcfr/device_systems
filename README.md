# device_systems

API REST construida con FastAPI, SQLAlchemy, Alembic y JWT para gestionar usuarios,
dispositivos y prestamos del sistema device_systems. Esta es la version 4.0.0, que cierra
el proyecto agregando autenticacion OAuth2 + JWT, autorizacion por roles, middleware
personalizado, CORS, rate limiting y manejo centralizado de configuracion.

---

## Que hace este proyecto

device_systems administra tres recursos relacionados (usuarios, dispositivos y prestamos)
detras de una capa de seguridad real. Nadie puede consultar o modificar datos sensibles sin
autenticarse con un token JWT, y cada accion respeta el rol del usuario que la solicita.
Ademas, cada peticion queda registrada con un identificador unico y su tiempo de respuesta,
y existen limites de frecuencia para evitar abuso sobre los endpoints mas sensibles.

---

## Tecnologias utilizadas

- Python 3.14
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic v2
- python-jose (JWT)
- passlib + bcrypt (hash de contrasenas)
- slowapi (rate limiting)
- python-dotenv (variables de entorno)
- SQLite
- Uvicorn
- uv como gestor de paquetes

---

## Como instalarlo

```bash
git clone <url-del-repositorio>
cd device_systems
git checkout device_systems_security
uv sync
```

Las dependencias del proyecto estan definidas en `pyproject.toml`, gestionadas con `uv`.
Tambien se incluye un `requirements.txt` como referencia para entornos que usen `pip`.

---

## Configuracion de variables de entorno

Copia el archivo de ejemplo y ajusta los valores segun tu entorno:

```bash
cp .env.example .env
```

```env
# Clave secreta para firmar los tokens JWT
# En produccion, genera una clave fuerte con: openssl rand -hex 32
SECRET_KEY=device-systems-secret-key-cambiar-en-produccion

# URL de la base de datos
DATABASE_URL=sqlite:///./device_systems.db

# Tiempo de expiracion del token JWT en minutos
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

`SECRET_KEY` nunca debe quedar hardcodeada ni subirse a un repositorio publico con su valor
real. El valor por defecto en el codigo solo existe para que el proyecto funcione sin
configuracion adicional en un entorno de practica.

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
│   ├── auth/
│   │   ├── security.py          # Hash de contrasenas y manejo de JWT
│   │   ├── auth_service.py      # Logica de registro y autenticacion
│   │   └── auth_routes.py       # Endpoints /auth/register, /auth/login, /auth/me
│   ├── config.py                 # Variables de entorno, logging y limiter centralizados
│   ├── database/
│   │   └── connection.py
│   ├── dependencies/
│   │   ├── database_dependency.py
│   │   └── auth_dependency.py   # get_current_user, get_current_active_user, require_role
│   ├── middlewares/
│   │   └── request_middleware.py # Logging, X-Request-ID y X-Process-Time
│   ├── models/
│   │   ├── user_model.py        # Incluye hashed_password
│   │   ├── device_model.py
│   │   └── loan_model.py
│   ├── schemas/
│   │   ├── auth_schema.py       # UserRegister, UserLogin, Token, TokenData
│   │   ├── user_schema.py
│   │   ├── device_schema.py
│   │   └── loan_schema.py
│   ├── routes/
│   │   ├── user_routes.py
│   │   ├── device_routes.py
│   │   └── loan_routes.py
│   └── services/
│       ├── user_service.py
│       ├── device_service.py
│       └── loan_service.py
├── alembic/
│   └── versions/                # Incluye la migracion de hashed_password
├── tests/
├── .env.example
├── main.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Autenticacion con OAuth2 + JWT

### Flujo general

1. El usuario se registra en `POST /auth/register` con nombre, email, contrasena y rol
2. La contrasena se valida (minimo 8 caracteres, mayuscula, minuscula, numero, sin espacios)
   y se guarda como un hash bcrypt, nunca en texto plano
3. El usuario inicia sesion en `POST /auth/login` con email y contrasena
4. Si las credenciales son correctas, la API devuelve un `access_token` JWT
5. El cliente envia ese token en el header `Authorization: Bearer <token>` en cada peticion
   a una ruta protegida
6. La API decodifica el token, identifica al usuario y valida su rol antes de ejecutar la accion

### Por que la contrasena nunca se guarda en texto plano

Si la base de datos se filtra o alguien obtiene acceso indebido, las contrasenas en texto
plano quedarian expuestas inmediatamente. Con un hash bcrypt, incluso quien tenga acceso a
la base de datos no puede recuperar la contrasena original, solo puede verificar si una
contrasena ingresada coincide con el hash, gracias a `verify_password()`.

### Por que se usa JWT en vez de sesiones tradicionales

Un JWT es auto-contenido: toda la informacion necesaria para validar al usuario (su id y
la fecha de expiracion) viaja dentro del propio token, firmado digitalmente. Esto evita que
el servidor tenga que guardar el estado de cada sesion activa en memoria o en base de datos,
lo que hace que la API sea mas facil de escalar horizontalmente.

---

## Autorizacion por roles

| Rol       | Permisos                                                          |
|-----------|--------------------------------------------------------------------|
| admin     | Acceso total, incluyendo eliminar dispositivos                    |
| support   | Gestionar dispositivos y prestamos, sin poder eliminar dispositivos|
| user      | Consultar informacion y solicitar prestamos                        |

### Rutas protegidas

| Ruta                       | Proteccion           |
|-----------------------------|------------------------|
| GET /users                  | Usuario autenticado    |
| GET /users/{user_id}        | Usuario autenticado    |
| POST /devices                | Admin o support        |
| PUT /devices/{device_id}     | Admin o support        |
| DELETE /devices/{device_id}  | Solo admin             |
| POST /loans                  | Usuario autenticado    |
| PATCH /loans/{loan_id}/return| Admin o support        |
| GET /loans/details           | Admin o support        |

La logica de roles vive en `app/dependencies/auth_dependency.py`. `require_role(*roles)` es
una fabrica de dependencias: genera la validacion exacta que cada ruta necesita sin tener
que escribir una funcion distinta por cada combinacion de roles permitidos.

---

## Middleware personalizado

`RequestLoggingMiddleware` se ejecuta en cada peticion, antes y despues de que la ruta
correspondiente procese la solicitud. Agrega tres cabeceras a toda respuesta:

| Cabecera         | Que contiene                                          |
|-------------------|--------------------------------------------------------|
| X-Request-ID      | Identificador unico de esa peticion especifica          |
| X-Process-Time    | Tiempo en segundos que tomo procesar la peticion        |
| X-App-Name        | Nombre de la aplicacion                                |

Ademas registra en consola, para cada peticion: metodo HTTP, ruta, codigo de estado y
duracion. Esto es la base de cualquier sistema de trazabilidad: si algo falla en produccion,
el `X-Request-ID` permite rastrear esa peticion especifica en los logs sin tener que adivinar
cual fue.

---

## CORS

Configurado con `CORSMiddleware` permitiendo unicamente los origenes de desarrollo:

```python
allow_origins=["http://localhost:5173", "http://localhost:3000"]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

### Por que no usar `allow_origins=["*"]` en produccion

Porque `allow_credentials=True` le dice al navegador que envie cookies y el header
`Authorization` con cada peticion entre dominios. Si se combina con `"*"`, cualquier sitio
web podria disparar peticiones autenticadas usando las credenciales que el navegador de la
victima ya tiene guardadas, sin que la victima lo note. En produccion siempre se debe listar
el dominio exacto del frontend autorizado.

---

## Rate limiting

Implementado con `slowapi`, limita la cantidad de peticiones por IP en una ventana de tiempo:

| Endpoint              | Limite       |
|-------------------------|---------------|
| POST /auth/register     | 3 por minuto  |
| POST /auth/login        | 5 por minuto  |
| GET /users               | 30 por minuto |
| POST /loans              | 10 por minuto |

Si se supera el limite, la API responde con codigo **429 Too Many Requests**. Este mecanismo
protege especialmente el login y el registro, que son los blancos tipicos de ataques de
fuerza bruta o de creacion masiva de cuentas falsas.

---

## Limitaciones conocidas

Durante las pruebas se identifico que el endpoint `POST /auth/register` permite que
cualquier persona se autoasigne el rol `admin` al registrarse, sin ningun tipo de
restriccion. En un sistema en produccion esto es un riesgo serio: el rol de administrador
nunca deberia poder auto-asignarse desde un registro publico, sino ser otorgado manualmente
por otro administrador ya existente, por ejemplo mediante un endpoint adicional protegido
con `require_admin` que permita cambiar el rol de un usuario.

Para esta entrega academica se documenta como limitacion conocida en lugar de corregirse,
ya que la tarea no especifico una restriccion de roles durante el registro, pero queda
identificado como el siguiente paso de hardening natural del proyecto.

---

## Codigos de estado usados

| Codigo | Cuando ocurre                                              |
|--------|-------------------------------------------------------------|
| 200    | Operacion exitosa                                            |
| 201    | Registro creado exitosamente                                 |
| 204    | Eliminacion exitosa, sin cuerpo de respuesta                |
| 400    | Dato duplicado o datos invalidos                              |
| 401    | No autenticado: token ausente, invalido o expirado            |
| 403    | Autenticado pero sin permisos suficientes para la accion       |
| 404    | Usuario, dispositivo o prestamo no encontrado                |
| 409    | Conflicto con el estado actual del recurso                    |
| 422    | Error de validacion (datos o filtros invalidos)               |
| 429    | Demasiadas solicitudes, limite de rate limiting alcanzado     |

---

## Flujo de prueba sugerido

### 1. Registro y login

```json
POST /auth/register
{
  "name": "Ana Perez",
  "email": "ana@mail.com",
  "password": "Clave1234",
  "role": "user"
}
```

```
POST /auth/login
username: ana@mail.com
password: Clave1234
```

![Registro exitoso](image/register_success.png)
![Login exitoso](image/login_success.png)

### 2. Probar contrasena invalida en el registro

```json
{
  "name": "Test",
  "email": "test@mail.com",
  "password": "abc",
  "role": "user"
}
```

Debe responder 422 explicando cuales reglas de seguridad no se cumplieron.

![Error 422 contrasena invalida](image/error_422_password.png)

### 3. Acceder a una ruta protegida sin token

```http
GET /users
```

Sin header Authorization, debe responder 401.

![Error 401 sin token](image/error_401_no_token.png)

### 4. Acceder con un rol sin permisos

Con el token de un usuario rol `user`, intentar `POST /devices`. Debe responder 403.

![Error 403 sin permisos](image/error_403_forbidden.png)

### 5. Confirmar las cabeceras del middleware

En cualquier respuesta, revisar los headers y confirmar la presencia de `X-Request-ID` y
`X-Process-Time`.

![Cabeceras del middleware](image/middleware_headers.png)

### 6. Disparar el rate limit

Ejecutar `POST /auth/login` mas de 5 veces en menos de un minuto. La sexta peticion debe
responder 429.

![Error 429 rate limit](image/error_429_rate_limit.png)

### 7. Confirmar CORS

Desde las DevTools del navegador, pestana Network, revisar que la respuesta incluya el
header `access-control-allow-origin`.

![Header CORS](image/cors_header.png)

---

## Migraciones de Alembic en esta entrega

Se agrego el campo `hashed_password` al modelo `User`. Como ya existian usuarios en la base
de datos, la migracion usa un `server_default` vacio para no romper las filas existentes:

```bash
uv run alembic revision --autogenerate -m "add authentication fields to users"
uv run alembic upgrade head
```

![Migracion de autenticacion](image/alembic_auth_migration.png)

---

## Reflexion

Esta ultima entrega fue donde el proyecto realmente se volvio una API lista para un entorno
real. Hasta antes de esto, cualquiera con la URL podia leer o modificar cualquier dato. Con
OAuth2 y JWT, cada peticion tiene que demostrar quien la hace, y con la autorizacion por
roles, cada usuario solo puede hacer lo que su rol le permite, sin importar que tan bien
formado este su request.

El middleware personalizado y el sistema de logging muestran algo que rara vez se ensena en
los primeros pasos de un curso: en produccion, el codigo que funciona no es suficiente, hay
que poder *observar* lo que esta pasando cuando algo sale mal. Un `X-Request-ID` no evita
errores, pero convierte un error invisible en uno rastreable.

El rate limiting y el CORS bien configurado son recordatorios de que seguridad no es un
checkbox que se marca una vez, es una capa continua de decisiones: cuanta confianza le doy
a un origen, cuantas peticiones le permito a una IP, que tan fuerte exijo que sea una
contrasena. Cada una de esas decisiones tiene un trade-off entre seguridad y comodidad, y
entender ese trade-off es mas importante que memorizar la sintaxis de cada libreria.

