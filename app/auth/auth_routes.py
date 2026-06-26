from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config import limiter
from app.schemas.auth_schema import UserRegister, Token
from app.schemas.user_schema import UserResponse
from app.auth.auth_service import register_user, authenticate_user
from app.auth.security import create_access_token
from app.dependencies.database_dependency import get_db
from app.dependencies.auth_dependency import get_current_user
from app.models.user_model import User

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Registrar usuario",
    description="Crea un usuario nuevo validando nombre, email unico, contrasena segura y rol permitido. La contrasena se guarda siempre hasheada.",
    response_description="Usuario registrado exitosamente",
)
@limiter.limit("3/minute")
def register(request: Request, data: UserRegister, db: Session = Depends(get_db)):
    return register_user(db, data)


@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesion",
    description="Autentica al usuario con email y contrasena, y devuelve un token JWT de acceso.",
    response_description="Token de acceso generado",
)
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contrasena incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Usuario autenticado",
    description="Devuelve la informacion del usuario propietario del token enviado. No expone la contrasena.",
    response_description="Datos del usuario autenticado",
)
def me(current_user: User = Depends(get_current_user)):
    return current_user
