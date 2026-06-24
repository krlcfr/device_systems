from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.connection import Base


# Representa la tabla loans en la base de datos
# cada prestamo conecta un usuario con un dispositivo
class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)

    # Clave foranea hacia el usuario que solicita el prestamo
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Clave foranea hacia el dispositivo prestado
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)

    # Fecha en que se realiza el prestamo
    loan_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Fecha de devolucion, queda vacia hasta que el dispositivo se devuelve
    return_date = Column(DateTime, nullable=True)

    # Estado del prestamo: active, returned u overdue
    status = Column(String(20), nullable=False, default="active")

    # Relacion muchos a uno, cada prestamo pertenece a un usuario
    user = relationship("User", back_populates="loans")

    # Relacion muchos a uno, cada prestamo pertenece a un dispositivo
    device = relationship("Device", back_populates="loans")
