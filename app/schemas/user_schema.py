from pydantic import BaseModel, EmailStr, Field
from enum import Enum


# Lista cerrada de roles validos.
class UserRole(str, Enum):
    admin = "admin"
    support = "support"
    user = "user"


# Entrada, define lo que el cliente debe mandar al crear un usuario.
class UserCreate(BaseModel):
    name: str = Field(min_length=3)
    email: EmailStr
    role: UserRole
    is_active: bool = Field(default=True)


# Salida, define lo que la API devuelve.
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool
