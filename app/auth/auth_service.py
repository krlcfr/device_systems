from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.schemas.auth_schema import UserRegister
from app.services.user_service import get_user_by_email
from app.auth.security import get_password_hash, verify_password


# Registra un usuario nuevo con contraseña hasheada
# verifica que el email no este registrado antes de insertar
def register_user(db: Session, data: UserRegister) -> User:
    existing = get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="El correo ya esta registrado")

    new_user = User(
        name=data.name,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role=data.role.value,
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Verifica las credenciales de un usuario
# devuelve el usuario si las credenciales son correctas, None si no lo son
def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user
