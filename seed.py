import random
from datetime import date, timedelta
from faker import Faker

from app.database import SessionLocal, engine, Base
from app import models

Base.metadata.create_all(bind=engine)

fake = Faker("es_AR")
db = SessionLocal()

POSICIONES = ["base", "escolta", "alero", "ala-pivot", "pivot"]

RANGOS_ALTURA = {
    "base": (175, 190),
    "escolta": (185, 198),
    "alero": (195, 205),
    "ala-pivot": (200, 210),
    "pivot": (205, 218),
}

# 1. Crear equipos
print("Creando equipos...")
equipos = []
for _ in range(15):
    equipo = models.Equipo(
        nombre=fake.unique.city() + " Basket",
        categoria=random.choice(["Primera", "Sub19", "Sub17"]),
    )
    db.add(equipo)
    equipos.append(equipo)
db.commit()
for e in equipos:
    db.refresh(e)

# 2. Crear jugadores (repartidos entre los equipos)
print("Creando jugadores...")
jugadores = []
for _ in range(1000):
    posicion = random.choice(POSICIONES)
    altura_min, altura_max = RANGOS_ALTURA[posicion]
    altura = random.randint(altura_min, altura_max)
    peso = round(altura * 0.42 + random.randint(-6, 10))

    jugador = models.Jugador(
        nombre=fake.name(),
        equipo_id=random.choice(equipos).id,
        posicion=posicion,
        dorsal=random.randint(0, 99),
        altura_cm=altura,
        peso_kg=peso,
        edad=random.randint(17, 34),
    )
    db.add(jugador)
    jugadores.append(jugador)
db.commit()
for j in jugadores:
    db.refresh(j)

# 3. Crear partidos (cada equipo juega contra varios rivales)
print("Creando partidos...")
partidos = []
fecha_inicio = date(2026, 3, 1)
for i in range(200):
    local, visitante = random.sample(equipos, 2)
    partido = models.Partido(
        fecha=fecha_inicio + timedelta(days=i * 2),
        equipo_local_id=local.id,
        equipo_visitante_id=visitante.id,
        resultado_local=random.randint(60, 110),
        resultado_visitante=random.randint(60, 110),
    )
    db.add(partido)
    partidos.append((partido, local.id, visitante.id))
db.commit()

# 4. Crear estadísticas (jugadores de los dos equipos de cada partido)
print("Creando estadísticas...")
jugadores_por_equipo = {}
for j in jugadores:
    jugadores_por_equipo.setdefault(j.equipo_id, []).append(j)

for partido, local_id, visitante_id in partidos:
    db.refresh(partido)
    participantes = (
        jugadores_por_equipo.get(local_id, [])[:8]
        + jugadores_por_equipo.get(visitante_id, [])[:8]
    )
    for jugador in participantes:
        tiros_intentados = random.randint(3, 20)
        tiros_convertidos = random.randint(0, tiros_intentados)
        estadistica = models.Estadistica(
            partido_id=partido.id,
            jugador_id=jugador.id,
            puntos=tiros_convertidos * random.choice([1, 2, 3]),
            rebotes=random.randint(0, 12),
            asistencias=random.randint(0, 10),
            robos=random.randint(0, 5),
            perdidas=random.randint(0, 5),
            tiros_intentados=tiros_intentados,
            tiros_convertidos=tiros_convertidos,
            minutos_jugados=round(random.uniform(5, 35), 1),
        )
        db.add(estadistica)
db.commit()

db.close()
print("Listo: equipos, jugadores, partidos y estadísticas generados.")