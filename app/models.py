from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float
from sqlalchemy.orm import relationship
from app.database import Base


class Equipo(Base):
    __tablename__ = "equipos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    categoria = Column(String, nullable=True)

    jugadores = relationship("Jugador", back_populates="equipo")


class Jugador(Base):
    __tablename__ = "jugadores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    equipo_id = Column(Integer, ForeignKey("equipos.id"))
    posicion = Column(String, nullable=True)
    dorsal = Column(Integer, nullable=True)
    foto_url = Column(String, nullable=True)
    altura_cm = Column(Integer, nullable=True)
    peso_kg = Column(Integer, nullable=True)
    edad = Column(Integer, nullable=True)

    equipo = relationship("Equipo", back_populates="jugadores")
class Partido(Base):
    __tablename__ = "partidos"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False)
    equipo_local_id = Column(Integer, ForeignKey("equipos.id"))
    equipo_visitante_id = Column(Integer, ForeignKey("equipos.id"))
    resultado_local = Column(Integer, nullable=True)
    resultado_visitante = Column(Integer, nullable=True)


class Estadistica(Base):
    __tablename__ = "estadisticas"

    id = Column(Integer, primary_key=True, index=True)
    partido_id = Column(Integer, ForeignKey("partidos.id"))
    jugador_id = Column(Integer, ForeignKey("jugadores.id"))
    puntos = Column(Integer, default=0)
    rebotes = Column(Integer, default=0)
    asistencias = Column(Integer, default=0)
    robos = Column(Integer, default=0)
    perdidas = Column(Integer, default=0)
    tiros_intentados = Column(Integer, default=0)
    tiros_convertidos = Column(Integer, default=0)
    minutos_jugados = Column(Float, nullable=True)
    
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)