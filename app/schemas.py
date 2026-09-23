from pydantic import BaseModel
from typing import Optional


class EquipoBase(BaseModel):
    nombre: str
    categoria: Optional[str] = None


class EquipoCreate(EquipoBase):
    pass


class Equipo(EquipoBase):
    id: int

    class Config:
        from_attributes = True
        
class JugadorBase(BaseModel):
    nombre: str
    equipo_id: int
    posicion: Optional[str] = None
    dorsal: Optional[int] = None
    altura_cm: Optional[int] = None
    peso_kg: Optional[int] = None
    edad: Optional[int] = None

class JugadorCreate(JugadorBase):
    pass


class Jugador(JugadorBase):
    id: int
    foto_url: Optional[str] = None
    altura_cm: Optional[int] = None
    peso_kg: Optional[int] = None
    edad: Optional[int] = None

    class Config:
        from_attributes = True
        
from datetime import date


class PartidoBase(BaseModel):
    fecha: date
    equipo_local_id: int
    equipo_visitante_id: int
    resultado_local: Optional[int] = None
    resultado_visitante: Optional[int] = None


class PartidoCreate(PartidoBase):
    pass


class Partido(PartidoBase):
    id: int

    class Config:
        from_attributes = True


class EstadisticaBase(BaseModel):
    partido_id: int
    jugador_id: int
    puntos: int = 0
    rebotes: int = 0
    asistencias: int = 0
    robos: int = 0
    perdidas: int = 0
    tiros_intentados: int = 0
    tiros_convertidos: int = 0
    minutos_jugados: Optional[float] = None


class EstadisticaCreate(EstadisticaBase):
    pass


class Estadistica(EstadisticaBase):
    id: int

    class Config:
        from_attributes = True
        
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class UsuarioCreate(BaseModel):
    username: str
    password: str