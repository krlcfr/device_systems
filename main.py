from fastapi import FastAPI
from app.routes.user_routes import router as user_router
from app.database.connection import create_tables

description = """
## device_systems API

API REST para la gestion de usuarios del sistema device_systems.

### Que puedes hacer con esta API

- **Listar** todos los usuarios con filtros por rol y estado
- **Consultar** un usuario especifico por su ID
- **Crear** nuevos usuarios con validacion automatica de datos
- **Actualizar** un usuario completo con PUT
- **Modificar** campos especificos de un usuario con PATCH
- **Eliminar** usuarios existentes

### Codigos de estado

| Codigo | Significado |
|--------|-------------|
| 200 | Operacion exitosa |
| 201 | Usuario creado |
| 204 | Usuario eliminado |
| 400 | Datos invalidos o correo duplicado |
| 404 | Usuario no encontrado |
| 422 | Error de validacion Pydantic |
"""

# Instancia principal de la aplicacion con metadatos completos para Swagger y ReDoc
app = FastAPI(
    title="device_systems",
    description=description,
    version="3.0",
    contact={
        "name": "Arthur Pendragon",
        "email": "arthur@mail.com",
    },
    license_info={
        "name": "MIT",
    },
)

# Crea las tablas en la base de datos al iniciar la aplicacion si no existen todavia
create_tables()

# Conecta las rutas de usuarios a la aplicacion principal
app.include_router(user_router)


# Endpoint raiz, solo sirve para confirmar que el servidor esta corriendo
@app.get("/", tags=["Root"])
def root():
    return {"message": "device_systems API running", "version": "3.0"}
