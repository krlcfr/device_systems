from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserUpdate, UserPartialUpdate


# Devuelve todos los usuarios con filtros opcionales por rol y estado
# order_by ordena por nombre o por fecha de creacion segun lo que mande el cliente
def get_all_users(db: Session, role=None, is_active=None, order_by="name"):
    query = db.query(User)

    if role is not None:
        query = query.filter(User.role == role.value)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    if order_by == "created_at":
        query = query.order_by(User.created_at)
    else:
        query = query.order_by(User.name)

    return query.all()


# Busca un usuario por id y lo devuelve
# si no existe lanza un 404
def get_user_by_id(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


# Busca un usuario por email y lo devuelve
# si no existe retorna None sin lanzar error
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


# Crea un nuevo usuario en la base de datos
# verifica que el email no este registrado antes de insertar
def create_user(db: Session, data: UserCreate):
    existing = get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="El correo ya esta registrado")

    new_user = User(
        name=data.name,
        email=data.email,
        role=data.role.value,
        is_active=data.is_active,
    )

    db.add(new_user)
    db.commit()
    # refresh actualiza el objeto con los datos que asigno la BD, como el id y el created_at
    db.refresh(new_user)
    return new_user


# Reemplaza completamente un usuario existente
def update_user(db: Session, user_id: int, data: UserUpdate):
    user = get_user_by_id(db, user_id)

    existing = get_user_by_email(db, data.email)
    if existing and existing.id != user_id:
        raise HTTPException(status_code=400, detail="El correo ya esta registrado")

    user.name = data.name
    user.email = data.email
    user.role = data.role.value
    user.is_active = data.is_active

    db.commit()
    db.refresh(user)
    return user


# Actualiza solo los campos que el cliente manda
# si no manda ningun campo lanza un 400
def partial_update_user(db: Session, user_id: int, data: UserPartialUpdate):
    user = get_user_by_id(db, user_id)

    fields = data.model_dump(exclude_unset=True)

    if not fields:
        raise HTTPException(status_code=400, detail="Debes enviar al menos un campo para actualizar")

    if "email" in fields:
        existing = get_user_by_email(db, fields["email"])
        if existing and existing.id != user_id:
            raise HTTPException(status_code=400, detail="El correo ya esta registrado")

    for key, value in fields.items():
        # Convierte el Enum a string antes de guardar en la BD
        setattr(user, key, value.value if hasattr(value, "value") else value)

    db.commit()
    db.refresh(user)
    return user


# Elimina un usuario existente de la base de datos
def delete_user(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    db.delete(user)
    db.commit()
