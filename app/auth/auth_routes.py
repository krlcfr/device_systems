from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.schemas.auth_schema import UserRegister, Token
from app.schemas.user_schema import UserResponse
from app.auth.auth_service import register_user, authenticate_user
from app.auth.security import create_access_token
from app.dependencies.database_dependency import get_db
from app.dependencies.auth_dependency import get_current_user
from app.models.user_model import User

router = APIRouter(prefix="/auth", tags=["Auth"])


# Registra un usuario nuevo con contraseña hasheada
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Registrar usuario",
    description="Crea un usuario nuevo validando nombre, email unico, contrasena segura y rol permitido. La contrasena se guarda siempre hasheada.",
    response_description="Usuario registrado exitosamente",
)
def register(data: UserRegister, db: Session = Depends(get_db)):
    return register_user(db, data)


# Autentica al usuario y devuelve un token JWT
# OAuth2PasswordRequestForm exige los campos username y password en un formulario
# usamos el campo username para recibir el email del usuario
@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesion",
    description="Autentica al usuario con email y contrasena, y devuelve un token JWT de acceso.",
    response_description="Token de acceso generado",
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contrasena incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # El sub del token es el id del usuario, asi get_current_user puede recuperarlo despues
    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}


# Devuelve los datos del usuario autenticado a partir del token
@router.get(
    "/me",
    response_model=UserResponse,
    summary="Usuario autenticado",
    description="Devuelve la informacion del usuario propietario del token enviado. No expone la contrasena.",
    response_description="Datos del usuario autenticado",
)
def me(current_user: User = Depends(get_current_user)):
    return current_user
