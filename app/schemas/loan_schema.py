from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


# Lista cerrada de estados validos para un prestamo
# usarla como tipo en los filtros hace que un valor invalido responda 422 automaticamente
class LoanStatus(str, Enum):
    active = "active"
    returned = "returned"
    overdue = "overdue"


# Molde de entrada para crear un prestamo
# solo se necesita el id del usuario y el del dispositivo, lo demas lo calcula el sistema
class LoanCreate(BaseModel):
    user_id: int
    device_id: int


# Molde de entrada para actualizar un prestamo manualmente
class LoanUpdate(BaseModel):
    status: LoanStatus
    return_date: Optional[datetime] = None


# Molde de salida basico, sin datos anidados de usuario o dispositivo
class LoanResponse(BaseModel):
    id: int
    user_id: int
    device_id: int
    loan_date: datetime
    return_date: Optional[datetime]
    status: str

    model_config = {"from_attributes": True}


# Version resumida del usuario, solo los datos relevantes para mostrar dentro de un prestamo
class UserBasicInfo(BaseModel):
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}


# Version resumida del dispositivo, solo los datos relevantes para mostrar dentro de un prestamo
class DeviceBasicInfo(BaseModel):
    id: int
    name: str
    serial_number: str
    device_type: str

    model_config = {"from_attributes": True}


# Molde de salida detallado, incluye los datos del usuario y del dispositivo relacionados
# se usa en los endpoints de consultas con joins
class LoanDetailResponse(BaseModel):
    id: int
    status: str
    loan_date: datetime
    return_date: Optional[datetime]
    user: UserBasicInfo
    device: DeviceBasicInfo

    model_config = {"from_attributes": True}
