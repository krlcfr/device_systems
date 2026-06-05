# device_systems

API REST construida con FastAPI y Python para gestionar usuarios del sistema device_systems.
Esta es la version 2.0 del proyecto, donde se completo el CRUD, se organizo mejor el codigo
y se aplico manejo de errores, documentacion automatica y Dependency Injection.

---

## Que hace este proyecto

device_systems permite crear, consultar, actualizar y eliminar usuarios de un sistema.
Cada usuario tiene nombre, correo, rol y estado. La API valida automaticamente los datos,
responde con codigos HTTP correctos segun la operacion y organiza su logica en capas
separadas para que el codigo sea limpio y facil de mantener.

---

## Tecnologias utilizadas

- Python 3.13
- FastAPI
- Pydantic v2
- Uvicorn
- uv como gestor de paquetes

---

## Como instalarlo

```bash
git clone <url-del-repositorio>
cd device_systems
uv sync
```

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
│   ├── data/
│   │   └── users_db.py         # Base de datos simulada en memoria
│   ├── dependencies/
│   │   └── user_dependencies.py # Funciones reutilizables con Depends()
│   ├── routes/
│   │   └── user_routes.py      # Definicion de endpoints
│   ├── schemas/
│   │   └── user_schema.py      # Modelos Pydantic de entrada y salida
│   └── services/
│       └── user_service.py     # Logica de negocio
├── main.py
├── pyproject.toml
└── README.md
```

Cada carpeta tiene una responsabilidad unica:

- **data**: los datos viven aqui, cualquier modulo que los necesite los importa desde aca
- **dependencies**: funciones que se reutilizan en multiples endpoints usando Depends()
- **routes**: solo define los endpoints y delega el trabajo al servicio
- **schemas**: define la forma que tienen los datos que entran y salen
- **services**: aqui vive toda la logica, las rutas solo la llaman

---

## Endpoints disponibles

| Metodo | Ruta              | Que hace                             | Codigo exitoso |
|--------|-------------------|--------------------------------------|----------------|
| GET    | /                 | Confirma que el servidor esta vivo   | 200            |
| GET    | /users            | Trae todos los usuarios              | 200            |
| GET    | /users?role=admin | Filtra usuarios por rol              | 200            |
| GET    | /users?is_active=true | Filtra por estado               | 200            |
| GET    | /users/{user_id}  | Trae un usuario por su ID            | 200            |
| POST   | /users            | Crea un usuario nuevo                | 201            |
| PUT    | /users/{user_id}  | Reemplaza un usuario completo        | 200            |
| PATCH  | /users/{user_id}  | Modifica campos especificos          | 200            |
| DELETE | /users/{user_id}  | Elimina un usuario                   | 204            |

---

## Codigos de estado usados

| Codigo | Cuando ocurre                                      |
|--------|----------------------------------------------------|
| 200    | Operacion exitosa                                  |
| 201    | Usuario creado exitosamente                        |
| 204    | Usuario eliminado, sin cuerpo de respuesta         |
| 400    | Correo duplicado o PATCH enviado sin campos        |
| 401    | API key invalida                                   |
| 404    | Usuario no encontrado                              |
| 422    | Datos invalidos segun las reglas de Pydantic       |

---

## Ejemplos de peticiones y respuestas

### GET /users

```http
GET http://127.0.0.1:8000/users
```

![GET /users](image/get_users.png)

---

### GET /users/{user_id}

```http
GET http://127.0.0.1:8000/users/1
```

![GET /users/id](image/get_user_by_id.png)

---

### GET /users?role=admin

```http
GET http://127.0.0.1:8000/users?role=admin
```

![GET por rol](image/get_users_by_role.png)

---

### GET /users?is_active=false

```http
GET http://127.0.0.1:8000/users?is_active=false
```

![GET por estado](image/get_users_by_status.png)

---

### POST /users

Body:
```json
{
  "name": "Aleja Torres",
  "email": "aleja@mail.com",
  "role": "user",
  "is_active": true
}
```

Respuesta exitosa (201):
```json
{
  "id": 5,
  "name": "Aleja Torres",
  "email": "aleja@mail.com",
  "role": "user",
  "is_active": true
}
```

![POST exitoso](image/post_user_success.png)

---

### PUT /users/{user_id}

Body:
```json
{
  "name": "Arthur Updated",
  "email": "arthur_updated@mail.com",
  "role": "admin",
  "is_active": true
}
```

![PUT usuario](image/put_user.png)

---

### PATCH /users/{user_id}

Body (solo los campos que quieres cambiar):
```json
{
  "role": "support"
}
```

![PATCH usuario](image/patch_user.png)

---

### DELETE /users/{user_id}

```http
DELETE http://127.0.0.1:8000/users/1
```

Responde con 204 y sin cuerpo.

![DELETE usuario](image/delete_user.png)

---

## Errores controlados

### Usuario no encontrado (404)

```json
{
  "detail": "Usuario no encontrado"
}
```

![Error 404](image/error_404.png)

---

### Correo duplicado (400)

```json
{
  "detail": "El correo ya esta registrado"
}
```

![Error 400 duplicado](image/error_400_duplicate.png)

---

### PATCH sin campos (400)

```json
{
  "detail": "Debes enviar al menos un campo para actualizar"
}
```

![Error 400 patch vacio](image/error_400_patch.png)

---

### Datos invalidos (422)

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "name"],
      "msg": "String should have at least 3 characters"
    }
  ]
}
```

![Error 422](image/error_422.png)

---

## Capturas de Swagger UI y ReDoc

![Swagger UI](image/swagger_ui.png)

![ReDoc](image/redoc.png)

![Cabeceras personalizadas](image/custom_headers.png)

---

## Como funciona la Dependency Injection

En lugar de repetir logica en cada endpoint, se crean funciones en `user_dependencies.py`
que FastAPI ejecuta automaticamente antes de entrar al endpoint usando `Depends()`.

Por ejemplo, en lugar de buscar el usuario y lanzar el 404 en cada endpoint que lo necesite,
se declara una sola dependencia:

```python
def get_user_or_404(user_id: int):
    return get_user_by_id(user_id)
```

Y en la ruta se usa asi:

```python
@router.get("/{user_id}")
def get_user(user: dict = Depends(get_user_or_404)):
    return user
```

FastAPI resuelve la dependencia, busca el usuario, y si no existe lanza el 404 antes de
entrar al endpoint. Si existe, lo pasa directo como parametro. Esto evita repetir codigo
y mantiene las rutas limpias.

---

## Como se maneja los errores

Todos los errores se lanzan con `HTTPException` desde el servicio o la dependencia correspondiente.
FastAPI los captura y los convierte automaticamente en respuestas JSON con el codigo correcto.

Los casos controlados son:

- Usuario no encontrado en GET, PUT, PATCH y DELETE: responde 404
- Correo duplicado en POST y PUT: responde 400
- PATCH enviado sin ningun campo: responde 400
- Datos que no cumplen las reglas de Pydantic: responde 422 automaticamente

---

## Reflexion

Pasar de una API basica a esta version fue un salto real en organizacion y robustez.
Separar la logica en capas hace que cada archivo tenga una responsabilidad clara y que
agregar o cambiar algo no rompa todo lo demas. La Dependency Injection con Depends() es
una de las funcionalidades mas utiles de FastAPI porque elimina codigo repetido y centraliza
validaciones que se usan en varios endpoints. El manejo de errores con HTTPException hace
que la API responda siempre de forma predecible, lo cual es clave cuando otros sistemas
o frontends consumen la API.

