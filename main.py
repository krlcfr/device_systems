from fastapi import FastAPI
from app.routes.user_routes import router as user_router

# Instancia principal de la aplicacion, todos los endpoints se registran aqui.

app = FastAPI(
    title="device_systems",
    version="1.0",
    description="API REST para gestion de usuarios del sistema device_systems",
)

# Conecta las rutas de usuarios a la aplicacion principal.

app.include_router(user_router)


# Endpoint raiz, solo sirve para confirmar que el servidor esta corriendo.

@app.get("/")
def root():
    return {"message": "device_systems API running", "version": "1.0"}

