from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import models

SECRET_KEY = "cambiar-esto-por-algo-largo-y-random-en-produccion"
ALGORITHM = "HS256"
EXPIRACION_MINUTOS = 60 * 24  # 24 horas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def hashear_password(password: str) -> str:
    return pwd_context.hash(password)


def verificar_password(password_plano: str, password_hash: str) -> bool:
    return pwd_context.verify(password_plano, password_hash)


def crear_token(username: str) -> str:
    expira = datetime.utcnow() + timedelta(minutes=EXPIRACION_MINUTOS)
    payload = {"sub": username, "exp": expira}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def usuario_actual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    excepcion = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la sesión",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise excepcion
    except JWTError:
        raise excepcion

    usuario = db.query(models.Usuario).filter(models.Usuario.username == username).first()
    if usuario is None:
        raise excepcion
    return usuario