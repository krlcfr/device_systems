from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.connection import Base


# Representa la tabla devices en la base de datos
# cada dispositivo puede tener varios prestamos a lo largo del tiempo
class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)

    # Nombre del dispositivo, obligatorio
    name = Column(String(100), nullable=False)

    # Numero de serie unico, no pueden existir dos dispositivos con el mismo
    serial_number = Column(String(100), unique=True, nullable=False, index=True)

    # Tipo de dispositivo, por ejemplo laptop, tablet, proyector
    device_type = Column(String(50), nullable=False)

    # Marca del dispositivo, no es obligatoria
    brand = Column(String(50), nullable=True)

    # Indica si el dispositivo esta disponible para prestamo
    is_available = Column(Boolean, default=True, nullable=False)

    # Fecha de creacion del registro
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacion uno a muchos, un dispositivo puede aparecer en varios prestamos historicos
    loans = relationship("Loan", back_populates="device")
