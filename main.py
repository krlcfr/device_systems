from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.user_routes import router as user_router
from app.routes.device_routes import router as device_router
from app.routes.loan_routes import router as loan_router
from app.auth.auth_routes import router as auth_router
from app.database.connection import create_tables

description = """
## device_systems API

API REST para la gestion de usuarios, dispositivos y prestamos del sistema device_systems.

### Que puedes hacer con esta API

- **Usuarios**: crear, listar, consultar, actualizar y eliminar
- **Dispositivos**: crear, listar con filtros avanzados, actualizar y eliminar
- **Prestamos**: crear, listar, devolver, y consultar con informacion relacionada
- **Consultas con joins**: ver prestamos junto con los datos del usuario y del dispositivo
- **Filtros avanzados**: busqueda flexible con ilike, filtros combinados con and_

### Recursos disponibles

- `/users` — gestion de usuarios
- `/devices` — gestion de dispositivos
- `/loans` — gestion de prestamos

### Codigos de estado

| Codigo | Significado |
|--------|-------------|
| 200 | Operacion exitosa |
| 201 | Registro creado |
| 204 | Eliminacion exitosa |
| 400 | Datos invalidos o dato duplicado |
| 404 | Recurso no encontrado |
| 409 | Conflicto con el estado actual del recurso |
| 422 | Error de validacion |
"""

# Instancia principal de la aplicacion con metadatos completos para Swagger y ReDoc
app = FastAPI(
    title="device_systems",
    description=description,
    version="4.0",
    contact={
        "name": "Arthur Pendragon",
        "email": "arthur@mail.com",
    },
    license_info={
        "name": "MIT",
    },
)

# Crea las tablas en la base de datos al iniciar la aplicacion si no existen todavia
# las tablas ya gestionadas por Alembic tambien pasan por aqui sin problema
create_tables()

# Configuracion CORS para desarrollo
# allow_origins lista los frontends autorizados a consumir esta API desde el navegador
# allow_credentials en True permite que el frontend envie cookies o el header Authorization
# en produccion estos origenes deben ser los dominios reales del frontend, nunca "*"
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conecta las rutas de usuarios, dispositivos y prestamos a la aplicacion principal
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(device_router)
app.include_router(loan_router)


# Endpoint raiz, solo sirve para confirmar que el servidor esta corriendo
@app.get("/", tags=["Root"])
def root():
    return {"message": "device_systems API running", "version": "4.0"}
