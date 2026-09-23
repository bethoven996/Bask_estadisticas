import os
import shutil
import uuid
import os
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.database import engine, Base, SessionLocal
from app import models, schemas
from app.auth import (
    hashear_password,
    verificar_password,
    crear_token,
    usuario_actual,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Basquet Stats API")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static/fotos_jugadores", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"mensaje": "API de estadísticas de básquet funcionando"}


@app.post("/login", response_model=schemas.TokenResponse)
def login(datos: schemas.LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.username == datos.username).first()
    if not usuario or not verificar_password(datos.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    token = crear_token(usuario.username)
    return {"access_token": token}
@app.post("/usuarios")
def crear_usuario(
    datos: schemas.UsuarioCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(usuario_actual),
):
    existente = db.query(models.Usuario).filter(models.Usuario.username == datos.username).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ese usuario ya existe")

    nuevo_usuario = models.Usuario(
        username=datos.username,
        password_hash=hashear_password(datos.password),
    )
    db.add(nuevo_usuario)
    db.commit()
    return {"mensaje": f"Usuario '{datos.username}' creado correctamente"}

@app.post("/equipos", response_model=schemas.Equipo)
def crear_equipo(
    equipo: schemas.EquipoCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(usuario_actual),
):
    nuevo_equipo = models.Equipo(nombre=equipo.nombre, categoria=equipo.categoria)
    db.add(nuevo_equipo)
    db.commit()
    db.refresh(nuevo_equipo)
    return nuevo_equipo


@app.get("/equipos", response_model=list[schemas.Equipo])
def listar_equipos(db: Session = Depends(get_db)):
    return db.query(models.Equipo).all()


@app.post("/jugadores", response_model=schemas.Jugador)
def crear_jugador(
    jugador: schemas.JugadorCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(usuario_actual),
):
    nuevo_jugador = models.Jugador(**jugador.model_dump())
    db.add(nuevo_jugador)
    db.commit()
    db.refresh(nuevo_jugador)
    return nuevo_jugador


@app.get("/jugadores", response_model=list[schemas.Jugador])
def listar_jugadores(db: Session = Depends(get_db)):
    return db.query(models.Jugador).all()


@app.post("/jugadores/{jugador_id}/foto", response_model=schemas.Jugador)
def subir_foto_jugador(
    jugador_id: int,
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(usuario_actual),
):
    jugador = db.query(models.Jugador).filter(models.Jugador.id == jugador_id).first()
    if not jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")

    extension = foto.filename.split(".")[-1]
    nombre_archivo = f"{uuid.uuid4()}.{extension}"
    ruta = f"static/fotos_jugadores/{nombre_archivo}"

    with open(ruta, "wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)

        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    jugador.foto_url = f"{backend_url}/static/fotos_jugadores/{nombre_archivo}"
    db.commit()
    db.refresh(jugador)
    return jugador


@app.post("/partidos", response_model=schemas.Partido)
def crear_partido(
    partido: schemas.PartidoCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(usuario_actual),
):
    nuevo_partido = models.Partido(**partido.model_dump())
    db.add(nuevo_partido)
    db.commit()
    db.refresh(nuevo_partido)
    return nuevo_partido


@app.get("/partidos", response_model=list[schemas.Partido])
def listar_partidos(db: Session = Depends(get_db)):
    return db.query(models.Partido).all()


@app.post("/estadisticas", response_model=schemas.Estadistica)
def crear_estadistica(
    estadistica: schemas.EstadisticaCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(usuario_actual),
):
    nueva_estadistica = models.Estadistica(**estadistica.model_dump())
    db.add(nueva_estadistica)
    db.commit()
    db.refresh(nueva_estadistica)
    return nueva_estadistica


@app.get("/estadisticas", response_model=list[schemas.Estadistica])
def listar_estadisticas(db: Session = Depends(get_db)):
    return db.query(models.Estadistica).all()