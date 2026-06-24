from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.device_model import Device
from app.schemas.device_schema import DeviceCreate, DeviceUpdate, DevicePartialUpdate


# Devuelve todos los dispositivos con filtros opcionales
# search busca de forma flexible en name, serial_number y brand
def get_all_devices(db: Session, device_type=None, is_available=None, brand=None, search=None):
    query = db.query(Device)

    if device_type is not None:
        query = query.filter(Device.device_type == device_type)

    if is_available is not None:
        query = query.filter(Device.is_available == is_available)

    if brand is not None:
        query = query.filter(Device.brand.ilike(f"%{brand}%"))

    if search is not None:
        query = query.filter(
            or_(
                Device.name.ilike(f"%{search}%"),
                Device.serial_number.ilike(f"%{search}%"),
                Device.brand.ilike(f"%{search}%"),
            )
        )

    return query.order_by(Device.name).all()


# Busca un dispositivo por id, si no existe lanza un 404
def get_device_by_id(db: Session, device_id: int):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return device


# Busca un dispositivo por su numero de serie
def get_device_by_serial(db: Session, serial_number: str):
    return db.query(Device).filter(Device.serial_number == serial_number).first()


# Crea un nuevo dispositivo verificando que el numero de serie no este registrado
def create_device(db: Session, data: DeviceCreate):
    existing = get_device_by_serial(db, data.serial_number)
    if existing:
        raise HTTPException(status_code=400, detail="El numero de serie ya esta registrado")

    new_device = Device(
        name=data.name,
        serial_number=data.serial_number,
        device_type=data.device_type,
        brand=data.brand,
        is_available=data.is_available,
    )

    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device


# Reemplaza completamente un dispositivo existente
def update_device(db: Session, device_id: int, data: DeviceUpdate):
    device = get_device_by_id(db, device_id)

    existing = get_device_by_serial(db, data.serial_number)
    if existing and existing.id != device_id:
        raise HTTPException(status_code=400, detail="El numero de serie ya esta registrado")

    device.name = data.name
    device.serial_number = data.serial_number
    device.device_type = data.device_type
    device.brand = data.brand
    device.is_available = data.is_available

    db.commit()
    db.refresh(device)
    return device


# Actualiza solo los campos que el cliente manda
def partial_update_device(db: Session, device_id: int, data: DevicePartialUpdate):
    device = get_device_by_id(db, device_id)

    fields = data.model_dump(exclude_unset=True)

    if not fields:
        raise HTTPException(status_code=400, detail="Debes enviar al menos un campo para actualizar")

    if "serial_number" in fields:
        existing = get_device_by_serial(db, fields["serial_number"])
        if existing and existing.id != device_id:
            raise HTTPException(status_code=400, detail="El numero de serie ya esta registrado")

    for key, value in fields.items():
        setattr(device, key, value)

    db.commit()
    db.refresh(device)
    return device


# Elimina un dispositivo existente
def delete_device(db: Session, device_id: int):
    device = get_device_by_id(db, device_id)
    db.delete(device)
    db.commit()
