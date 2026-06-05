from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum


# Lista cerrada de roles validos, si llega cualquier otro valor Pydantic lo rechaza
class UserRole(str, Enum):
    admin = "admin"
    support = "support"
    user = "user"


# Molde de entrada, define lo que el cliente debe mandar al crear un usuario
class UserCreate(BaseModel):
    # Minimo 3 caracteres
    name: str = Field(min_length=3)
    # Pydantic valida que tenga formato de email real
    email: EmailStr
    # Solo acepta los valores del Enum de arriba
    role: UserRole
    # Si no lo mandan llega como True por defecto
    is_active: bool = Field(default=True)


# Molde de entrada para PUT, igual que UserCreate pero deja claro que es una actualizacion completa
class UserUpdate(BaseModel):
    name: str = Field(min_length=3)
    email: EmailStr
    role: UserRole
    is_active: bool


# Molde de entrada para PATCH, todos los campos son opcionales
# el cliente manda solo lo que quiere cambiar
class UserPartialUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


# Molde de salida, define lo que la API devuelve
# incluye el id que asigna el sistema, el cliente nunca lo manda
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool
