from fastapi import FastAPI
from app.routes.user_routes import router as user_router

# Metadatos que aparecen en el Swagger y en el ReDoc
# description acepta markdown para darle formato a la pagina de documentacion
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
| 401 | API key invalida |
| 404 | Usuario no encontrado |
| 422 | Error de validacion Pydantic |
"""

# Instancia principal de la aplicacion con metadatos completos para Swagger y ReDoc
app = FastAPI(
    title="device_systems",
    description=description,
    version="2.0",
    contact={
        "name": "Arthur",
        "email": "arthur@mail.com",
    },
    license_info={
        "name": "MIT",
    },
)

# Conecta las rutas de usuarios a la aplicacion principal
app.include_router(user_router)


# Endpoint raiz, solo sirve para confirmar que el servidor esta corriendo
@app.get("/", tags=["Root"])
def root():
    return {"message": "device_systems API running", "version": "2.0"}
