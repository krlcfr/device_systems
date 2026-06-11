from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./device_systems.db"

# Motor de conexion a la base de datos
# check_same_thread en False porque FastAPI puede usar multiples hilos
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Fabrica de sesiones, cada request recibe la suya propia
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base de la que heredan todos los modelos SQLAlchemy
class Base(DeclarativeBase):
    pass

# Crea todas las tablas definidas en los modelos si no existen todavia
def create_tables():
    Base.metadata.create_all(bind=engine)
