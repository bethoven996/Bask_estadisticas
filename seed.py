import random
from datetime import date, timedelta

import pandas as pd
from sqlalchemy.orm import sessionmaker

from app.database import engine, Base
from app import models

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
db = SessionLocal()

EQUIPOS_NBA = {
    "ATL": "Atlanta Hawks", "BOS": "Boston Celtics", "BKN": "Brooklyn Nets",
    "CHA": "Charlotte Hornets", "CHI": "Chicago Bulls", "CLE": "Cleveland Cavaliers",
    "DAL": "Dallas Mavericks", "DEN": "Denver Nuggets", "DET": "Detroit Pistons",
    "GSW": "Golden State Warriors", "HOU": "Houston Rockets", "IND": "Indiana Pacers",
    "LAC": "LA Clippers", "LAL": "Los Angeles Lakers", "MEM": "Memphis Grizzlies",
    "MIA": "Miami Heat", "MIL": "Milwaukee Bucks", "MIN": "Minnesota Timberwolves",
    "NOP": "New Orleans Pelicans", "NYK": "New York Knicks", "OKC": "Oklahoma City Thunder",
    "ORL": "Orlando Magic", "PHI": "Philadelphia 76ers", "PHX": "Phoenix Suns",
    "POR": "Portland Trail Blazers", "SAC": "Sacramento Kings", "SAS": "San Antonio Spurs",
    "TOR": "Toronto Raptors", "UTA": "Utah Jazz", "WAS": "Washington Wizards",
}

# 1. Limpieza (por si el script ya se corrió antes)
print("Limpiando datos existentes...")
db.query(models.Estadistica).delete()
db.query(models.Partido).delete()
db.query(models.Jugador).delete()
db.query(models.Equipo).delete()
db.commit()

# 2. Leer el dataset
print("Leyendo dataset...")
df = pd.read_csv("all_seasons.csv")
df = df.dropna(subset=["player_height", "player_weight", "age", "pts", "reb", "ast"])
df = df[df["team_abbreviation"].isin(EQUIPOS_NBA.keys())]

# 3. Calcular promedios de CARRERA, ponderados por partidos jugados en cada temporada
print("Calculando promedios de carrera...")
df["pts_total"] = df["pts"] * df["gp"]
df["reb_total"] = df["reb"] * df["gp"]
df["ast_total"] = df["ast"] * df["gp"]

carrera = df.groupby("player_name").agg(
    gp_total=("gp", "sum"),
    pts_total=("pts_total", "sum"),
    reb_total=("reb_total", "sum"),
    ast_total=("ast_total", "sum"),
).reset_index()

# Solo jugadores con una muestra de carrera sólida (al menos 100 partidos en total)
carrera = carrera[carrera["gp_total"] >= 100]

carrera["pts"] = carrera["pts_total"] / carrera["gp_total"]
carrera["reb"] = carrera["reb_total"] / carrera["gp_total"]
carrera["ast"] = carrera["ast_total"] / carrera["gp_total"]

# Datos de perfil (equipo, altura, peso, edad): tomamos su temporada con más partidos jugados
idx_temporada_principal = df.loc[df.groupby("player_name")["gp"].idxmax()]
perfil = idx_temporada_principal[["player_name", "team_abbreviation", "age", "player_height", "player_weight"]]

jugadores_df = carrera.merge(perfil, on="player_name")

# Repartir hasta ~34 jugadores por equipo, tope de 1000 en total
jugadores_df["_orden"] = jugadores_df.groupby("team_abbreviation").cumcount()
jugadores_df = jugadores_df[jugadores_df["_orden"] < 34]
jugadores_df = jugadores_df.head(1000)

def asignar_posicion(row):
    if row["ast"] >= 5:
        return "base"
    if row["reb"] >= 9:
        return "pivot"
    if row["reb"] >= 6.5:
        return "ala-pivot"
    if row["ast"] >= 3:
        return "escolta"
    return "alero"

# 4. Crear equipos
print("Creando equipos...")
equipos_creados = {}
for sigla, nombre in EQUIPOS_NBA.items():
    equipo = models.Equipo(nombre=nombre, categoria="NBA")
    db.add(equipo)
    equipos_creados[sigla] = equipo
db.commit()

# 5. Crear jugadores, con promedios de carrera
print(f"Creando {len(jugadores_df)} jugadores reales (promedios de carrera)...")
jugadores_creados = []
for _, row in jugadores_df.iterrows():
    equipo = equipos_creados.get(row["team_abbreviation"])
    if not equipo:
        continue
    jugador = models.Jugador(
        nombre=row["player_name"],
        equipo_id=equipo.id,
        posicion=asignar_posicion(row),
        dorsal=random.randint(0, 99),
        altura_cm=round(row["player_height"]),
        peso_kg=round(row["player_weight"]),
        edad=int(row["age"]),
    )
    db.add(jugador)
    jugadores_creados.append((jugador, row))
db.commit()

# 6. Crear un partido por equipo, para colgar ahí el promedio de carrera de cada jugador
print("Creando partidos...")
partidos_por_equipo = {}
fecha_inicio = date(2026, 3, 1)
equipos_lista = list(equipos_creados.values())
for i, equipo in enumerate(equipos_lista):
    rival = equipos_lista[(i + 1) % len(equipos_lista)]
    partido = models.Partido(
        fecha=fecha_inicio + timedelta(days=i),
        equipo_local_id=equipo.id,
        equipo_visitante_id=rival.id,
        resultado_local=random.randint(90, 120),
        resultado_visitante=random.randint(90, 120),
    )
    db.add(partido)
    partidos_por_equipo[equipo.id] = partido
db.commit()

# 7. Crear estadísticas: el promedio de carrera de cada jugador
print("Creando estadísticas...")
for jugador, row in jugadores_creados:
    partido = partidos_por_equipo.get(jugador.equipo_id)
    if not partido:
        continue
    puntos = row["pts"]
    tiros_intentados = max(round(puntos / 0.45), 1)
    tiros_convertidos = round(tiros_intentados * 0.45)
    estadistica = models.Estadistica(
        partido_id=partido.id,
        jugador_id=jugador.id,
        puntos=round(puntos, 1),
        rebotes=round(row["reb"], 1),
        asistencias=round(row["ast"], 1),
        robos=round(random.uniform(0.5, 1.5), 1),
        perdidas=round(random.uniform(1, 3), 1),
        tiros_intentados=tiros_intentados,
        tiros_convertidos=tiros_convertidos,
        minutos_jugados=round(random.uniform(20, 36), 1),
    )
    db.add(estadistica)
db.commit()

db.close()
print(f"Listo: {len(equipos_creados)} equipos NBA reales y {len(jugadores_creados)} jugadores con promedios de carrera.")