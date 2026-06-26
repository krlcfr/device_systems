"""
Configuracion compartida de la aplicacion.
Centraliza el limiter de slowapi, logging y variables de entorno.
"""

import logging
import os
from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address

load_dotenv()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("device_systems")

# ---------------------------------------------------------------------------
# Variables de entorno
# ---------------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "device-systems-secret-key-cambiar-en-produccion")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./device_systems.db")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# ---------------------------------------------------------------------------
# Rate Limiter global (slowapi)
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address)
