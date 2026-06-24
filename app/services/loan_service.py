from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from datetime import datetime

from app.models.loan_model import Loan
from app.models.user_model import User
from app.models.device_model import Device
from app.schemas.loan_schema import LoanCreate


# Devuelve todos los prestamos con filtros opcionales
def get_all_loans(db: Session, status=None, user_id=None, device_id=None):
    query = db.query(Loan)

    if status is not None:
        query = query.filter(Loan.status == status.value)

    if user_id is not None:
        query = query.filter(Loan.user_id == user_id)

    if device_id is not None:
        query = query.filter(Loan.device_id == device_id)

    return query.order_by(Loan.loan_date.desc()).all()


# Busca un prestamo por id, si no existe lanza un 404
def get_loan_by_id(db: Session, loan_id: int):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Prestamo no encontrado")
    return loan


# Crea un nuevo prestamo aplicando todas las reglas de negocio
def create_loan(db: Session, data: LoanCreate):
    # Verifica que el usuario exista
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Verifica que el dispositivo exista
    device = db.query(Device).filter(Device.id == data.device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")

    # Verifica que el dispositivo este disponible
    # 409 porque es un conflicto con el estado actual del recurso, no un error del cliente
    if not device.is_available:
        raise HTTPException(status_code=409, detail="El dispositivo no esta disponible para prestamo")

    new_loan = Loan(
        user_id=data.user_id,
        device_id=data.device_id,
        loan_date=datetime.utcnow(),
        status="active",
    )

    # El dispositivo deja de estar disponible mientras dure el prestamo
    device.is_available = False

    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)
    return new_loan


# Marca un prestamo como devuelto y libera el dispositivo
def return_loan(db: Session, loan_id: int):
    loan = get_loan_by_id(db, loan_id)

    if loan.status == "returned":
        raise HTTPException(status_code=409, detail="Este prestamo ya fue devuelto")

    loan.status = "returned"
    loan.return_date = datetime.utcnow()

    device = db.query(Device).filter(Device.id == loan.device_id).first()
    device.is_available = True

    db.commit()
    db.refresh(loan)
    return loan


# Devuelve prestamos con la informacion completa de usuario y dispositivo usando join
# permite filtrar por estado, email del usuario o tipo de dispositivo
def get_loans_with_details(db: Session, status=None, user_email=None, device_type=None):
    # joinedload precarga las relaciones user y device en la misma consulta
    # esto evita hacer una query adicional por cada prestamo al acceder a loan.user o loan.device
    query = db.query(Loan).options(joinedload(Loan.user), joinedload(Loan.device))

    # join real con User y Device para poder filtrar por sus columnas
    query = query.join(User, Loan.user_id == User.id).join(Device, Loan.device_id == Device.id)

    conditions = []

    if status is not None:
        conditions.append(Loan.status == status.value)

    if user_email is not None:
        conditions.append(User.email.ilike(f"%{user_email}%"))

    if device_type is not None:
        conditions.append(Device.device_type == device_type)

    if conditions:
        query = query.where(and_(*conditions))

    return query.order_by(Loan.loan_date.desc()).all()


# Devuelve todos los prestamos asociados a un usuario especifico, con detalle de dispositivo
def get_loans_by_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return (
        db.query(Loan)
        .options(joinedload(Loan.user), joinedload(Loan.device))
        .filter(Loan.user_id == user_id)
        .order_by(Loan.loan_date.desc())
        .all()
    )


# Devuelve el historial completo de prestamos de un dispositivo especifico
def get_loans_by_device(db: Session, device_id: int):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")

    return (
        db.query(Loan)
        .options(joinedload(Loan.user), joinedload(Loan.device))
        .filter(Loan.device_id == device_id)
        .order_by(Loan.loan_date.desc())
        .all()
    )
