from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# Molde de entrada para crear un dispositivo
class DeviceCreate(BaseModel):
    name: str = Field(min_length=3)
    serial_number: str = Field(min_length=3)
    device_type: str = Field(min_length=3)
    brand: Optional[str] = None
    is_available: bool = Field(default=True)


# Molde de entrada para PUT, reemplaza el dispositivo completo
class DeviceUpdate(BaseModel):
    name: str = Field(min_length=3)
    serial_number: str = Field(min_length=3)
    device_type: str = Field(min_length=3)
    brand: Optional[str] = None
    is_available: bool


# Molde de entrada para PATCH, todos los campos son opcionales
class DevicePartialUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3)
    serial_number: Optional[str] = Field(default=None, min_length=3)
    device_type: Optional[str] = Field(default=None, min_length=3)
    brand: Optional[str] = None
    is_available: Optional[bool] = None


# Molde de salida, define lo que la API devuelve
class DeviceResponse(BaseModel):
    id: int
    name: str
    serial_number: str
    device_type: str
    brand: Optional[str]
    is_available: bool
    created_at: datetime

    model_config = {"from_attributes": True}
