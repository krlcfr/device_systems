from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

from app.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

# Contexto de hash, bcrypt es el algoritmo recomendado por la documentacion
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Algoritmo de firma de JWT
ALGORITHM = "HS256"


def get_password_hash(password: str) -> str:
    """Genera un hash seguro de la contraseña proporcionada."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con su hash almacenado."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT con los datos proporcionados y un tiempo de expiracion."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decodifica un token JWT y devuelve su contenido.
    Si el token es invalido o expiro, jwt.decode lanza JWTError.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
