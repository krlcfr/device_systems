from fastapi import APIRouter, HTTPException, Response
from app.schemas.user_schema import UserCreate, UserResponse, UserRole
from typing import Optional

router = APIRouter()

# Lista en memoria que actua como base de datos temporal
fake_db = [
    {"id": 1, "name": "Arthur Pendragon", "email": "arthur@mail.com", "role": "admin", "is_active": True},
    {"id": 2, "name": "Santiago Pinzon", "email": "santiago@mail.com", "role": "support", "is_active": True},
    {"id": 3, "name": "Laura Mesa", "email": "laura@mail.com", "role": "user", "is_active": False},
    {"id": 4, "name": "Carlos Rios", "email": "carlos@mail.com", "role": "user", "is_active": True},
]

# Funcion auxiliar que agrega las cabeceras personalizadas a cualquier respuesta
def set_custom_headers(response: Response):
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"


# Devuelve todos los usuarios, con filtros opcionales por rol y estado
@router.get("/users", response_model=list[UserResponse])
def get_users(response: Response, role: Optional[UserRole] = None, is_active: Optional[bool] = None):
    set_custom_headers(response)
    result = fake_db

    # Si mandan el filtro de rol, filtra por ese rol
    if role is not None:
        result = [u for u in result if u["role"] == role.value]

    # Si mandan el filtro de estado, filtra activos o inactivos
    if is_active is not None:
        result = [u for u in result if u["is_active"] == is_active]

    return result


# Devuelve un usuario especifico por su id
# Si no existe lanza un error 404
@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, response: Response):
    set_custom_headers(response)
    for user in fake_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")


# Crea un nuevo usuario y lo agrega a la lista
# Rechaza el registro si el email ya existe en la base de datos
@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, response: Response):
    set_custom_headers(response)
    for existing in fake_db:
        if existing["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")

    # Genera el id sumando 1 al ultimo id de la lista
    new_id = fake_db[-1]["id"] + 1

    new_user = {
        "id": new_id,
        "name": user.name,
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active,
    }

    fake_db.append(new_user)

    return new_user
