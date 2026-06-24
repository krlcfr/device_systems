from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from typing import Optional

from app.schemas.user_schema import UserCreate, UserUpdate, UserPartialUpdate, UserResponse, UserRole
from app.services.user_service import (
    get_all_users,
    get_user_by_id,
    create_user,
    update_user,
    partial_update_user,
    delete_user,
)
from app.dependencies.database_dependency import get_db
from app.schemas.loan_schema import LoanDetailResponse
from app.services.loan_service import get_loans_by_user

router = APIRouter(prefix="/users", tags=["Users"])


# Funcion auxiliar que agrega las cabeceras personalizadas a cualquier respuesta
def set_custom_headers(response: Response):
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "3.0"


# Devuelve todos los usuarios con filtros opcionales y orden configurable
@router.get(
    "/",
    response_model=list[UserResponse],
    summary="Listar usuarios",
    description="Devuelve la lista de usuarios. Permite filtrar por rol y estado, y ordenar por nombre o fecha de creacion.",
    response_description="Lista de usuarios encontrados",
)
def get_users(
    response: Response,
    db: Session = Depends(get_db),
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    order_by: Optional[str] = "name",
):
    set_custom_headers(response)
    return get_all_users(db, role=role, is_active=is_active, order_by=order_by)


# Devuelve un usuario especifico por su id
@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Consultar usuario por ID",
    description="Busca y devuelve un usuario por su ID. Si no existe responde con 404.",
    response_description="Usuario encontrado",
)
def get_user(user_id: int, response: Response, db: Session = Depends(get_db)):
    set_custom_headers(response)
    return get_user_by_id(db, user_id)


# Crea un nuevo usuario en la base de datos
@router.post(
    "/",
    response_model=UserResponse,
    status_code=201,
    summary="Crear usuario",
    description="Registra un nuevo usuario. Valida formato de email, rol permitido y que el correo no este duplicado.",
    response_description="Usuario creado exitosamente",
)
def post_user(user: UserCreate, response: Response, db: Session = Depends(get_db)):
    set_custom_headers(response)
    return create_user(db, user)


# Reemplaza completamente un usuario existente
@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario completo",
    description="Reemplaza todos los campos de un usuario existente. Si no existe responde con 404.",
    response_description="Usuario actualizado",
)
def put_user(user_id: int, data: UserUpdate, response: Response, db: Session = Depends(get_db)):
    set_custom_headers(response)
    return update_user(db, user_id, data)


# Actualiza parcialmente un usuario, solo los campos que el cliente manda
@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario parcialmente",
    description="Modifica solo los campos enviados. Si no se envia ningun campo responde con 400. Si no existe responde con 404.",
    response_description="Usuario actualizado parcialmente",
)
def patch_user(user_id: int, data: UserPartialUpdate, response: Response, db: Session = Depends(get_db)):
    set_custom_headers(response)
    return partial_update_user(db, user_id, data)


# Elimina un usuario existente y responde con 204 sin cuerpo
@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Eliminar usuario",
    description="Elimina un usuario por su ID. Si no existe responde con 404. No retorna cuerpo en la respuesta.",
    response_description="Usuario eliminado exitosamente",
)
def remove_user(user_id: int, db: Session = Depends(get_db)):
    delete_user(db, user_id)


# Devuelve los prestamos asociados a un usuario, con detalle del dispositivo
@router.get(
    "/{user_id}/loans",
    response_model=list[LoanDetailResponse],
    tags=["Loans"],
    summary="Prestamos de un usuario",
    description="Devuelve el historial de prestamos de un usuario especifico, con la informacion del dispositivo de cada prestamo. Si el usuario no existe responde con 404.",
    response_description="Lista de prestamos del usuario",
)
def get_user_loans(user_id: int, response: Response, db: Session = Depends(get_db)):
    set_custom_headers(response)
    return get_loans_by_user(db, user_id)
