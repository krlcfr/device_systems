from fastapi import APIRouter, Depends, Response
from typing import Optional

from app.schemas.user_schema import UserCreate, UserUpdate, UserPartialUpdate, UserResponse, UserRole
from app.services.user_service import (
    get_all_users,
    create_user,
    update_user,
    partial_update_user,
    delete_user,
)
from app.dependencies.user_dependencies import get_user_or_404

router = APIRouter(prefix="/users", tags=["Users"])


# Funcion auxiliar que agrega las cabeceras personalizadas a cualquier respuesta
def set_custom_headers(response: Response):
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "2.0"


# Devuelve todos los usuarios, con filtros opcionales por rol y estado
@router.get(
    "/",
    response_model=list[UserResponse],
    summary="Listar usuarios",
    description="Devuelve la lista completa de usuarios. Permite filtrar por rol y por estado activo o inactivo.",
    response_description="Lista de usuarios encontrados",
)
def get_users(response: Response, role: Optional[UserRole] = None, is_active: Optional[bool] = None):
    set_custom_headers(response)
    return get_all_users(role=role, is_active=is_active)


# Devuelve un usuario especifico por su id usando la dependencia get_user_or_404
@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Consultar usuario por ID",
    description="Busca y devuelve un usuario por su ID. Si no existe responde con 404.",
    response_description="Usuario encontrado",
)
def get_user(response: Response, user: dict = Depends(get_user_or_404)):
    set_custom_headers(response)
    return user


# Crea un nuevo usuario validando los datos de entrada con Pydantic
@router.post(
    "/",
    response_model=UserResponse,
    status_code=201,
    summary="Crear usuario",
    description="Registra un nuevo usuario. Valida formato de email, rol permitido y que el correo no este duplicado.",
    response_description="Usuario creado exitosamente",
)
def post_user(user: UserCreate, response: Response):
    set_custom_headers(response)
    return create_user(user)


# Reemplaza completamente un usuario existente
@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario completo",
    description="Reemplaza todos los campos de un usuario existente. Requiere enviar todos los campos. Si no existe responde con 404.",
    response_description="Usuario actualizado",
)
def put_user(user_id: int, data: UserUpdate, response: Response):
    set_custom_headers(response)
    return update_user(user_id, data)


# Actualiza parcialmente un usuario, solo los campos que el cliente manda
@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario parcialmente",
    description="Modifica solo los campos enviados. Si no se envia ningun campo responde con 400. Si no existe responde con 404.",
    response_description="Usuario actualizado parcialmente",
)
def patch_user(user_id: int, data: UserPartialUpdate, response: Response):
    set_custom_headers(response)
    return partial_update_user(user_id, data)


# Elimina un usuario existente y responde con 204 sin cuerpo de respuesta
@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Eliminar usuario",
    description="Elimina un usuario por su ID. Si no existe responde con 404. No retorna cuerpo en la respuesta.",
    response_description="Usuario eliminado exitosamente",
)
def remove_user(user_id: int):
    delete_user(user_id)
