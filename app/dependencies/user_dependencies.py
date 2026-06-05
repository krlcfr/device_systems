from fastapi import HTTPException, Header
from app.services.user_service import get_user_by_id
from app.data.users_db import users_db


# Busca el usuario por id y lo devuelve listo para usar en la ruta
# si no existe el servicio lanza el 404 automaticamente
def get_user_or_404(user_id: int):
    return get_user_by_id(user_id)


# Verifica que el email no este registrado en otro usuario
def validate_unique_email(email: str, exclude_id: int = None):
    for user in users_db:
        if user["email"] == email and user["id"] != exclude_id:
            raise HTTPException(status_code=400, detail="El correo ya esta registrado")


# Verifica que el rol que llega sea uno de los permitidos
def validate_role(role: str):
    allowed = ["admin", "support", "user"]
    if role not in allowed:
        raise HTTPException(status_code=400, detail=f"Rol no permitido. Los roles validos son: {', '.join(allowed)}")


# Devuelve la configuracion general de la API
def get_api_config():
    return {
        "app_name": "device_systems",
        "version": "2.0",
        "description": "API REST para gestion de usuarios",
    }


# Simula una autenticacion basica mediante una cabecera personalizada
# el cliente debe mandar el header x-api-key con el valor correcto
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != "device-systems-2024":
        raise HTTPException(status_code=401, detail="API key invalida")
