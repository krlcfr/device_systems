from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.auth.security import decode_access_token
from app.models.user_model import User

# tokenUrl le dice al Swagger en que endpoint se consigue el token
# para probar las rutas protegidas desde el boton Authorize
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Extrae el usuario desde el token enviado en el header Authorization
# si el token es invalido, expiro, o el usuario ya no existe, responde 401
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    return user


# Verifica ademas que el usuario autenticado este activo
def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user


# Fabrica de dependencias para restringir una ruta a uno o varios roles especificos
# se usa asi: Depends(require_role("admin", "support"))
def require_role(*allowed_roles: str):
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta accion",
            )
        return current_user

    return role_checker


# Atajo para las rutas que solo puede usar un administrador
def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta accion requiere rol de administrador",
        )
    return current_user
