from app.database.connection import SessionLocal


# Genera una sesion de base de datos para cada request
# el yield entrega la sesion al endpoint y el finally la cierra cuando el request termina
# asi garantizamos que no queden conexiones abiertas sin importar si hubo error o no
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
