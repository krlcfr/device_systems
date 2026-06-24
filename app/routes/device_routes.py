from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from typing import Optional

from app.schemas.device_schema import DeviceCreate, DeviceUpdate, DevicePartialUpdate, DeviceResponse
from app.services.device_service import (
    get_all_devices,
    get_device_by_id,
    create_device,
    update_device,
    partial_update_device,
    delete_device,
)
from app.dependencies.database_dependency import get_db
from app.schemas.loan_schema import LoanDetailResponse
from app.services.loan_service import get_loans_by_device

router = APIRouter(prefix="/devices", tags=["Devices"])


# Funcion auxiliar que agrega las cabeceras personalizadas a cualquier respuesta
def set_custom_headers(response: Response):
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "4.0"


# Devuelve todos los dispositivos con filtros opcionales
@router.get(
    "/",
    response_model=list[DeviceResponse],
    summary="Listar dispositivos",
    description="Devuelve la lista de dispositivos. Permite filtrar por tipo, disponibilidad, marca y busqueda libre.",
    response_description="Lista de dispositivos encontrados",
)
def get_devices(
    response: Response,
    db: Session = Depends(get_db),
    device_type: Optional[str] = None,
    is_available: Optional[bool] = None,
    brand: Optional[str] = None,
    search: Optional[str] = None,
):
    set_custom_headers(response)
    return get_all_devices(db, device_type=device_type, is_available=is_available, brand=brand, search=search)


# Devuelve un dispositivo especifico por su id
@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Consultar dispositivo por ID",
    description="Busca y devuelve un dispositivo por su ID. Si no existe responde con 404.",
    response_description="Dispositivo encontrado",
)
def get_device(device_id: int, response: Response, db: Session = Depends(get_db)):
    set_custom_headers(response)
    return get_device_by_id(db, device_id)


# Crea un nuevo dispositivo
@router.post(
    "/",
    response_model=DeviceResponse,
    status_code=201,
    summary="Crear dispositivo",
    description="Registra un nuevo dispositivo. Valida que el numero de serie no este duplicado.",
    response_description="Dispositivo creado exitosamente",
)
def post_device(device: DeviceCreate, response: Response, db: Session = Depends(get_db)):
    set_custom_headers(response)
    return create_device(db, device)


# Reemplaza completamente un dispositivo existente
@router.put(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Actualizar dispositivo completo",
    description="Reemplaza todos los campos de un dispositivo existente. Si no existe responde con 404.",
    response_description="Dispositivo actualizado",
)
def put_device(device_id: int, data: DeviceUpdate, response: Response, db: Session = Depends(get_db)):
    set_custom_headers(response)
    return update_device(db, device_id, data)


# Actualiza parcialmente un dispositivo
@router.patch(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Actualizar dispositivo parcialmente",
    description="Modifica solo los campos enviados. Si no se envia ningun campo responde con 400. Si no existe responde con 404.",
    response_description="Dispositivo actualizado parcialmente",
)
def patch_device(device_id: int, data: DevicePartialUpdate, response: Response, db: Session = Depends(get_db)):
    set_custom_headers(response)
    return partial_update_device(db, device_id, data)


# Elimina un dispositivo existente
@router.delete(
    "/{device_id}",
    status_code=204,
    summary="Eliminar dispositivo",
    description="Elimina un dispositivo por su ID. Si no existe responde con 404.",
    response_description="Dispositivo eliminado exitosamente",
)
def remove_device(device_id: int, db: Session = Depends(get_db)):
    delete_device(db, device_id)


# Devuelve el historial de prestamos de un dispositivo, con detalle del usuario
@router.get(
    "/{device_id}/loans",
    response_model=list[LoanDetailResponse],
    tags=["Loans"],
    summary="Historial de prestamos de un dispositivo",
    description="Devuelve todos los prestamos registrados para un dispositivo, con la informacion del usuario de cada prestamo. Si el dispositivo no existe responde con 404.",
    response_description="Lista de prestamos del dispositivo",
)
def get_device_loans(device_id: int, response: Response, db: Session = Depends(get_db)):
    set_custom_headers(response)
    return get_loans_by_device(db, device_id)
