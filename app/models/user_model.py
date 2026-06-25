from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.connection import Base


# Representa la tabla users en la base de datos
# cada atributo es una columna de la tabla
class User(Base):
    __tablename__ = "users"

    # Clave primaria, se autoincrementa con cada usuario nuevo
    id = Column(Integer, primary_key=True, index=True)

    # Nombre obligatorio, no puede llegar vacio
    name = Column(String(100), nullable=False)

    # Email obligatorio y unico, no pueden existir dos usuarios con el mismo correo
    email = Column(String(255), unique=True, nullable=False, index=True)

    # Hash de la contraseña generado con passlib, nunca se guarda en texto plano
    # server_default vacio evita romper filas existentes creadas antes de esta columna
    hashed_password = Column(String(255), nullable=False, server_default="")

    # Rol obligatorio, la validacion de valores permitidos la maneja Pydantic
    role = Column(String(50), nullable=False)

    # Estado del usuario, llega como True si no se especifica
    is_active = Column(Boolean, default=True, nullable=False)

    # Fecha de creacion, se asigna automaticamente al momento de crear el usuario
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacion uno a muchos, un usuario puede tener muchos prestamos
    loans = relationship("Loan", back_populates="user")
