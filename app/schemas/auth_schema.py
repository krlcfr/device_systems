from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from app.schemas.user_schema import UserRole


# Valida que la contraseña cumpla con las reglas minimas de seguridad
# se reutiliza tanto en UserRegister como en cualquier otro lugar que reciba contraseñas
def validate_password_strength(password: str) -> str:
    if len(password) < 8:
        raise ValueError("La contrasena debe tener minimo 8 caracteres")

    if " " in password:
        raise ValueError("La contrasena no puede contener espacios en blanco")

    if not any(char.isupper() for char in password):
        raise ValueError("La contrasena debe tener al menos una mayuscula")

    if not any(char.islower() for char in password):
        raise ValueError("La contrasena debe tener al menos una minuscula")

    if not any(char.isdigit() for char in password):
        raise ValueError("La contrasena debe tener al menos un numero")

    return password


# Molde de entrada para registrar un usuario nuevo
class UserRegister(BaseModel):
    name: str = Field(min_length=3, description="Nombre completo del usuario")
    email: EmailStr = Field(description="Correo electronico, debe ser unico")
    password: str = Field(min_length=8, description="Contrasena segura del usuario")
    role: UserRole = Field(default=UserRole.user, description="Rol del usuario")

    # field_validator corre la validacion personalizada sobre el campo password
    @field_validator("password")
    @classmethod
    def check_password_strength(cls, value: str) -> str:
        return validate_password_strength(value)


# Molde de entrada para iniciar sesion
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Molde de salida del login, lo que recibe el cliente despues de autenticarse
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Datos que se extraen del token decodificado, uso interno de las dependencias
class TokenData(BaseModel):
    user_id: int
    email: str
    role: str

    model_config = ConfigDict(from_attributes=True)
