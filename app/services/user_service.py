from fastapi import HTTPException
from app.data.users_db import users_db
from app.schemas.user_schema import UserCreate, UserUpdate, UserPartialUpdate


# Devuelve todos los usuarios, con filtros opcionales
def get_all_users(role=None, is_active=None):
    result = users_db

    if role is not None:
        result = [u for u in result if u["role"] == role.value]

    if is_active is not None:
        result = [u for u in result if u["is_active"] == is_active]

    return result


# Busca un usuario por id y lo devuelve
# si no existe lanza un 404
def get_user_by_id(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="Usuario no encontrado")


# Verifica si un email ya esta registrado en la base de datos
# el parametro exclude_id sirve para ignorar el propio usuario en PUT y PATCH
def check_duplicate_email(email: str, exclude_id: int = None):
    for user in users_db:
        if user["email"] == email and user["id"] != exclude_id:
            raise HTTPException(status_code=400, detail="El correo ya esta registrado")


# Crea un nuevo usuario y lo agrega a la lista
def create_user(data: UserCreate):
    check_duplicate_email(data.email)

    new_id = users_db[-1]["id"] + 1 if users_db else 1

    new_user = {
        "id": new_id,
        "name": data.name,
        "email": data.email,
        "role": data.role.value,
        "is_active": data.is_active,
    }

    users_db.append(new_user)
    return new_user


# Reemplaza completamente un usuario existente
def update_user(user_id: int, data: UserUpdate):
    check_duplicate_email(data.email, exclude_id=user_id)

    for i, user in enumerate(users_db):
        if user["id"] == user_id:
            users_db[i] = {
                "id": user_id,
                "name": data.name,
                "email": data.email,
                "role": data.role.value,
                "is_active": data.is_active,
            }
            return users_db[i]

    raise HTTPException(status_code=404, detail="Usuario no encontrado")


# Actualiza solo los campos que el cliente manda
# si no manda ningun campo lanza un 400
def partial_update_user(user_id: int, data: UserPartialUpdate):
    fields = data.model_dump(exclude_unset=True)

    if not fields:
        raise HTTPException(status_code=400, detail="Debes enviar al menos un campo para actualizar")

    if "email" in fields:
        check_duplicate_email(fields["email"], exclude_id=user_id)

    for i, user in enumerate(users_db):
        if user["id"] == user_id:
            for key, value in fields.items():
                # Convierte el Enum a string antes de guardar
                users_db[i][key] = value.value if hasattr(value, "value") else value
            return users_db[i]

    raise HTTPException(status_code=404, detail="Usuario no encontrado")


# Elimina un usuario existente
# si no existe lanza un 404
def delete_user(user_id: int):
    for i, user in enumerate(users_db):
        if user["id"] == user_id:
            users_db.pop(i)
            return

    raise HTTPException(status_code=404, detail="Usuario no encontrado")
