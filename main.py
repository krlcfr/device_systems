from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import limiter, logger
from app.routes.user_routes import router as user_router
from app.routes.device_routes import router as device_router
from app.routes.loan_routes import router as loan_router
from app.auth.auth_routes import router as auth_router
from app.database.connection import create_tables
from app.middlewares.request_middleware import RequestLoggingMiddleware

logger.info("Iniciando device_systems API")

description = """
## device_systems API

API REST segura para gestion de usuarios, dispositivos y prestamos del sistema device_systems.

### Que puedes hacer con esta API

- **Usuarios**: crear, listar, consultar, actualizar y eliminar
- **Dispositivos**: crear, listar con filtros avanzados, actualizar y eliminar
- **Prestamos**: crear, listar, devolver, y consultar con informacion relacionada
- **Consultas con joins**: ver prestamos junto con los datos del usuario y del dispositivo
- **Filtros avanzados**: busqueda flexible con ilike, filtros combinados con and_
- **Autenticacion**: registro y login con OAuth2 + JWT
- **Seguridad**: rate limiting, middleware personalizado, CORS controlado

### Recursos disponibles

- /auth — autenticacion y registro
- /users — gestion de usuarios
- /devices — gestion de dispositivos
- /loans — gestion de prestamos

### Codigos de estado

| Codigo | Significado |
|--------|-------------|
| 200 | Operacion exitosa |
| 201 | Registro creado |
| 204 | Eliminacion exitosa |
| 400 | Datos invalidos o dato duplicado |
| 401 | No autenticado |
| 403 | No autorizado (permisos insuficientes) |
| 404 | Recurso no encontrado |
| 409 | Conflicto con el estado actual del recurso |
| 422 | Error de validacion |
| 429 | Demasiadas solicitudes (rate limit) |
"""

# ---------------------------------------------------------------------------
# Instancia principal de la aplicacion con metadatos completos
# ---------------------------------------------------------------------------
app = FastAPI(
    title="device_systems API",
    description=description,
    version="4.0.0",
    contact={
        "name": "Arthur Pendragon",
        "email": "arthur@mail.com",
    },
    license_info={
        "name": "MIT",
    },
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
    },
)

# ---------------------------------------------------------------------------
# Creacion de tablas (solo si no existen)
# ---------------------------------------------------------------------------
create_tables()

# ---------------------------------------------------------------------------
# Middleware personalizado (debe ir ANTES de CORS para medir tiempos reales)
# ---------------------------------------------------------------------------
app.add_middleware(RequestLoggingMiddleware)

# ---------------------------------------------------------------------------
# Configuracion CORS para desarrollo
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Rate limiting - Integracion con slowapi
# ---------------------------------------------------------------------------
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(device_router)
app.include_router(loan_router)


# ---------------------------------------------------------------------------
# Endpoint raiz
# ---------------------------------------------------------------------------
@app.get("/", tags=["Root"])
def root():
    return {"message": "device_systems API running", "version": "4.0.0"}
