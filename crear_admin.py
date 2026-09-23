from app.database import SessionLocal
from app.auth import hashear_password
from app import models

db = SessionLocal()

username = input("Elegí un usuario: ")
password = input("Elegí una contraseña: ")

existente = db.query(models.Usuario).filter(models.Usuario.username == username).first()
if existente:
    print("Ya existe un usuario con ese nombre.")
else:
    nuevo_usuario = models.Usuario(
        username=username,
        password_hash=hashear_password(password),
    )
    db.add(nuevo_usuario)
    db.commit()
    print(f"Usuario '{username}' creado correctamente.")

db.close()