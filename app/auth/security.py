from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os

# Contexto de hash, bcrypt es el algoritmo recomendado por la documentacion
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Clave secreta para firmar los tokens, en produccion debe venir de una variable de entorno real
SECRET_KEY = os.getenv("SECRET_KEY", "device-systems-secret-key-cambiar-en-produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Genera un hash seguro de la contraseña proporcionada
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# Verifica si una contraseña en texto plano coincide con su hash almacenado
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Crea un token JWT con los datos proporcionados y un tiempo de expiracion
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Decodifica un token JWT y devuelve su contenido
# si el token es invalido o expiro, jwt.decode lanza JWTError
def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
